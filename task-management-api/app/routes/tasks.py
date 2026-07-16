from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from sqlalchemy.orm import joinedload

from app import db, cache
from app.models.task import Task
from app.models.project import Project, TeamMember
from app.models.notification import Notification
from app.schemas.task import TaskSchema, TaskCreateSchema, TaskUpdateSchema
from app.tasks.celery_tasks import send_task_assignment_email, generate_user_report

tasks_bp = Blueprint('tasks', __name__)
task_schema = TaskSchema()
tasks_schema = TaskSchema(many=True)
task_create_schema = TaskCreateSchema()
task_update_schema = TaskUpdateSchema()


@tasks_bp.route('', methods=['GET'])
@jwt_required()
@cache.cached(timeout=60, query_string=True)
def get_tasks():
    """
    Get all tasks for current user
    ---
    tags:
      - Tasks
    security:
      - Bearer: []
    parameters:
      - in: query
        name: status
        type: string
        enum: [pending, in_progress, completed]
      - in: query
        name: priority
        type: string
        enum: [low, medium, high]
      - in: query
        name: project_id
        type: integer
        description: Filter by project
      - in: query
        name: assigned_to_me
        type: boolean
        description: Show tasks assigned to current user
    responses:
      200:
        description: List of tasks
      401:
        description: Unauthorized
    """
    current_user_id = int(get_jwt_identity())
    
    # Get tasks owned by user or assigned to user with eager loading for performance
    query = Task.query.options(
        joinedload(Task.assignee)
    ).filter(
        db.or_(
            Task.user_id == current_user_id,
            Task.assigned_to_id == current_user_id
        )
    )
    
    status = request.args.get('status')
    priority = request.args.get('priority')
    project_id = request.args.get('project_id', type=int)
    assigned_to_me = request.args.get('assigned_to_me', 'false').lower() == 'true'
    
    if status:
        query = query.filter_by(status=status)
    if priority:
        query = query.filter_by(priority=priority)
    if project_id:
        query = query.filter_by(project_id=project_id)
    if assigned_to_me:
        query = query.filter_by(assigned_to_id=current_user_id)
    
    tasks = query.order_by(Task.created_at.desc()).all()
    return jsonify(tasks_schema.dump(tasks)), 200


@tasks_bp.route('/<int:task_id>', methods=['GET'])
@jwt_required()
@cache.cached(timeout=300, key_prefix=lambda: f'task_{task_id}_{get_jwt_identity()}')
def get_task(task_id):
    """
    Get a specific task
    ---
    tags:
      - Tasks
    security:
      - Bearer: []
    parameters:
      - in: path
        name: task_id
        type: integer
        required: true
    responses:
      200:
        description: Task details
      404:
        description: Task not found
    """
    current_user_id = int(get_jwt_identity())
    # Eager load relationships for better performance
    task = Task.query.options(
        joinedload(Task.assignee)
    ).filter_by(id=task_id, user_id=current_user_id).first_or_404()
    return jsonify(task_schema.dump(task)), 200


@tasks_bp.route('', methods=['POST'])
@jwt_required()
def create_task():
    """
    Create a new task
    ---
    tags:
      - Tasks
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - title
          properties:
            title:
              type: string
              example: Complete project
            description:
              type: string
              example: Finish the API implementation
            status:
              type: string
              enum: [pending, in_progress, completed]
            priority:
              type: string
              enum: [low, medium, high]
            due_date:
              type: string
              format: date-time
    responses:
      201:
        description: Task created
      400:
        description: Validation error
    """
    current_user_id = int(get_jwt_identity())
    
    try:
        data = task_create_schema.load(request.json)
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400
    
    # Validate project access if project_id provided
    if data.get('project_id'):
        project = Project.query.get(data['project_id'])
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        member = TeamMember.query.filter_by(
            project_id=data['project_id'], 
            user_id=current_user_id
        ).first()
        if not member and project.owner_id != current_user_id:
            return jsonify({'error': 'Access denied to project'}), 403
    
    task = Task(user_id=current_user_id, **data)
    db.session.add(task)
    db.session.commit()
    
    # Clear cache for user's tasks
    cache.delete_memoized(get_tasks)
    
    # Notify assignee if task is assigned (background task)
    if task.assigned_to_id and task.assigned_to_id != current_user_id:
        notification = Notification(
            user_id=task.assigned_to_id,
            type='task_assigned',
            title='Task Assigned',
            message=f'You have been assigned to task "{task.title}"',
            task_id=task.id,
            project_id=task.project_id
        )
        db.session.add(notification)
        db.session.commit()
        
        # Send email notification asynchronously
        send_task_assignment_email.delay(task.id, task.assigned_to_id)
    
    return jsonify(task_schema.dump(task)), 201


@tasks_bp.route('/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    """
    Update a task
    ---
    tags:
      - Tasks
    security:
      - Bearer: []
    parameters:
      - in: path
        name: task_id
        type: integer
        required: true
      - in: body
        name: body
        schema:
          type: object
          properties:
            title:
              type: string
            description:
              type: string
            status:
              type: string
              enum: [pending, in_progress, completed]
            priority:
              type: string
              enum: [low, medium, high]
            due_date:
              type: string
              format: date-time
    responses:
      200:
        description: Task updated
      404:
        description: Task not found
    """
    current_user_id = int(get_jwt_identity())
    
    # Allow task owner or assignee to update
    task = Task.query.filter(
        Task.id == task_id,
        db.or_(
            Task.user_id == current_user_id,
            Task.assigned_to_id == current_user_id
        )
    ).first_or_404()
    
    try:
        data = task_update_schema.load(request.json)
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400
    
    old_assigned_to = task.assigned_to_id
    
    for key, value in data.items():
        setattr(task, key, value)
    
    db.session.commit()
    
    # Clear cache for this task and user's tasks
    cache.delete(f'task_{task_id}_{current_user_id}')
    cache.delete_memoized(get_tasks)
    
    # Notify new assignee if assignment changed
    if data.get('assigned_to_id') and data['assigned_to_id'] != old_assigned_to and data['assigned_to_id'] != current_user_id:
        notification = Notification(
            user_id=data['assigned_to_id'],
            type='task_assigned',
            title='Task Assigned',
            message=f'You have been assigned to task "{task.title}"',
            task_id=task.id,
            project_id=task.project_id
        )
        db.session.add(notification)
        db.session.commit()
        
        # Send email notification asynchronously
        send_task_assignment_email.delay(task.id, data['assigned_to_id'])
    
    return jsonify(task_schema.dump(task)), 200


@tasks_bp.route('/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    """
    Delete a task
    ---
    tags:
      - Tasks
    security:
      - Bearer: []
    parameters:
      - in: path
        name: task_id
        type: integer
        required: true
    responses:
      200:
        description: Task deleted
      404:
        description: Task not found
    """
    current_user_id = int(get_jwt_identity())
    task = Task.query.filter_by(id=task_id, user_id=current_user_id).first_or_404()
    
    db.session.delete(task)
    db.session.commit()
    
    # Clear cache
    cache.delete(f'task_{task_id}_{current_user_id}')
    cache.delete_memoized(get_tasks)
    
    return jsonify({'message': 'Task deleted successfully'}), 200


@tasks_bp.route('/reports/generate', methods=['POST'])
@jwt_required()
def request_report():
    """
    Generate user task report asynchronously
    ---
    tags:
      - Tasks
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        schema:
          type: object
          properties:
            report_type:
              type: string
              enum: [summary, detailed, analytics]
              default: summary
    responses:
      202:
        description: Report generation started
      400:
        description: Invalid request
    """
    current_user_id = int(get_jwt_identity())
    data = request.json or {}
    report_type = data.get('report_type', 'summary')
    
    if report_type not in ['summary', 'detailed', 'analytics']:
        return jsonify({'error': 'Invalid report type'}), 400
    
    # Start background task
    task = generate_user_report.delay(current_user_id, report_type)
    
    return jsonify({
        'message': 'Report generation started',
        'task_id': task.id,
        'status_url': f'/api/tasks/reports/status/{task.id}'
    }), 202


@tasks_bp.route('/reports/status/<task_id>', methods=['GET'])
@jwt_required()
def get_report_status(task_id):
    """
    Check status of report generation task
    ---
    tags:
      - Tasks
    security:
      - Bearer: []
    parameters:
      - in: path
        name: task_id
        type: string
        required: true
    responses:
      200:
        description: Task status
    """
    from celery.result import AsyncResult
    
    task = AsyncResult(task_id)
    
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'status': 'Task is waiting to be executed'
        }
    elif task.state == 'STARTED':
        response = {
            'state': task.state,
            'status': 'Task is currently running'
        }
    elif task.state == 'SUCCESS':
        response = {
            'state': task.state,
            'status': 'Task completed successfully',
            'result': task.result
        }
    elif task.state == 'FAILURE':
        response = {
            'state': task.state,
            'status': 'Task failed',
            'error': str(task.info)
        }
    else:
        response = {
            'state': task.state,
            'status': str(task.info)
        }
    
    return jsonify(response), 200

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from app import db
from app.models.project import Project, TeamMember
from app.models.notification import Notification
from app.models.user import User
from app.schemas.project import (
    ProjectSchema, ProjectCreateSchema, ProjectUpdateSchema,
    TeamMemberSchema, TeamMemberCreateSchema, TeamMemberUpdateSchema
)

projects_bp = Blueprint('projects', __name__)
project_schema = ProjectSchema()
projects_schema = ProjectSchema(many=True)
project_create_schema = ProjectCreateSchema()
project_update_schema = ProjectUpdateSchema()
team_member_schema = TeamMemberSchema()
team_members_schema = TeamMemberSchema(many=True)
team_member_create_schema = TeamMemberCreateSchema()
team_member_update_schema = TeamMemberUpdateSchema()


def is_project_member(project_id, user_id):
    """Check if user is a member of the project."""
    return TeamMember.query.filter_by(project_id=project_id, user_id=user_id).first() is not None


def is_project_admin(project_id, user_id):
    """Check if user is admin or owner of the project."""
    member = TeamMember.query.filter_by(project_id=project_id, user_id=user_id).first()
    return member and member.role in ['owner', 'admin']


@projects_bp.route('', methods=['GET'])
@jwt_required()
def get_projects():
    """
    Get all projects for current user
    ---
    tags:
      - Projects
    security:
      - Bearer: []
    parameters:
      - in: query
        name: status
        type: string
        enum: [active, archived, completed]
    responses:
      200:
        description: List of projects
    """
    current_user_id = int(get_jwt_identity())
    
    # Get projects where user is owner or member
    member_project_ids = db.session.query(TeamMember.project_id).filter_by(user_id=current_user_id)
    query = Project.query.filter(
        db.or_(
            Project.owner_id == current_user_id,
            Project.id.in_(member_project_ids)
        )
    )
    
    status = request.args.get('status')
    if status:
        query = query.filter_by(status=status)
    
    projects = query.order_by(Project.created_at.desc()).all()
    return jsonify(projects_schema.dump(projects)), 200


@projects_bp.route('/<int:project_id>', methods=['GET'])
@jwt_required()
def get_project(project_id):
    """
    Get a specific project
    ---
    tags:
      - Projects
    security:
      - Bearer: []
    parameters:
      - in: path
        name: project_id
        type: integer
        required: true
    responses:
      200:
        description: Project details
      403:
        description: Access denied
      404:
        description: Project not found
    """
    current_user_id = int(get_jwt_identity())
    project = Project.query.get_or_404(project_id)
    
    if project.owner_id != current_user_id and not is_project_member(project_id, current_user_id):
        return jsonify({'error': 'Access denied'}), 403
    
    return jsonify(project_schema.dump(project)), 200


@projects_bp.route('', methods=['POST'])
@jwt_required()
def create_project():
    """
    Create a new project
    ---
    tags:
      - Projects
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - name
          properties:
            name:
              type: string
              example: My Project
            description:
              type: string
            status:
              type: string
              enum: [active, archived, completed]
    responses:
      201:
        description: Project created
      400:
        description: Validation error
    """
    current_user_id = int(get_jwt_identity())
    
    try:
        data = project_create_schema.load(request.json)
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400
    
    project = Project(owner_id=current_user_id, **data)
    db.session.add(project)
    db.session.flush()
    
    # Add owner as team member with 'owner' role
    owner_member = TeamMember(user_id=current_user_id, project_id=project.id, role='owner')
    db.session.add(owner_member)
    db.session.commit()
    
    return jsonify(project_schema.dump(project)), 201


@projects_bp.route('/<int:project_id>', methods=['PUT'])
@jwt_required()
def update_project(project_id):
    """
    Update a project
    ---
    tags:
      - Projects
    security:
      - Bearer: []
    parameters:
      - in: path
        name: project_id
        type: integer
        required: true
      - in: body
        name: body
        schema:
          type: object
          properties:
            name:
              type: string
            description:
              type: string
            status:
              type: string
              enum: [active, archived, completed]
    responses:
      200:
        description: Project updated
      403:
        description: Access denied
      404:
        description: Project not found
    """
    current_user_id = int(get_jwt_identity())
    project = Project.query.get_or_404(project_id)
    
    if not is_project_admin(project_id, current_user_id):
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        data = project_update_schema.load(request.json)
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400
    
    for key, value in data.items():
        setattr(project, key, value)
    
    db.session.commit()
    return jsonify(project_schema.dump(project)), 200


@projects_bp.route('/<int:project_id>', methods=['DELETE'])
@jwt_required()
def delete_project(project_id):
    """
    Delete a project
    ---
    tags:
      - Projects
    security:
      - Bearer: []
    parameters:
      - in: path
        name: project_id
        type: integer
        required: true
    responses:
      200:
        description: Project deleted
      403:
        description: Only owner can delete
      404:
        description: Project not found
    """
    current_user_id = int(get_jwt_identity())
    project = Project.query.get_or_404(project_id)
    
    if project.owner_id != current_user_id:
        return jsonify({'error': 'Only project owner can delete'}), 403
    
    db.session.delete(project)
    db.session.commit()
    
    return jsonify({'message': 'Project deleted successfully'}), 200


# Team Member Routes

@projects_bp.route('/<int:project_id>/members', methods=['GET'])
@jwt_required()
def get_team_members(project_id):
    """
    Get all team members of a project
    ---
    tags:
      - Team
    security:
      - Bearer: []
    parameters:
      - in: path
        name: project_id
        type: integer
        required: true
    responses:
      200:
        description: List of team members
      403:
        description: Access denied
    """
    current_user_id = int(get_jwt_identity())
    project = Project.query.get_or_404(project_id)
    
    if project.owner_id != current_user_id and not is_project_member(project_id, current_user_id):
        return jsonify({'error': 'Access denied'}), 403
    
    members = TeamMember.query.filter_by(project_id=project_id).all()
    return jsonify(team_members_schema.dump(members)), 200


@projects_bp.route('/<int:project_id>/members', methods=['POST'])
@jwt_required()
def add_team_member(project_id):
    """
    Add a team member to project
    ---
    tags:
      - Team
    security:
      - Bearer: []
    parameters:
      - in: path
        name: project_id
        type: integer
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - user_id
          properties:
            user_id:
              type: integer
            role:
              type: string
              enum: [admin, member, viewer]
    responses:
      201:
        description: Member added
      400:
        description: User already a member
      403:
        description: Admin access required
    """
    current_user_id = int(get_jwt_identity())
    project = Project.query.get_or_404(project_id)
    
    if not is_project_admin(project_id, current_user_id):
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        data = team_member_create_schema.load(request.json)
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400
    
    # Check if user exists
    user = User.query.get(data['user_id'])
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Check if already a member
    if is_project_member(project_id, data['user_id']):
        return jsonify({'error': 'User is already a team member'}), 400
    
    member = TeamMember(project_id=project_id, **data)
    db.session.add(member)
    
    # Create notification for invited user
    notification = Notification(
        user_id=data['user_id'],
        type='project_invite',
        title='Project Invitation',
        message=f'You have been added to project "{project.name}"',
        project_id=project_id
    )
    db.session.add(notification)
    db.session.commit()
    
    return jsonify(team_member_schema.dump(member)), 201


@projects_bp.route('/<int:project_id>/members/<int:member_id>', methods=['PUT'])
@jwt_required()
def update_team_member(project_id, member_id):
    """
    Update team member role
    ---
    tags:
      - Team
    security:
      - Bearer: []
    parameters:
      - in: path
        name: project_id
        type: integer
        required: true
      - in: path
        name: member_id
        type: integer
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - role
          properties:
            role:
              type: string
              enum: [admin, member, viewer]
    responses:
      200:
        description: Member role updated
      403:
        description: Admin access required
    """
    current_user_id = int(get_jwt_identity())
    Project.query.get_or_404(project_id)
    
    if not is_project_admin(project_id, current_user_id):
        return jsonify({'error': 'Admin access required'}), 403
    
    member = TeamMember.query.filter_by(id=member_id, project_id=project_id).first_or_404()
    
    # Cannot change owner role
    if member.role == 'owner':
        return jsonify({'error': 'Cannot change owner role'}), 400
    
    try:
        data = team_member_update_schema.load(request.json)
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400
    
    member.role = data['role']
    db.session.commit()
    
    return jsonify(team_member_schema.dump(member)), 200


@projects_bp.route('/<int:project_id>/members/<int:member_id>', methods=['DELETE'])
@jwt_required()
def remove_team_member(project_id, member_id):
    """
    Remove a team member from project
    ---
    tags:
      - Team
    security:
      - Bearer: []
    parameters:
      - in: path
        name: project_id
        type: integer
        required: true
      - in: path
        name: member_id
        type: integer
        required: true
    responses:
      200:
        description: Member removed
      403:
        description: Admin access required
    """
    current_user_id = int(get_jwt_identity())
    Project.query.get_or_404(project_id)
    
    if not is_project_admin(project_id, current_user_id):
        return jsonify({'error': 'Admin access required'}), 403
    
    member = TeamMember.query.filter_by(id=member_id, project_id=project_id).first_or_404()
    
    # Cannot remove owner
    if member.role == 'owner':
        return jsonify({'error': 'Cannot remove project owner'}), 400
    
    db.session.delete(member)
    db.session.commit()
    
    return jsonify({'message': 'Team member removed'}), 200

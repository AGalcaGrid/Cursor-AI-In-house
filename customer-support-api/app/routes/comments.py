from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError

from app import db
from app.models.ticket import Ticket
from app.models.comment import Comment
from app.schemas.comment import CommentSchema, CommentCreateSchema
from app.utils.errors import NotFoundError, ForbiddenError, ValidationException
from app.utils.security import get_current_user

comments_bp = Blueprint('comments', __name__)
comment_schema = CommentSchema()
comments_schema = CommentSchema(many=True)
comment_create_schema = CommentCreateSchema()


def get_ticket_with_access(ticket_id, user):
    """Get ticket with access check."""
    ticket = Ticket.query.get(ticket_id)
    if not ticket:
        raise NotFoundError('Ticket not found')
    
    if user.role == 'customer' and ticket.customer_id != user.id:
        raise ForbiddenError('Access denied')
    
    return ticket


@comments_bp.route('/tickets/<int:ticket_id>/comments', methods=['GET'])
@jwt_required()
def get_comments(ticket_id):
    """
    Get all comments for a ticket
    ---
    tags:
      - Comments
    security:
      - Bearer: []
    parameters:
      - in: path
        name: ticket_id
        type: integer
        required: true
    responses:
      200:
        description: List of comments
      404:
        description: Ticket not found
    """
    user = get_current_user()
    ticket = get_ticket_with_access(ticket_id, user)
    
    query = Comment.query.filter_by(ticket_id=ticket_id)
    
    # Customers cannot see internal comments
    if user.role == 'customer':
        query = query.filter_by(is_internal=False)
    
    comments = query.order_by(Comment.created_at.asc()).all()
    
    return jsonify({
        'status': 'success',
        'data': comments_schema.dump(comments)
    }), 200


@comments_bp.route('/tickets/<int:ticket_id>/comments', methods=['POST'])
@jwt_required()
def create_comment(ticket_id):
    """
    Add a comment to a ticket
    ---
    tags:
      - Comments
    security:
      - Bearer: []
    parameters:
      - in: path
        name: ticket_id
        type: integer
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - content
          properties:
            content:
              type: string
              example: Thank you for your response...
            is_internal:
              type: boolean
              default: false
              description: Internal notes (agents/admins only)
    responses:
      201:
        description: Comment created
      404:
        description: Ticket not found
    """
    user = get_current_user()
    ticket = get_ticket_with_access(ticket_id, user)
    
    try:
        data = comment_create_schema.load(request.json)
    except ValidationError as err:
        raise ValidationException('Validation failed', errors=err.messages)
    
    # Customers cannot create internal comments
    if user.role == 'customer' and data.get('is_internal', False):
        raise ForbiddenError('Customers cannot create internal notes')
    
    comment = Comment(
        ticket_id=ticket_id,
        author_id=user.id,
        content=data['content'],
        is_internal=data.get('is_internal', False),
        is_from_customer=(user.role == 'customer')
    )
    
    db.session.add(comment)
    
    # Track first response time
    if user.role in ['agent', 'admin'] and not ticket.first_response_at:
        ticket.first_response_at = datetime.utcnow()
    
    # If customer replies to waiting ticket, move to in_progress
    if user.role == 'customer' and ticket.status == 'waiting':
        ticket.update_status('in_progress', user.id)
    
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': 'Comment added successfully',
        'data': comment_schema.dump(comment)
    }), 201


@comments_bp.route('/tickets/<int:ticket_id>/comments/<int:comment_id>', methods=['PUT'])
@jwt_required()
def update_comment(ticket_id, comment_id):
    """
    Update a comment
    ---
    tags:
      - Comments
    security:
      - Bearer: []
    parameters:
      - in: path
        name: ticket_id
        type: integer
        required: true
      - in: path
        name: comment_id
        type: integer
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            content:
              type: string
    responses:
      200:
        description: Comment updated
      404:
        description: Comment not found
    """
    user = get_current_user()
    ticket = get_ticket_with_access(ticket_id, user)
    
    comment = Comment.query.filter_by(id=comment_id, ticket_id=ticket_id).first()
    if not comment:
        raise NotFoundError('Comment not found')
    
    # Only author or admin can edit
    if comment.author_id != user.id and user.role != 'admin':
        raise ForbiddenError('Cannot edit this comment')
    
    try:
        data = comment_create_schema.load(request.json, partial=True)
    except ValidationError as err:
        raise ValidationException('Validation failed', errors=err.messages)
    
    if 'content' in data:
        comment.content = data['content']
    
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': 'Comment updated successfully',
        'data': comment_schema.dump(comment)
    }), 200


@comments_bp.route('/tickets/<int:ticket_id>/comments/<int:comment_id>', methods=['DELETE'])
@jwt_required()
def delete_comment(ticket_id, comment_id):
    """
    Delete a comment
    ---
    tags:
      - Comments
    security:
      - Bearer: []
    parameters:
      - in: path
        name: ticket_id
        type: integer
        required: true
      - in: path
        name: comment_id
        type: integer
        required: true
    responses:
      200:
        description: Comment deleted
      404:
        description: Comment not found
    """
    user = get_current_user()
    ticket = get_ticket_with_access(ticket_id, user)
    
    comment = Comment.query.filter_by(id=comment_id, ticket_id=ticket_id).first()
    if not comment:
        raise NotFoundError('Comment not found')
    
    # Only author or admin can delete
    if comment.author_id != user.id and user.role != 'admin':
        raise ForbiddenError('Cannot delete this comment')
    
    db.session.delete(comment)
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': 'Comment deleted successfully'
    }), 200

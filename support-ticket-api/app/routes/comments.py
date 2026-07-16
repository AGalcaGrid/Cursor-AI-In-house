from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from app import db
from app.models.ticket import Ticket
from app.models.comment import Comment
from app.models.user import User
from app.schemas.comment import CommentSchema, CommentCreateSchema
from app.utils.errors import NotFoundError, ForbiddenError, ValidationError as APIValidationError
from app.services.email_service import EmailService
import re

comments_bp = Blueprint('comments', __name__)
comment_schema = CommentSchema()
comments_schema = CommentSchema(many=True)
comment_create_schema = CommentCreateSchema()


def get_current_user():
    """Get current authenticated user."""
    user_id = get_jwt_identity()
    return User.query.get(int(user_id))


@comments_bp.route('/<int:ticket_id>/comments', methods=['GET'])
@jwt_required()
def get_comments(ticket_id):
    """
    Get comments for a ticket (FR-015, FR-016)
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
      403:
        description: Access denied
      404:
        description: Ticket not found
    """
    user = get_current_user()
    ticket = Ticket.query.get(ticket_id)
    
    if not ticket:
        raise NotFoundError('Ticket not found')
    
    if not user.can_view_ticket(ticket):
        raise ForbiddenError('Access denied to this ticket')
    
    # Filter internal comments for customers (FR-016)
    if user.is_customer():
        comments = Comment.query.filter_by(
            ticket_id=ticket_id, 
            is_internal=False
        ).order_by(Comment.created_at.asc()).all()
    else:
        comments = Comment.query.filter_by(
            ticket_id=ticket_id
        ).order_by(Comment.created_at.asc()).all()
    
    return jsonify({
        'status': 'success',
        'comments': comments_schema.dump(comments)
    }), 200


@comments_bp.route('/<int:ticket_id>/comments', methods=['POST'])
@jwt_required()
def create_comment(ticket_id):
    """
    Add comment to ticket (FR-015, FR-016)
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
              example: Thank you for your response. I have tried the solution...
            is_internal:
              type: boolean
              default: false
              description: Internal comments visible only to agents/admins
    responses:
      201:
        description: Comment created
      400:
        description: Validation error
      403:
        description: Access denied
      404:
        description: Ticket not found
    """
    user = get_current_user()
    ticket = Ticket.query.get(ticket_id)
    
    if not ticket:
        raise NotFoundError('Ticket not found')
    
    if not user.can_view_ticket(ticket):
        raise ForbiddenError('Access denied to this ticket')
    
    try:
        data = comment_create_schema.load(request.json)
    except ValidationError as err:
        raise APIValidationError('Validation failed', errors=err.messages)
    
    # Customers cannot create internal comments (FR-016)
    if user.is_customer() and data.get('is_internal', False):
        raise ForbiddenError('Customers cannot create internal comments')
    
    comment = Comment(
        ticket_id=ticket_id,
        user_id=user.id,
        content=data['content'],
        is_internal=data.get('is_internal', False)
    )
    
    db.session.add(comment)
    
    # Mark first response for SLA tracking
    if not ticket.first_response_at and (user.is_agent() or user.is_admin()):
        ticket.first_response_at = comment.created_at
    
    db.session.commit()
    
    # Send email notifications (FR-018)
    if not comment.is_internal:
        recipients = []
        # Notify customer if agent/admin commented
        if user.is_agent() or user.is_admin():
            recipients.append(ticket.customer_email)
        # Notify assigned agent if customer commented
        elif ticket.assigned_agent and ticket.assigned_agent.email != user.email:
            recipients.append(ticket.assigned_agent.email)
        
        if recipients:
            EmailService.notify_new_comment(ticket, comment, user, recipients)
    
    # Handle @mentions (FR-017)
    mentions = re.findall(r'@(\w+(?:\.\w+)?@[\w.-]+\.\w+)', comment.content)
    for email in mentions:
        mentioned_user = User.query.filter_by(email=email).first()
        if mentioned_user and mentioned_user.id != user.id:
            EmailService.notify_mention(ticket, comment, user, mentioned_user)
    
    return jsonify({
        'status': 'success',
        'message': 'Comment added successfully',
        'comment': comment_schema.dump(comment)
    }), 201


@comments_bp.route('/<int:ticket_id>/comments/<int:comment_id>', methods=['DELETE'])
@jwt_required()
def delete_comment(ticket_id, comment_id):
    """
    Delete a comment (admin only)
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
      403:
        description: Admin access required
      404:
        description: Comment not found
    """
    user = get_current_user()
    
    if not user.is_admin():
        raise ForbiddenError('Admin access required')
    
    comment = Comment.query.filter_by(id=comment_id, ticket_id=ticket_id).first()
    if not comment:
        raise NotFoundError('Comment not found')
    
    db.session.delete(comment)
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': 'Comment deleted successfully'
    }), 200

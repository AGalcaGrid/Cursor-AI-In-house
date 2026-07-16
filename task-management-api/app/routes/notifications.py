from flask import Blueprint, request, jsonify, Response
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
import json
import time

from app import db
from app.models.notification import Notification
from app.schemas.notification import NotificationSchema, NotificationUpdateSchema

notifications_bp = Blueprint('notifications', __name__)
notification_schema = NotificationSchema()
notifications_schema = NotificationSchema(many=True)
notification_update_schema = NotificationUpdateSchema()


@notifications_bp.route('', methods=['GET'])
@jwt_required()
def get_notifications():
    """
    Get all notifications for current user
    ---
    tags:
      - Notifications
    security:
      - Bearer: []
    parameters:
      - in: query
        name: unread_only
        type: boolean
        description: Filter to show only unread notifications
    responses:
      200:
        description: List of notifications
    """
    current_user_id = int(get_jwt_identity())
    query = Notification.query.filter_by(user_id=current_user_id)
    
    unread_only = request.args.get('unread_only', 'false').lower() == 'true'
    if unread_only:
        query = query.filter_by(is_read=False)
    
    notifications = query.order_by(Notification.created_at.desc()).limit(50).all()
    return jsonify(notifications_schema.dump(notifications)), 200


@notifications_bp.route('/unread-count', methods=['GET'])
@jwt_required()
def get_unread_count():
    """
    Get count of unread notifications
    ---
    tags:
      - Notifications
    security:
      - Bearer: []
    responses:
      200:
        description: Unread notification count
    """
    current_user_id = int(get_jwt_identity())
    count = Notification.query.filter_by(user_id=current_user_id, is_read=False).count()
    return jsonify({'unread_count': count}), 200


@notifications_bp.route('/<int:notification_id>', methods=['PUT'])
@jwt_required()
def update_notification(notification_id):
    """
    Mark notification as read/unread
    ---
    tags:
      - Notifications
    security:
      - Bearer: []
    parameters:
      - in: path
        name: notification_id
        type: integer
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - is_read
          properties:
            is_read:
              type: boolean
    responses:
      200:
        description: Notification updated
      404:
        description: Notification not found
    """
    current_user_id = int(get_jwt_identity())
    notification = Notification.query.filter_by(
        id=notification_id, 
        user_id=current_user_id
    ).first_or_404()
    
    try:
        data = notification_update_schema.load(request.json)
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400
    
    notification.is_read = data['is_read']
    db.session.commit()
    
    return jsonify(notification_schema.dump(notification)), 200


@notifications_bp.route('/mark-all-read', methods=['POST'])
@jwt_required()
def mark_all_read():
    """
    Mark all notifications as read
    ---
    tags:
      - Notifications
    security:
      - Bearer: []
    responses:
      200:
        description: All notifications marked as read
    """
    current_user_id = int(get_jwt_identity())
    Notification.query.filter_by(user_id=current_user_id, is_read=False).update({'is_read': True})
    db.session.commit()
    
    return jsonify({'message': 'All notifications marked as read'}), 200


@notifications_bp.route('/<int:notification_id>', methods=['DELETE'])
@jwt_required()
def delete_notification(notification_id):
    """
    Delete a notification
    ---
    tags:
      - Notifications
    security:
      - Bearer: []
    parameters:
      - in: path
        name: notification_id
        type: integer
        required: true
    responses:
      200:
        description: Notification deleted
      404:
        description: Notification not found
    """
    current_user_id = int(get_jwt_identity())
    notification = Notification.query.filter_by(
        id=notification_id, 
        user_id=current_user_id
    ).first_or_404()
    
    db.session.delete(notification)
    db.session.commit()
    
    return jsonify({'message': 'Notification deleted'}), 200


@notifications_bp.route('/stream', methods=['GET'])
@jwt_required()
def stream_notifications():
    """
    Server-Sent Events stream for real-time notifications
    ---
    tags:
      - Notifications
    security:
      - Bearer: []
    responses:
      200:
        description: SSE stream of notifications
    """
    current_user_id = int(get_jwt_identity())
    
    def generate():
        last_id = 0
        while True:
            # Check for new notifications
            notifications = Notification.query.filter(
                Notification.user_id == current_user_id,
                Notification.id > last_id,
                Notification.is_read == False
            ).order_by(Notification.id.asc()).all()
            
            for notification in notifications:
                last_id = notification.id
                yield f"data: {json.dumps(notification.to_dict())}\n\n"
            
            time.sleep(2)  # Poll every 2 seconds
    
    return Response(
        generate(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive'
        }
    )

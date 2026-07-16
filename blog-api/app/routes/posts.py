from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from app import db, cache
from app.models.post import Post
from app.models.comment import Comment
from app.models.category import Category
from app.models.user import User
from app.schemas.post import PostSchema, PostCreateSchema, PostUpdateSchema
from app.schemas.comment import CommentSchema, CommentCreateSchema
from app.utils.errors import NotFoundError, ForbiddenError, ValidationError as APIValidationError

posts_bp = Blueprint('posts', __name__)
post_schema = PostSchema()
posts_schema = PostSchema(many=True)
post_create_schema = PostCreateSchema()
post_update_schema = PostUpdateSchema()
comment_schema = CommentSchema()
comments_schema = CommentSchema(many=True)
comment_create_schema = CommentCreateSchema()


def make_cache_key():
    """Generate cache key based on request args."""
    return f"posts:{request.args.get('page', 1)}:{request.args.get('per_page', 20)}:{request.args.get('category', '')}"


def invalidate_posts_cache():
    """Invalidate all posts-related cache."""
    cache.clear()


@posts_bp.route('', methods=['GET'])
@cache.cached(timeout=60, key_prefix=make_cache_key)
def get_posts():
    """
    Get all posts with pagination
    ---
    tags:
      - Posts
    parameters:
      - in: query
        name: page
        type: integer
        default: 1
      - in: query
        name: per_page
        type: integer
        default: 20
      - in: query
        name: category
        type: string
        description: Filter by category slug
    responses:
      200:
        description: List of posts
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', current_app.config.get('POSTS_PER_PAGE', 20), type=int)
    category_slug = request.args.get('category')
    
    query = Post.query.filter_by(is_published=True)
    
    if category_slug:
        category = Category.query.filter_by(slug=category_slug).first()
        if category:
            query = query.filter_by(category_id=category.id)
    
    pagination = query.order_by(Post.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'status': 'success',
        'posts': posts_schema.dump(pagination.items),
        'pagination': {
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    }), 200


@posts_bp.route('', methods=['POST'])
@jwt_required()
def create_post():
    """
    Create a new post
    ---
    tags:
      - Posts
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
            - content
          properties:
            title:
              type: string
              example: My First Blog Post
            content:
              type: string
              example: This is the content of my blog post...
            excerpt:
              type: string
              example: A brief summary
            category_id:
              type: integer
              example: 1
            is_published:
              type: boolean
              default: true
    responses:
      201:
        description: Post created successfully
      400:
        description: Validation error
      401:
        description: Unauthorized
    """
    current_user_id = get_jwt_identity()
    
    try:
        data = post_create_schema.load(request.json)
    except ValidationError as err:
        raise APIValidationError('Validation failed', errors=err.messages)
    
    # Validate category if provided
    if data.get('category_id'):
        category = Category.query.get(data['category_id'])
        if not category:
            raise NotFoundError('Category not found')
    
    # Generate slug from title
    base_slug = Post.generate_slug(data['title'])
    slug = base_slug
    counter = 1
    while Post.query.filter_by(slug=slug).first():
        slug = f"{base_slug}-{counter}"
        counter += 1
    
    post = Post(
        title=data['title'],
        slug=slug,
        content=data['content'],
        excerpt=data.get('excerpt'),
        category_id=data.get('category_id'),
        is_published=data.get('is_published', True),
        author_id=int(current_user_id)
    )
    
    db.session.add(post)
    db.session.commit()
    
    # Invalidate cache
    invalidate_posts_cache()
    
    return jsonify({
        'status': 'success',
        'message': 'Post created successfully',
        'post': post_schema.dump(post)
    }), 201


@posts_bp.route('/<int:post_id>', methods=['GET'])
@cache.cached(timeout=120)
def get_post(post_id):
    """
    Get a single post by ID
    ---
    tags:
      - Posts
    parameters:
      - in: path
        name: post_id
        type: integer
        required: true
    responses:
      200:
        description: Post details
      404:
        description: Post not found
    """
    post = Post.query.get(post_id)
    if not post:
        raise NotFoundError('Post not found')
    
    return jsonify({
        'status': 'success',
        'post': post_schema.dump(post)
    }), 200


@posts_bp.route('/<int:post_id>', methods=['PUT'])
@jwt_required()
def update_post(post_id):
    """
    Update a post
    ---
    tags:
      - Posts
    security:
      - Bearer: []
    parameters:
      - in: path
        name: post_id
        type: integer
        required: true
      - in: body
        name: body
        schema:
          type: object
          properties:
            title:
              type: string
            content:
              type: string
            excerpt:
              type: string
            category_id:
              type: integer
            is_published:
              type: boolean
    responses:
      200:
        description: Post updated successfully
      401:
        description: Unauthorized
      403:
        description: Forbidden - not the author
      404:
        description: Post not found
    """
    current_user_id = get_jwt_identity()
    
    post = Post.query.get(post_id)
    if not post:
        raise NotFoundError('Post not found')
    
    if post.author_id != int(current_user_id):
        raise ForbiddenError('You can only edit your own posts')
    
    try:
        data = post_update_schema.load(request.json)
    except ValidationError as err:
        raise APIValidationError('Validation failed', errors=err.messages)
    
    # Update slug if title changed
    if 'title' in data and data['title'] != post.title:
        base_slug = Post.generate_slug(data['title'])
        slug = base_slug
        counter = 1
        while Post.query.filter(Post.slug == slug, Post.id != post.id).first():
            slug = f"{base_slug}-{counter}"
            counter += 1
        post.slug = slug
    
    # Validate category if provided
    if 'category_id' in data and data['category_id']:
        category = Category.query.get(data['category_id'])
        if not category:
            raise NotFoundError('Category not found')
    
    for key, value in data.items():
        setattr(post, key, value)
    
    db.session.commit()
    
    # Invalidate cache
    invalidate_posts_cache()
    
    return jsonify({
        'status': 'success',
        'message': 'Post updated successfully',
        'post': post_schema.dump(post)
    }), 200


@posts_bp.route('/<int:post_id>', methods=['DELETE'])
@jwt_required()
def delete_post(post_id):
    """
    Delete a post
    ---
    tags:
      - Posts
    security:
      - Bearer: []
    parameters:
      - in: path
        name: post_id
        type: integer
        required: true
    responses:
      200:
        description: Post deleted successfully
      401:
        description: Unauthorized
      403:
        description: Forbidden - not the author
      404:
        description: Post not found
    """
    current_user_id = get_jwt_identity()
    
    post = Post.query.get(post_id)
    if not post:
        raise NotFoundError('Post not found')
    
    if post.author_id != int(current_user_id):
        raise ForbiddenError('You can only delete your own posts')
    
    db.session.delete(post)
    db.session.commit()
    
    # Invalidate cache
    invalidate_posts_cache()
    
    return jsonify({
        'status': 'success',
        'message': 'Post deleted successfully'
    }), 200


# Comment routes
@posts_bp.route('/<int:post_id>/comments', methods=['GET'])
def get_comments(post_id):
    """
    Get comments for a post
    ---
    tags:
      - Comments
    parameters:
      - in: path
        name: post_id
        type: integer
        required: true
    responses:
      200:
        description: List of comments
      404:
        description: Post not found
    """
    post = Post.query.get(post_id)
    if not post:
        raise NotFoundError('Post not found')
    
    comments = Comment.query.filter_by(post_id=post_id).order_by(Comment.created_at.desc()).all()
    
    return jsonify({
        'status': 'success',
        'comments': comments_schema.dump(comments)
    }), 200


@posts_bp.route('/<int:post_id>/comments', methods=['POST'])
@jwt_required()
def create_comment(post_id):
    """
    Create a comment on a post
    ---
    tags:
      - Comments
    security:
      - Bearer: []
    parameters:
      - in: path
        name: post_id
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
              example: Great post! Thanks for sharing.
    responses:
      201:
        description: Comment created successfully
      400:
        description: Validation error
      401:
        description: Unauthorized
      404:
        description: Post not found
    """
    current_user_id = get_jwt_identity()
    
    post = Post.query.get(post_id)
    if not post:
        raise NotFoundError('Post not found')
    
    try:
        data = comment_create_schema.load(request.json)
    except ValidationError as err:
        raise APIValidationError('Validation failed', errors=err.messages)
    
    comment = Comment(
        content=data['content'],
        post_id=post_id,
        author_id=int(current_user_id)
    )
    
    db.session.add(comment)
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': 'Comment created successfully',
        'comment': comment_schema.dump(comment)
    }), 201


@posts_bp.route('/<int:post_id>/comments/<int:comment_id>', methods=['DELETE'])
@jwt_required()
def delete_comment(post_id, comment_id):
    """
    Delete a comment
    ---
    tags:
      - Comments
    security:
      - Bearer: []
    parameters:
      - in: path
        name: post_id
        type: integer
        required: true
      - in: path
        name: comment_id
        type: integer
        required: true
    responses:
      200:
        description: Comment deleted successfully
      401:
        description: Unauthorized
      403:
        description: Forbidden - not the author
      404:
        description: Comment not found
    """
    current_user_id = get_jwt_identity()
    
    comment = Comment.query.filter_by(id=comment_id, post_id=post_id).first()
    if not comment:
        raise NotFoundError('Comment not found')
    
    if comment.author_id != int(current_user_id):
        raise ForbiddenError('You can only delete your own comments')
    
    db.session.delete(comment)
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': 'Comment deleted successfully'
    }), 200

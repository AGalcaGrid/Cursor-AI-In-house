from flask import Blueprint, request, jsonify, current_app

from app.models.post import Post
from app.schemas.post import PostSchema

search_bp = Blueprint('search', __name__)
posts_schema = PostSchema(many=True)


@search_bp.route('', methods=['GET'])
def search_posts():
    """
    Search posts by keyword
    ---
    tags:
      - Search
    parameters:
      - in: query
        name: q
        type: string
        required: true
        description: Search keyword
      - in: query
        name: page
        type: integer
        default: 1
      - in: query
        name: per_page
        type: integer
        default: 20
    responses:
      200:
        description: Search results
      400:
        description: Missing search query
    """
    query = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', current_app.config.get('POSTS_PER_PAGE', 20), type=int)
    
    if not query:
        return jsonify({
            'status': 'error',
            'message': 'Search query is required'
        }), 400
    
    # Search in title and content
    search_filter = Post.query.filter(
        Post.is_published == True,
        (Post.title.ilike(f'%{query}%') | Post.content.ilike(f'%{query}%'))
    )
    
    pagination = search_filter.order_by(Post.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'status': 'success',
        'query': query,
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

from datetime import datetime
from flask import request


def format_datetime(dt):
    """Format datetime object to ISO format string."""
    if dt is None:
        return None
    return dt.isoformat()


def paginate_query(query, schema):
    """
    Paginate a SQLAlchemy query.
    
    Args:
        query: SQLAlchemy query object
        schema: Marshmallow schema for serialization
    
    Returns:
        dict: Paginated results with metadata
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    per_page = min(per_page, 100)  # Max 100 items per page
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return {
        'items': schema.dump(pagination.items),
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total_pages': pagination.pages,
            'total_items': pagination.total,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    }

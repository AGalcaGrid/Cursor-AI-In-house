from marshmallow import fields, validate
from app import ma
from app.models.project import Project, TeamMember


class ProjectSchema(ma.SQLAlchemyAutoSchema):
    """Schema for project serialization."""
    class Meta:
        model = Project
        include_fk = True
        load_instance = True
    
    owner = fields.Nested('UserSchema', only=['id', 'username', 'email'], dump_only=True)


class ProjectCreateSchema(ma.Schema):
    """Schema for project creation."""
    name = fields.String(
        required=True,
        validate=validate.Length(min=1, max=200)
    )
    description = fields.String(allow_none=True)
    status = fields.String(
        validate=validate.OneOf(['active', 'archived', 'completed']),
        load_default='active'
    )


class ProjectUpdateSchema(ma.Schema):
    """Schema for project updates."""
    name = fields.String(validate=validate.Length(min=1, max=200))
    description = fields.String(allow_none=True)
    status = fields.String(
        validate=validate.OneOf(['active', 'archived', 'completed'])
    )


class TeamMemberSchema(ma.SQLAlchemyAutoSchema):
    """Schema for team member serialization."""
    class Meta:
        model = TeamMember
        include_fk = True
        load_instance = True
    
    user = fields.Nested('UserSchema', only=['id', 'username', 'email'], dump_only=True)


class TeamMemberCreateSchema(ma.Schema):
    """Schema for adding team members."""
    user_id = fields.Integer(required=True)
    role = fields.String(
        validate=validate.OneOf(['admin', 'member', 'viewer']),
        load_default='member'
    )


class TeamMemberUpdateSchema(ma.Schema):
    """Schema for updating team member role."""
    role = fields.String(
        required=True,
        validate=validate.OneOf(['admin', 'member', 'viewer'])
    )

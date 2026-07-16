from app.models.user import User
from app.models.customer import Customer
from app.models.agent import Agent
from app.models.ticket import Ticket, TicketStatusHistory, TicketAssignment, PriorityChangeHistory
from app.models.comment import Comment
from app.models.attachment import Attachment

__all__ = [
    'User', 'Customer', 'Agent', 
    'Ticket', 'TicketStatusHistory', 'TicketAssignment', 'PriorityChangeHistory',
    'Comment', 'Attachment'
]

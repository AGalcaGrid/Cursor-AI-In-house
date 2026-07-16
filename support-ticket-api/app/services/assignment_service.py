"""
Auto-assignment Service (FR-006)
Automatically assigns tickets based on agent workload and expertise.
"""
from sqlalchemy import func
from app import db
from app.models.user import User
from app.models.ticket import Ticket
from app.models.assignment import Assignment
from app.services.email_service import EmailService


class AssignmentService:
    """Service for automatic ticket assignment."""
    
    @staticmethod
    def get_agent_workload():
        """Get current workload for all available agents."""
        # Count open tickets per agent
        workload = db.session.query(
            User.id,
            User.name,
            User.email,
            User.expertise_areas,
            User.availability_status,
            func.count(Ticket.id).label('open_tickets')
        ).outerjoin(
            Ticket,
            (User.id == Ticket.assigned_to_id) & 
            (Ticket.status.notin_(['resolved', 'closed']))
        ).filter(
            User.role.in_(['agent', 'admin']),
            User.is_active == True,
            User.availability_status == 'available'
        ).group_by(User.id).all()
        
        return workload
    
    @classmethod
    def find_best_agent(cls, ticket):
        """
        Find the best agent to assign a ticket to based on:
        1. Agent availability status
        2. Current workload (number of open tickets)
        3. Category expertise (if applicable)
        """
        workload = cls.get_agent_workload()
        
        if not workload:
            return None
        
        # Score each agent
        scored_agents = []
        for agent in workload:
            score = 100  # Base score
            
            # Reduce score based on workload (fewer tickets = higher score)
            score -= agent.open_tickets * 10
            
            # Bonus for category expertise
            if agent.expertise_areas and ticket.category in agent.expertise_areas:
                score += 20
            
            # Bonus for priority expertise
            if ticket.priority == 'urgent' and agent.expertise_areas:
                if 'urgent' in agent.expertise_areas or 'escalation' in agent.expertise_areas:
                    score += 15
            
            scored_agents.append({
                'agent_id': agent.id,
                'name': agent.name,
                'email': agent.email,
                'score': score,
                'open_tickets': agent.open_tickets
            })
        
        # Sort by score (highest first), then by workload (lowest first)
        scored_agents.sort(key=lambda x: (-x['score'], x['open_tickets']))
        
        if scored_agents:
            return User.query.get(scored_agents[0]['agent_id'])
        
        return None
    
    @classmethod
    def auto_assign_ticket(cls, ticket, assigned_by_user):
        """
        Automatically assign a ticket to the best available agent.
        Returns the assigned agent or None if no agent available.
        """
        agent = cls.find_best_agent(ticket)
        
        if not agent:
            return None
        
        # Create assignment record
        assignment = Assignment(
            ticket_id=ticket.id,
            assigned_to_id=agent.id,
            assigned_by_id=assigned_by_user.id if assigned_by_user else None
        )
        db.session.add(assignment)
        
        # Update ticket
        ticket.assigned_to_id = agent.id
        if ticket.status == 'open':
            ticket.status = 'assigned'
        
        db.session.commit()
        
        # Send notification
        EmailService.notify_ticket_assigned(ticket, agent)
        
        return agent
    
    @classmethod
    def reassign_unassigned_tickets(cls):
        """
        Background task to assign any unassigned tickets.
        Can be called periodically by a scheduler.
        """
        unassigned = Ticket.query.filter(
            Ticket.assigned_to_id.is_(None),
            Ticket.status == 'open'
        ).all()
        
        assigned_count = 0
        for ticket in unassigned:
            agent = cls.auto_assign_ticket(ticket, None)
            if agent:
                assigned_count += 1
        
        return assigned_count

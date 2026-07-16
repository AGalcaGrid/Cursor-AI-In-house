"""
Export Service for generating CSV and PDF reports (FR-028, FR-031)
"""
import csv
import io
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_LEFT


class ExportService:
    """Service for exporting data to CSV and PDF formats."""
    
    @staticmethod
    def tickets_to_csv(tickets):
        """
        Export tickets to CSV format (FR-028).
        Returns a string buffer containing CSV data.
        """
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header row
        writer.writerow([
            'Ticket Number',
            'Subject',
            'Status',
            'Priority',
            'Category',
            'Customer Email',
            'Assigned Agent',
            'Created At',
            'Updated At',
            'Resolved At',
            'SLA Breached'
        ])
        
        # Data rows
        for ticket in tickets:
            writer.writerow([
                ticket.ticket_number,
                ticket.subject,
                ticket.status,
                ticket.priority,
                ticket.category,
                ticket.customer_email,
                ticket.assigned_agent.name if ticket.assigned_agent else 'Unassigned',
                ticket.created_at.strftime('%Y-%m-%d %H:%M:%S') if ticket.created_at else '',
                ticket.updated_at.strftime('%Y-%m-%d %H:%M:%S') if ticket.updated_at else '',
                ticket.resolved_at.strftime('%Y-%m-%d %H:%M:%S') if ticket.resolved_at else '',
                'Yes' if ticket.sla_response_breached or ticket.sla_resolution_breached else 'No'
            ])
        
        output.seek(0)
        return output.getvalue()
    
    @staticmethod
    def tickets_to_pdf(tickets, title="Ticket Report"):
        """
        Export tickets to PDF format (FR-031).
        Returns a bytes buffer containing PDF data.
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
        
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            alignment=TA_CENTER,
            spaceAfter=20
        )
        elements.append(Paragraph(title, title_style))
        
        # Generated date
        date_style = ParagraphStyle(
            'DateStyle',
            parent=styles['Normal'],
            fontSize=10,
            alignment=TA_CENTER,
            spaceAfter=20
        )
        elements.append(Paragraph(f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}", date_style))
        elements.append(Spacer(1, 20))
        
        # Table data
        data = [['Ticket #', 'Subject', 'Status', 'Priority', 'Assigned To', 'Created']]
        
        for ticket in tickets:
            data.append([
                ticket.ticket_number,
                ticket.subject[:30] + '...' if len(ticket.subject) > 30 else ticket.subject,
                ticket.status.replace('_', ' ').title(),
                ticket.priority.upper(),
                ticket.assigned_agent.name if ticket.assigned_agent else 'Unassigned',
                ticket.created_at.strftime('%Y-%m-%d') if ticket.created_at else ''
            ])
        
        # Create table
        table = Table(data, colWidths=[1.2*inch, 2*inch, 0.9*inch, 0.7*inch, 1.2*inch, 0.9*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
        ]))
        
        elements.append(table)
        
        # Summary
        elements.append(Spacer(1, 30))
        summary_style = ParagraphStyle('Summary', parent=styles['Normal'], fontSize=10)
        elements.append(Paragraph(f"<b>Total Tickets:</b> {len(tickets)}", summary_style))
        
        # Count by status
        status_counts = {}
        for ticket in tickets:
            status_counts[ticket.status] = status_counts.get(ticket.status, 0) + 1
        
        for status, count in status_counts.items():
            elements.append(Paragraph(f"<b>{status.replace('_', ' ').title()}:</b> {count}", summary_style))
        
        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()
    
    @staticmethod
    def agent_report_to_pdf(agent_data, title="Agent Performance Report"):
        """
        Export agent performance report to PDF.
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
        
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            alignment=TA_CENTER,
            spaceAfter=20
        )
        elements.append(Paragraph(title, title_style))
        
        # Generated date
        date_style = ParagraphStyle(
            'DateStyle',
            parent=styles['Normal'],
            fontSize=10,
            alignment=TA_CENTER,
            spaceAfter=20
        )
        elements.append(Paragraph(f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}", date_style))
        elements.append(Spacer(1, 20))
        
        # Table data
        data = [['Agent Name', 'Total Tickets', 'Resolved', 'Avg Resolution (hrs)', 'SLA Compliance']]
        
        for agent in agent_data:
            data.append([
                agent.get('name', 'N/A'),
                str(agent.get('total_tickets', 0)),
                str(agent.get('resolved_tickets', 0)),
                f"{agent.get('avg_resolution_hours', 0):.1f}",
                f"{agent.get('sla_compliance', 0):.1f}%"
            ])
        
        # Create table
        table = Table(data, colWidths=[1.8*inch, 1.2*inch, 1*inch, 1.5*inch, 1.2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
        ]))
        
        elements.append(table)
        
        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()
    
    @staticmethod
    def sla_report_to_csv(sla_data):
        """
        Export SLA compliance report to CSV.
        """
        output = io.StringIO()
        writer = csv.writer(output)
        
        writer.writerow([
            'Ticket Number',
            'Subject',
            'Priority',
            'Response SLA',
            'Response Actual',
            'Response Breached',
            'Resolution SLA',
            'Resolution Actual',
            'Resolution Breached'
        ])
        
        for item in sla_data:
            writer.writerow([
                item.get('ticket_number', ''),
                item.get('subject', ''),
                item.get('priority', ''),
                item.get('response_sla', ''),
                item.get('response_actual', ''),
                'Yes' if item.get('response_breached') else 'No',
                item.get('resolution_sla', ''),
                item.get('resolution_actual', ''),
                'Yes' if item.get('resolution_breached') else 'No'
            ])
        
        output.seek(0)
        return output.getvalue()

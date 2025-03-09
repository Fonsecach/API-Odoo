import base64
import time
from datetime import datetime


class HealthCheck:
    def __init__(self):
        self.status = 'ok'
        self.version = '0.1.0'
        self.start_time = time.time()

    def get_health_check(self) -> dict:
        return {
            'status': 'healthy',
            'version': self.version,
            'timestamp': datetime.now(),
            'uptime': time.time() - self.start_time,
        }

    def get_ping_status(self) -> dict:
        return {'status': 'ok'}



def create_helpdesk_ticket(models, db, uid, password, ticket_data):
    """Cria um novo ticket na central de ajuda com anexos"""
    try:
        # Mapeamento dos campos para o Odoo
        ticket_vals = {
            'stage_id': ticket_data.stage_id,
            'team_id': ticket_data.team_id,
            'user_id': ticket_data.user_id,
            'partner_id': ticket_data.partner_id,
            'name': ticket_data.name.upper(),
            'description': ticket_data.description,
            'priority': ticket_data.priority,
            'x_studio_selection_field_4el_1ianiqtqf': ticket_data.x_studio_selection_field_4el_1ianiqtqf
        }
        
        # Cria o ticket
        ticket_id = models.execute_kw(
            db, uid, password,
            'helpdesk.ticket', 'create',
            [ticket_vals]
        )
        
        # Processa os anexos
        doc_results = []
        for doc in ticket_data.documents:
            try:
                attachment_id = models.execute_kw(
                    db, uid, password,
                    'ir.attachment', 'create',
                    [{
                        'name': doc.filename,
                        'datas': doc.file_content,
                        'res_model': 'helpdesk.ticket',
                        'res_id': ticket_id
                    }]
                )
                doc_results.append({
                    'filename': doc.filename,
                    'success': True,
                    'attachment_id': attachment_id
                })
            except Exception as e:
                doc_results.append({
                    'filename': doc.filename,
                    'success': False,
                    'error': str(e)
                })
        
        return {
            'ticket_id': ticket_id,
            'success': True,
            'documents': doc_results
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': f"Erro ao criar ticket: {str(e)}",
            'documents': []
        }


async def process_attachments(models, db, uid, password, ticket_id, files):
    doc_responses = []
    for file in files:
        try:
            content = await file.read()
            encoded_content = base64.b64encode(content).decode('utf-8')
            
            attachment_id = models.execute_kw(
                db, uid, password,
                'ir.attachment', 'create',
                [{
                    'name': file.filename,
                    'datas': encoded_content,
                    'res_model': 'helpdesk.ticket',
                    'res_id': ticket_id
                }]
            )
            doc_responses.append({
                'filename': file.filename,
                'success': True,
                'attachment_id': attachment_id
            })
        except Exception as e:
            doc_responses.append({
                'filename': file.filename,
                'success': False,
                'error': str(e)
            })
    return doc_responses

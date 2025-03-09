from datetime import datetime
from http import HTTPStatus
from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, logger

from app.Services.health_service import create_helpdesk_ticket, process_attachments
from app.config.settings import ODOO_DB, ODOO_PASSWORD, ODOO_URL, ODOO_USERNAME
from app.Services.authentication import authenticate_odoo, connect_to_odoo
from app.Services.helpdesk_service import (
    get_helpdesk_info,
    get_helpdesk_info_by_team_and_id,
    get_helpdesk_info_by_team_id,
)
from app.schemas.schemas import TicketCreateSchema, TicketResponse
from app.utils.utils import validar_formato_nome

router = APIRouter(prefix='/tickets', tags=['Central de Ajuda'])


@router.get('/', summary='Lista todos os chamados abertos')
async def list_tickets(limit: int = 100, offset: int = 0):
    common, models = connect_to_odoo(ODOO_URL)
    uid = authenticate_odoo(common, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD)

    if not uid:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Falha na autentificação no Odoo',
        )

    helpdesk_info = get_helpdesk_info(
        models, ODOO_DB, uid, ODOO_PASSWORD, limit, offset
    )

    if not helpdesk_info:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Nenhum chamado localizado',
        )

    return {'chamados': helpdesk_info}


@router.get('/{team_id}', summary='Lista todos os chamados abertos do time')
async def list_tickets_by_team_id(
    team_id: int, limit: int = 100, offset: int = 0
):
    common, models = connect_to_odoo(ODOO_URL)
    uid = authenticate_odoo(common, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD)

    if not uid:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Falha na autentificação no Odoo',
        )

    helpdesk_info = get_helpdesk_info_by_team_id(
        models, ODOO_DB, uid, ODOO_PASSWORD, team_id, limit, offset
    )

    if not helpdesk_info:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Nenhum chamado localizado',
        )

    return {'chamados': helpdesk_info}


@router.get(
    '/{team_id}/{ticket_id}',
    summary='Lista todos os chamados abertos do time',
)
async def list_tickets_by_team_id(team_id: int, ticket_id: int):
    common, models = connect_to_odoo(ODOO_URL)
    uid = authenticate_odoo(common, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD)

    if not uid:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Falha na autentificação no Odoo',
        )

    helpdesk_info = get_helpdesk_info_by_team_and_id(
        models, ODOO_DB, uid, ODOO_PASSWORD, team_id, ticket_id
    )

    if not helpdesk_info:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Nenhum chamado localizado',
        )

    return {'chamados': helpdesk_info}


@router.get(
    '/{team_id}/{stage_id}',
    summary='Lista todos os chamados abertos do time por estágio',
)
async def list_tickets_by_team_and_stage_id(
    team_id: int, stage_id: int, limit: int = 100, offset: int = 0
):
    common, models = connect_to_odoo(ODOO_URL)
    uid = authenticate_odoo(common, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD)

    if not uid:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Falha na autentificação no Odoo',
        )

    helpdesk_info = get_helpdesk_info_by_team_and_id(
        models, ODOO_DB, uid, ODOO_PASSWORD, team_id, stage_id, limit, offset
    )

    if not helpdesk_info:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Nenhum chamado localizado',
        )

    return {'chamados': helpdesk_info}


def format_cnpj_name(name: str) -> str:
    parts = name.rsplit(' ', 1)
    if len(parts) != 2 or len(parts[1]) != 14:
        raise HTTPException(
            status_code=400,
            detail="Formato CNPJ inválido no campo name"
        )
    
    cnpj = parts[1]
    formatted_cnpj = f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:14]}"
    return f"{parts[0]} {formatted_cnpj}"


@router.post(
    '/',
    summary='Cria novo ticket com anexos',
    response_model=TicketResponse,
    status_code=201
)
async def create_ticket_with_files(
    ticket_data: TicketCreateSchema = Depends(),
    files: List[UploadFile] = File(...)
):
    try:
        # Autenticação
        common, models = connect_to_odoo(ODOO_URL)
        uid = authenticate_odoo(common, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD)
        
        if not uid:
            raise HTTPException(status_code=401, detail="Autenticação falhou")

        ticket_dict = ticket_data.dict(by_alias=True)

        # Cria ticket
        ticket_id = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'helpdesk.ticket', 'create', [ticket_dict]
        )

        # Processa anexos
        doc_results = await process_attachments(
            models, ODOO_DB, uid, ODOO_PASSWORD, ticket_id, files
        )

        return TicketResponse(
            ticket_id=ticket_id,
            success=True,
            documents=doc_results
        )

    except Exception as e:
        logger.error(f"Erro: {str(e)}")
        return TicketResponse(
            success=False,
            error=str(e)
        )

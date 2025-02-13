from datetime import datetime

from pydantic import BaseModel, EmailStr


class Company_default(BaseModel):
    company_type: int = 0
    name: str
    vat: str
    country_id: int = 31
    phone: str
    email: EmailStr


class Company_return(Company_default):
    company_id: int

# Utilizado no metodo para atualizar alguns campos do modelo de clientes
class contact_update(BaseModel):
    vat: str | None
    x_studio_categoria_economica: str | None
    company_type: str = 'company'
    
    
class Opportunity_default(BaseModel):
    name: str
    partner_id: int
    x_studio_tese: str | None
    user_id: int
    team_id: int
    stage_id: int = 10


class Opportunity_return(Opportunity_default):
    opportunity_id: int


class TarefaCreate(BaseModel):
    name: str
    project_id: int
    stage_id: int
    x_studio_tese_2: str | None
    x_studio_segmento: str | None


class TarefaUpdate(BaseModel):
    partner_id: int | None
    x_studio_tese_2: str
    x_studio_segmento: str | None


class PartnerNames(BaseModel):
    names: list[str]


class Config:
    extra = 'allow'


class Message(BaseModel):
    message: str


class HealthCheck(BaseModel):
    status: str
    version: str
    timestamp: datetime
    uptime: float


class PingResponse(BaseModel):
    status: str

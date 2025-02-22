from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


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


class SaleOrderLine(BaseModel):
    product_id: int = Field(..., description="ID do produto")
    product_uom_qty: float = Field(..., description="Quantidade do produto")
    price_unit: float = Field(..., description="Preço unitário do produto")


class SaleOrderCreate(BaseModel):
    partner_id: int = Field(..., description="ID do cliente")
    opportunity_id: Optional[int] = Field(None, description="ID da oportunidade (crm.lead) vinculada")
    order_line: List[SaleOrderLine] = Field(..., description="Lista de itens do pedido")
    date_order: Optional[datetime] = Field(
        default_factory=datetime.now,  # Valor padrão: data e hora atuais
        description="Data do pedido (formato: YYYY-MM-DD)"
    )
    client_order_ref: Optional[str] = Field(None, description="Referência do pedido do cliente")
    type_name: str = Field(default="Pedido de venda", description="Tipo do pedido")


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

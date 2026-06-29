from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from backend.database import Base

class Comprovante(Base):
    __tablename__ = "comprovantes"

    id = Column(Integer, primary_key=True, index=True)
    original_filename = Column(String, nullable=False)
    saved_filename = Column(String, nullable=False)
    description = Column(String, nullable=False)
    bank = Column(String, nullable=True) # Banco Origem
    comprovante_type = Column(String, nullable=True) # BOLETO, TRIBUTO, CONSUMO, PIX, TRANSFERENCIA_INTERNA
    amount = Column(Float, nullable=True)
    date = Column(String, nullable=True) # AAAA-MM-DD
    source_path = Column(String, nullable=False) # Usamos para CONTA ORIGEM
    
    # NOVAS COLUNAS PARA TRANSFERÊNCIAS
    dest_bank = Column(String, nullable=True)    # Banco Destino
    dest_account = Column(String, nullable=True) # Conta Destino
    
    page_number = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
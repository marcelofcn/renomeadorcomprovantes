"""
FastAPI Application - Renomeador de Comprovantes v2.0
"""
import sys
import logging
import time
import os
import zipfile
from io import BytesIO
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func

# Adicionar parent directory para importações de módulos internos
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.config import settings, CORS_ORIGINS
from backend.database import SessionLocal, get_db, engine, Base
from backend.models.comprovante import Comprovante
from backend.services.pdf_processing import process_pdf_file, listar_comprovantes

# --- CONFIGURAÇÃO DE DIRETÓRIOS (NA RAIZ DO PROJETO) ---
BASE_DIR = Path(__file__).parent.parent
UPLOAD_DIR = BASE_DIR / 'data' / 'uploads'
PROCESSADOS_DIR = BASE_DIR / 'data' / 'processados'

# Garantir que as pastas existam
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
PROCESSADOS_DIR.mkdir(parents=True, exist_ok=True)

# Configurar Logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)

# Configuração de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Em produção, substitua por CORS_ORIGINS
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Inicializa as tabelas do banco de dados ao ligar o servidor."""
    Base.metadata.create_all(bind=engine)
    logger.info("Banco de dados e diretórios inicializados com sucesso.")

@app.get("/api/health")
async def health():
    """Rota de verificação de status."""
    return {"status": "ok", "app": settings.APP_NAME}

# --- ROTA DE UPLOAD (Aceita /upload e /upload/pdf) ---
@app.post("/api/upload")
@app.post("/api/upload/pdf")
async def upload_comprovante(
    file: UploadFile = File(...), 
    bank: str = Form(...), # Nome do banco selecionado no select do frontend
    db: Session = Depends(get_db)
):
    try:
        # 1. Validar extensão
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Apenas arquivos PDF são aceitos.")

        # 2. Salvar arquivo temporariamente
        content = await file.read()
        safe_filename = Path(file.filename).name
        temp_path = UPLOAD_DIR / f"{int(time.time())}_{safe_filename}"
        temp_path.write_bytes(content)
        
        # 3. Processar o arquivo (Corte de páginas, Extração e Renomeação)
        stats = process_pdf_file(temp_path, safe_filename, db, banco_escolhido=bank)
        
        # 4. Verificar se a trava de segurança de banco foi acionada
        if stats.get("banco_invalido"):
            if temp_path.exists(): os.remove(temp_path)
            raise HTTPException(
                status_code=400, 
                detail=f"Conflito de Banco: Você selecionou '{bank}', mas o PDF enviado pertence ao '{stats['banco_detectado']}'."
            )

        # 5. Montar mensagem de retorno detalhada
        if stats["sucesso"] == 0 and stats["duplicado"] > 0:
            return {
                "status": "warning",
                "message": f"Aviso: Todas as {stats['duplicado']} páginas deste arquivo já foram processadas.",
                "data": stats
            }
        
        if stats["sucesso"] == 0:
            raise HTTPException(status_code=422, detail="Não foi possível extrair dados válidos do comprovante. Verifique o banco selecionado.")

        return {
            "status": "success", 
            "message": f"Processado: {stats['sucesso']} salvos, {stats['duplicado']} duplicados.", 
            "data": stats
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Erro crítico no upload: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro interno no servidor: {str(e)}")

# --- ROTA DASHBOARD: RESUMO AGRUPADO POR CONTA/DATA ---
@app.get("/api/dashboard/resumo")
def resumo_dashboard(db: Session = Depends(get_db)):
    """Retorna os dados para os cards do Dashboard."""
    agrupados = db.query(
        Comprovante.bank,
        Comprovante.source_path.label("conta"),
        Comprovante.date,
        func.count(Comprovante.id).label("total_arquivos"),
        func.sum(Comprovante.amount).label("valor_total")
    ).group_by(
        Comprovante.bank, 
        Comprovante.source_path, 
        Comprovante.date
    ).order_by(Comprovante.date.desc()).all()

    return [
        {
            "bank": r.bank,
            "conta": r.conta,
            "data_iso": r.date,
            "total_arquivos": r.total_arquivos,
            "valor_total": float(r.valor_total or 0)
        } for r in agrupados
    ]

# --- ROTA DOWNLOAD ZIP ---
@app.get("/api/download/zip/{date}/{account}")
def download_zip(date: str, account: str, db: Session = Depends(get_db)):
    """Gera um arquivo ZIP com todos os PDFs de um card do Dashboard."""
    comprovantes = db.query(Comprovante).filter(
        Comprovante.date == date,
        Comprovante.source_path == account
    ).all()

    if not comprovantes:
        raise HTTPException(status_code=404, detail="Nenhum arquivo encontrado para este lote.")

    io = BytesIO()
    with zipfile.ZipFile(io, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for c in comprovantes:
            caminho_arquivo = PROCESSADOS_DIR / c.saved_filename
            if caminho_arquivo.exists():
                zip_file.write(caminho_arquivo, arcname=c.saved_filename)

    io.seek(0)
    return StreamingResponse(
        io, 
        media_type="application/x-zip-compressed",
        headers={"Content-Disposition": f"attachment; filename=lote_{account}_{date}.zip"}
    )

# --- LISTAGEM E DOWNLOAD INDIVIDUAL ---

@app.get("/api/comprovantes")
def get_historico(db: Session = Depends(get_db)):
    """Retorna os últimos comprovantes processados."""
    return {"comprovantes": listar_comprovantes(db)}

@app.get("/api/download/{filename}")
def download_individual(filename: str):
    """Baixa um arquivo PDF renomeado individualmente."""
    path = PROCESSADOS_DIR / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail="Arquivo físico não encontrado.")
    return FileResponse(path=path)

if __name__ == "__main__":
    import uvicorn
    # Executa o servidor na porta 8000
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
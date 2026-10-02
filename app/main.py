from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.database import get_db_connection
from app.routes import auth

app = FastAPI(
    title="HoopID Backend FastAPI",
    description="API de rendimiento para atletas desarrollada en FastAPI",
    version="1.0.0",
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(auth.router)


@app.get("/api/health")
async def health_check():
    try:
        conn = await get_db_connection()
        db_time = await conn.fetchval("SELECT NOW()")
        await conn.close()
        return {"status": "ok", "db_time": str(db_time)}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error conectando a la base de datos: {str(e)}"
        )


@app.get("/")
async def root():
    return {"message": "Bienvenido a HoopID API (FastAPI)"}

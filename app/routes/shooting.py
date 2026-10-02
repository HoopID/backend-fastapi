from fastapi import APIRouter, Depends, HTTPException, status
from app.database import get_db_connection
from app.schemas import ShootingSessionCreate
from app.security import get_current_user

router = APIRouter(prefix="/api/shooting-sessions", tags=["Shooting Sessions"])


# GET /api/shooting-sessions/ - Listar todas las sesiones del usuario
@router.get("/")
async def get_sessions(current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    conn = await get_db_connection()
    try:
        rows = await conn.fetch(
            "SELECT * FROM shooting_sessions WHERE user_id = $1 ORDER BY session_date DESC",
            user_id,
        )
        sessions = []
        for r in rows:
            item = dict(r)
            made = item["shots_made"]
            attempted = item["shots_attempted"]
            item["shooting_percentage"] = (
                round((made / attempted * 100), 2) if attempted > 0 else 0.0
            )
            item["session_date"] = str(item["session_date"])
            item["created_at"] = str(item["created_at"])
            item["updated_at"] = str(item["updated_at"])
            sessions.append(item)

        return {"message": "Sesiones obtenidas exitosamente", "sessions": sessions}
    finally:
        await conn.close()


# POST /api/shooting-sessions/ - Crear una sesión de tiro
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_session(
    data: ShootingSessionCreate,
    current_user: dict = Depends(get_current_user),
):
    if data.shots_made > data.shots_attempted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Los tiros encestados no pueden superar a los intentos",
        )

    user_id = current_user["id"]
    conn = await get_db_connection()
    try:
        row = await conn.fetchrow(
            """
            INSERT INTO shooting_sessions (user_id, session_date, shots_made, shots_attempted, shot_type, notes)
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING *
            """,
            user_id,
            data.session_date,
            data.shots_made,
            data.shots_attempted,
            data.shot_type,
            data.notes,
        )
        item = dict(row)
        item["shooting_percentage"] = (
            round((item["shots_made"] / item["shots_attempted"] * 100), 2)
            if item["shots_attempted"] > 0
            else 0.0
        )
        item["session_date"] = str(item["session_date"])
        item["created_at"] = str(item["created_at"])
        item["updated_at"] = str(item["updated_at"])

        return {"message": "Sesión creada exitosamente", "session": item}
    finally:
        await conn.close()


# DELETE /api/shooting-sessions/{session_id} - Eliminar una sesión
@router.delete("/{session_id}")
async def delete_session(
    session_id: int,
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["id"]
    conn = await get_db_connection()
    try:
        row = await conn.fetchrow(
            "DELETE FROM shooting_sessions WHERE id = $1 AND user_id = $2 RETURNING id",
            session_id,
            user_id,
        )
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sesión no encontrada o no pertenece al usuario",
            )
        return {"message": "Sesión eliminada exitosamente"}
    finally:
        await conn.close()

from fastapi import APIRouter, Depends, HTTPException, status
from app.database import get_db_connection
from app.schemas import MatchCreate
from app.security import get_current_user

router = APIRouter(prefix="/api/matches", tags=["Matches & Boxscores"])


# GET /api/matches/ - Listar partidos con su boxscore
@router.get("", response_model=dict)
@router.get("/")
async def get_matches(current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    conn = await get_db_connection()
    try:
        rows = await conn.fetch(
            """
            SELECT
                m.id as match_id, m.opponent, m.match_date, m.location, m.result,
                m.team_score, m.opponent_score, m.notes,
                b.id as boxscore_id, b.minutes_played, b.points, b.rebounds,
                b.assists, b.steals, b.blocks, b.turnovers, b.fouls
            FROM matches m
            LEFT JOIN boxscores b ON m.id = b.match_id
            WHERE m.user_id = $1
            ORDER BY m.match_date DESC
            """,
            user_id,
        )

        matches = []
        for r in rows:
            item = dict(r)
            match_data = {
                "id": item["match_id"],
                "opponent": item["opponent"],
                "match_date": str(item["match_date"]),
                "location": item["location"],
                "result": item["result"],
                "team_score": item["team_score"],
                "opponent_score": item["opponent_score"],
                "notes": item["notes"],
                "boxscore": None,
            }
            if item["boxscore_id"]:
                match_data["boxscore"] = {
                    "id": item["boxscore_id"],
                    "minutes_played": item["minutes_played"],
                    "points": item["points"],
                    "rebounds": item["rebounds"],
                    "assists": item["assists"],
                    "steals": item["steals"],
                    "blocks": item["blocks"],
                    "turnovers": item["turnovers"],
                    "fouls": item["fouls"],
                }
            matches.append(match_data)

        return {"message": "Partidos obtenidos exitosamente", "matches": matches}
    finally:
        await conn.close()


# POST /api/matches/ - Crear un partido y su boxscore
@router.post("", status_code=status.HTTP_201_CREATED)
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_match(
    data: MatchCreate,
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["id"]
    conn = await get_db_connection()
    tx = conn.transaction()
    await tx.start()
    try:
        # Insertar Partido
        match_row = await conn.fetchrow(
            """
            INSERT INTO matches (user_id, opponent, match_date, location, result, team_score, opponent_score, notes)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            RETURNING *
            """,
            user_id,
            data.opponent,
            data.match_date,
            data.location,
            data.result,
            data.team_score,
            data.opponent_score,
            data.notes,
        )
        match_dict = dict(match_row)
        match_dict["match_date"] = str(match_dict["match_date"])
        match_dict["created_at"] = str(match_dict["created_at"])
        match_dict["updated_at"] = str(match_dict["updated_at"])

        # Insertar Boxscore opcional
        boxscore_dict = None
        if data.boxscore:
            box_row = await conn.fetchrow(
                """
                INSERT INTO boxscores (match_id, minutes_played, points, rebounds, assists, steals, blocks, turnovers, fouls)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                RETURNING *
                """,
                match_dict["id"],
                data.boxscore.minutes_played,
                data.boxscore.points,
                data.boxscore.rebounds,
                data.boxscore.assists,
                data.boxscore.steals,
                data.boxscore.blocks,
                data.boxscore.turnovers,
                data.boxscore.fouls,
            )
            boxscore_dict = dict(box_row)
            boxscore_dict["created_at"] = str(boxscore_dict["created_at"])
            boxscore_dict["updated_at"] = str(boxscore_dict["updated_at"])

        await tx.commit()
        match_dict["boxscore"] = boxscore_dict
        return {"message": "Partido creado exitosamente", "match": match_dict}
    except Exception as e:
        await tx.rollback()
        raise HTTPException(status_code=500, detail=f"Error creando partido: {str(e)}")
    finally:
        await conn.close()


# DELETE /api/matches/{match_id} - Eliminar un partido
@router.delete("/{match_id}")
async def delete_match(
    match_id: int,
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["id"]
    conn = await get_db_connection()
    try:
        row = await conn.fetchrow(
            "DELETE FROM matches WHERE id = $1 AND user_id = $2 RETURNING id",
            match_id,
            user_id,
        )
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Partido no encontrado o no pertenece al usuario",
            )
        return {"message": "Partido eliminado exitosamente"}
    finally:
        await conn.close()

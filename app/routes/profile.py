from fastapi import APIRouter, Depends, HTTPException, status
from app.database import get_db_connection
from app.schemas import ProfileUpdate
from app.security import get_current_user

router = APIRouter(prefix="/api/profile", tags=["Profile"])


# GET /api/profile - Obtener el perfil del usuario autenticado
@router.get("/")
async def get_profile(current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    conn = await get_db_connection()
    try:
        profile = await conn.fetchrow(
            "SELECT * FROM user_profiles WHERE user_id = $1", user_id
        )
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Perfil no encontrado para este usuario",
            )

        profile_dict = dict(profile)
        profile_dict["created_at"] = (
            str(profile_dict["created_at"]) if profile_dict.get("created_at") else None
        )
        profile_dict["updated_at"] = (
            str(profile_dict["updated_at"]) if profile_dict.get("updated_at") else None
        )

        return {"message": "Perfil obtenido exitosamente", "profile": profile_dict}
    finally:
        await conn.close()


# PUT /api/profile - Crear o actualizar el perfil del usuario autenticado
@router.put("/")
async def update_profile(
    profile_data: ProfileUpdate, current_user: dict = Depends(get_current_user)
):
    user_id = current_user["id"]
    conn = await get_db_connection()
    try:
        # Verificar si el perfil existe
        existing_profile = await conn.fetchrow(
            "SELECT id FROM user_profiles WHERE user_id = $1", user_id
        )

        if existing_profile:
            # Actualizar perfil existente
            updated_profile = await conn.fetchrow(
                """
                UPDATE user_profiles SET
                    full_name = COALESCE($1, full_name),
                    height_cm = COALESCE($2, height_cm),
                    weight_kg = COALESCE($3, weight_kg),
                    wingspan_cm = COALESCE($4, wingspan_cm),
                    position = COALESCE($5, position),
                    club = COALESCE($6, club),
                    league = COALESCE($7, league),
                    updated_at = NOW()
                WHERE user_id = $8
                RETURNING *
                """,
                profile_data.full_name,
                profile_data.height_cm,
                profile_data.weight_kg,
                profile_data.wingspan_cm,
                profile_data.position,
                profile_data.club,
                profile_data.league,
                user_id,
            )
            msg = "Perfil actualizado exitosamente"
        else:
            # Insertar nuevo perfil
            updated_profile = await conn.fetchrow(
                """
                INSERT INTO user_profiles (
                    user_id, full_name, height_cm, weight_kg, wingspan_cm, position, club, league, created_at, updated_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, NOW(), NOW())
                RETURNING *
                """,
                user_id,
                profile_data.full_name,
                profile_data.height_cm,
                profile_data.weight_kg,
                profile_data.wingspan_cm,
                profile_data.position,
                profile_data.club,
                profile_data.league,
            )
            msg = "Perfil creado exitosamente"

        profile_dict = dict(updated_profile)
        profile_dict["created_at"] = (
            str(profile_dict["created_at"]) if profile_dict.get("created_at") else None
        )
        profile_dict["updated_at"] = (
            str(profile_dict["updated_at"]) if profile_dict.get("updated_at") else None
        )

        return {"message": msg, "profile": profile_dict}
    finally:
        await conn.close()

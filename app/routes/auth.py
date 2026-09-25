from fastapi import APIRouter, HTTPException, status
from app.database import get_db_connection
from app.schemas import UserRegister, UserLogin, TokenResponse
from app.security import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister):
    conn = await get_db_connection()
    try:
        # Verificar si el email ya existe
        existing_user = await conn.fetchrow(
            "SELECT id FROM users WHERE email = $1", user_data.email
        )
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El correo electrónico ya está registrado",
            )

        # Hashear la contraseña
        hashed_pwd = hash_password(user_data.password)

        # Insertar nuevo usuario
        new_user = await conn.fetchrow(
            "INSERT INTO users (email, password) VALUES ($1, $2) RETURNING id, email, created_at",
            user_data.email,
            hashed_pwd,
        )

        return {
            "message": "Usuario registrado exitosamente",
            "user": {
                "id": new_user["id"],
                "email": new_user["email"],
                "created_at": str(new_user["created_at"]),
            },
        }
    finally:
        await conn.close()


@router.post("/login", response_model=TokenResponse)
async def login(user_data: UserLogin):
    conn = await get_db_connection()
    try:
        # Buscar usuario por email
        user = await conn.fetchrow(
            "SELECT * FROM users WHERE email = $1", user_data.email
        )
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales inválidas",
            )

        # Verificar la contraseña
        if not verify_password(user_data.password, user["password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales inválidas",
            )

        # Generar Token JWT
        token_data = {"id": user["id"], "email": user["email"]}
        access_token = create_access_token(data=token_data)

        return {
            "message": "Autenticación exitosa",
            "token": access_token,
            "user": {"id": user["id"], "email": user["email"]},
        }
    finally:
        await conn.close()

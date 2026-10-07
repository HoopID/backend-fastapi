from datetime import date
from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class UserRegister(BaseModel):
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    message: str
    token: str
    user: dict


class ProfileBase(BaseModel):
    full_name: Optional[str] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    wingspan_cm: Optional[float] = None
    position: Optional[str] = None
    club: Optional[str] = None
    league: Optional[str] = None


class ProfileUpdate(ProfileBase):
    pass


class ProfileResponse(ProfileBase):
    id: int
    user_id: int
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


# Esquemas para Sesiones de Tiro
class ShootingSessionCreate(BaseModel):
    session_date: date
    shots_made: int = Field(..., ge=0)
    shots_attempted: int = Field(..., ge=0)
    shot_type: Optional[str] = "General"
    notes: Optional[str] = None


class ShootingSessionResponse(BaseModel):
    id: int
    user_id: int
    session_date: str
    shots_made: int
    shots_attempted: int
    shooting_percentage: float
    shot_type: str
    notes: Optional[str] = None
    created_at: str
    updated_at: str


# Esquemas para Partidos y Boxscores
class BoxscoreSchema(BaseModel):
    minutes_played: Optional[int] = Field(0, ge=0)
    points: Optional[int] = Field(0, ge=0)
    rebounds: Optional[int] = Field(0, ge=0)
    assists: Optional[int] = Field(0, ge=0)
    steals: Optional[int] = Field(0, ge=0)
    blocks: Optional[int] = Field(0, ge=0)
    turnovers: Optional[int] = Field(0, ge=0)
    fouls: Optional[int] = Field(0, ge=0, le=5)


class MatchCreate(BaseModel):
    opponent: str
    match_date: date
    location: Optional[str] = None
    result: Optional[str] = None
    team_score: Optional[int] = None
    opponent_score: Optional[int] = None
    notes: Optional[str] = None
    boxscore: Optional[BoxscoreSchema] = None

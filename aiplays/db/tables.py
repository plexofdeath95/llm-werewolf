"""SQLAlchemy tables for game analysis (player LLM histories live in ADK's own DB)."""
from typing import Any

from sqlalchemy import JSON, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class GameRow(Base):
    __tablename__ = "games"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    mode: Mapped[str] = mapped_column(String, index=True)
    seed: Mapped[int] = mapped_column(Integer)
    config: Mapped[dict[str, Any]] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String, default="running")
    winner: Mapped[str | None] = mapped_column(String, nullable=True)
    rounds: Mapped[int] = mapped_column(Integer, default=0)
    cost_usd: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[float] = mapped_column(Float)
    ended_at: Mapped[float | None] = mapped_column(Float, nullable=True)


class PlayerRow(Base):
    __tablename__ = "game_players"
    game_id: Mapped[str] = mapped_column(ForeignKey("games.id"), primary_key=True)
    player_id: Mapped[str] = mapped_column(String, primary_key=True)
    seat: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String)
    model_id: Mapped[str] = mapped_column(String, index=True)
    slug: Mapped[str] = mapped_column(String)
    persona: Mapped[str | None] = mapped_column(Text, nullable=True)
    role: Mapped[str] = mapped_column(String)
    team: Mapped[str] = mapped_column(String)
    alive: Mapped[bool] = mapped_column(default=True)
    died_round: Mapped[int | None] = mapped_column(Integer, nullable=True)
    death_cause: Mapped[str | None] = mapped_column(String, nullable=True)


class EventRow(Base):
    __tablename__ = "game_events"
    game_id: Mapped[str] = mapped_column(ForeignKey("games.id"), primary_key=True)
    seq: Mapped[int] = mapped_column(Integer, primary_key=True)
    round: Mapped[int] = mapped_column(Integer)
    phase: Mapped[str] = mapped_column(String)
    kind: Mapped[str] = mapped_column(String, index=True)
    actor: Mapped[str | None] = mapped_column(String, nullable=True)
    target: Mapped[str | None] = mapped_column(String, nullable=True)
    text: Mapped[str] = mapped_column(Text)
    data: Mapped[dict[str, Any]] = mapped_column(JSON)
    visible_to: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    ts: Mapped[float] = mapped_column(Float)

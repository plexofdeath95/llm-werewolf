"""Benchmark queries per model, built on the ORM tables (shared by scripts/stats.py and the API)."""
from sqlalchemy import Select, case, desc, func, select
from sqlalchemy.orm import aliased

from aiplays.db.repo import Repo
from aiplays.db.tables import EventRow as E
from aiplays.db.tables import GameRow as G
from aiplays.db.tables import PlayerRow as P

T = aliased(P)  # the vote target's seat


def _scope(include_fake: bool) -> list:
    where = [G.status == "finished"]
    return where if include_fake else where + [G.config["fake"].as_boolean().is_(False)]


def _pct(expr, label: str):
    return func.round(func.avg(expr) * 100, 1).label(label)


def win_rate(fake: bool) -> Select:
    return (select(P.model_id, func.count().label("seats"), _pct(P.won, "win_pct"),
                   _pct(P.alive, "survived_pct"))
            .join(G, G.id == P.game_id).where(*_scope(fake))
            .group_by(P.model_id).order_by(desc("win_pct")))


def win_by_team(fake: bool) -> Select:
    return (select(P.model_id, P.team, func.count().label("seats"), _pct(P.won, "win_pct"))
            .join(G, G.id == P.game_id).where(*_scope(fake))
            .group_by(P.model_id, P.team).order_by(P.model_id, P.team))


def _day_votes(fake: bool):
    return (select().select_from(E).join(G, G.id == E.game_id)
            .join(P, (P.game_id == E.game_id) & (P.player_id == E.actor))
            .join(T, (T.game_id == E.game_id) & (T.player_id == E.target))
            .where(E.kind == "vote", E.phase == "vote", *_scope(fake)))


def vote_accuracy(fake: bool) -> Select:
    return (_day_votes(fake).add_columns(P.model_id, func.count().label("votes"),
                                         _pct(T.team == "wolves", "hit_wolf_pct"))
            .where(P.team == "village").group_by(P.model_id).order_by(desc("hit_wolf_pct")))


def wolf_deception(fake: bool) -> Select:
    seats = func.count(func.distinct(T.game_id + T.player_id))
    return (_day_votes(fake).add_columns(T.model_id, seats.label("wolf_seats"),
                                         func.round(func.count() * 1.0 / seats, 2)
                                         .label("votes_against_per_seat"))
            .where(T.team == "wolves").group_by(T.model_id).order_by("votes_against_per_seat"))


def _per_actor(fake: bool, *cols) -> Select:
    return (select(P.model_id, *cols).select_from(E).join(G, G.id == E.game_id)
            .join(P, (P.game_id == E.game_id) & (P.player_id == E.actor))
            .where(*_scope(fake)).group_by(P.model_id))


def talk(fake: bool) -> Select:
    speech = E.kind == "speech"
    return _per_actor(
        fake, func.sum(case((speech, 1), else_=0)).label("messages"),
        func.sum(case((speech & E.data["interrupt"].as_boolean().is_(True), 1), else_=0))
        .label("interrupts"),
        func.round(func.avg(E.data["urgency"].as_float()), 2).label("avg_urgency"),
    ).where(E.kind.in_(["speech", "reaction"])).order_by(desc("messages"))


def cost(fake: bool) -> Select:
    return _per_actor(
        fake, func.count().label("calls"),
        func.round(func.sum(E.data["cost"].as_float()), 4).label("usd"),
        func.round(func.avg(E.data["latency"].as_float()), 2).label("avg_latency_s"),
    ).where(E.kind == "thought").order_by(desc("usd"))


REPORTS = {
    "Win rate & survival by model": win_rate,
    "Win rate by model and team": win_by_team,
    "Village vote accuracy (day votes on real wolves)": vote_accuracy,
    "Wolf deception (day votes received per wolf seat)": wolf_deception,
    "Talk: messages, interrupts, urgency": talk,
    "Cost & latency per call": cost,
}


async def report(repo: Repo, include_fake: bool = False) -> dict[str, dict]:
    out = {}
    async with repo.session() as s:
        for title, build in REPORTS.items():
            res = await s.execute(build(include_fake))
            out[title] = {"columns": list(res.keys()), "rows": [list(r) for r in res.all()]}
    return out

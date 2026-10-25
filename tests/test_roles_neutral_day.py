"""Neutral day hooks, deaths and win conditions (with a tiny scripted moderator)."""
import random

from rolekit import act, game, night, run

from aiplays.modes.werewolf import win
from aiplays.modes.werewolf.roles.base import ROLES
from aiplays.modes.werewolf.status import status


class FakeMod:
    def __init__(self, st, pick: str | None = None):
        self.state, self.pick, self.rng, self.events = st, pick, random.Random(0), []

    async def ask(self, p, question, schema, *, fallback, deep=False, choices=None):
        return schema(target=self.pick) if self.pick else fallback

    async def kill(self, p, cause, text, *, narrate=False):
        p.alive, p.death_cause = False, cause

    async def emit(self, kind, text="", **kw):
        self.events.append(text)


def hook(p, name):
    return ROLES[p.role].hook(name)


async def test_jester_wins_on_the_noose_and_takes_a_voter():
    st = game("jester", "villager", "villager", "villager", "villager")
    jest, ben, cat = st.players[:3]
    assert await hook(jest, "on_lynched")(FakeMod(st, "Ben"), jest, [ben, cat]) is False
    assert not ben.alive and cat.alive
    assert win.winners(st, "village") == ["p0", "p1", "p2", "p3", "p4"]  # jester co-wins


async def test_prophet_counts_a_marked_lynch_and_a_marked_night_death():
    st = game("maligned_prophet", "villager", "villager", "villager", "villager")
    pro, ben, cat = st.players[:3]
    st.round = 1
    await hook(pro, "day_action")(FakeMod(st, "Ben"), pro)
    await hook(pro, "after_lynch")(FakeMod(st), pro, ben, [])
    st.round = 2
    await hook(pro, "day_action")(FakeMod(st, "Cat"), pro)
    n = night(st, 3)
    n.deaths[cat.id] = "killed"
    hook(pro, "after_night")(n, pro)
    assert status(st, pro).marks["seen"] == 2 and hook(pro, "win")(st, pro, "village")


async def test_executioner_and_assassin_score_through_the_vote():
    st = game("executioner", "assassin", "villager", "villager", "villager", "villager")
    exe, ass = st.players[:2]
    target = st.by_id(status(st, ass).marks["targets"][0])
    status(st, exe).marks["target"] = target.id
    await hook(exe, "after_lynch")(FakeMod(st), exe, target, [ass])
    await hook(ass, "after_lynch")(FakeMod(st), ass, target, [ass])
    assert hook(exe, "win")(st, exe, "wolves")
    assert target.id in status(st, ass).marks["done"]


async def test_cult_leader_takeover_and_collapse():
    st = game("cult_leader", "villager", "alpha", "villager", "villager")
    for p in st.players[1:]:
        status(st, p).flags.add("cult")
    assert win.winner(st) == "neutral" and len(win.winners(st, "neutral")) == 5
    await hook(st.players[0], "on_death")(FakeMod(st), st.players[0])
    assert not any(p.alive for p in st.players[1:])


def test_munitions_bomb_kills_visitors_then_the_finale():
    st = game("munitions_expert", "doctor", "doctor", "villager", "villager")
    bomber, d1, d2 = st.players[:3]
    act(n := night(st, 1), bomber, "plant", st.players[3])
    act(n, d1, "heal", st.players[3])
    act(n, d2, "heal", st.players[3])
    assert set(run(n).deaths) == {d1.id, d2.id} and status(st, bomber).kills == 2
    st.players[4].role = "doctor"
    act(n := night(st, 2), bomber, "plant", bomber)
    act(n, st.players[4], "heal", bomber)
    run(n)
    assert bomber.id in n.deaths and hook(bomber, "win")(st, bomber, "village")


def test_hostile_neutral_last_standing_wins():
    st = game("arsonist", "villager", "villager", "villager", "villager")
    for p in st.players[2:]:
        p.alive = False
    assert win.winner(st) == "neutral" and win.winners(st, "neutral") == ["p0"]

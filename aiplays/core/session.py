"""GameSession: builds a game from config and runs it as a background task."""
import asyncio
import logging
import random
import uuid

from aiplays.agents.factory import build_agents, build_narrator
from aiplays.agents.pricing import load_prices
from aiplays.core.bus import EventBus
from aiplays.core.config import GameConfig
from aiplays.core.events import Kind
from aiplays.core.gate import Budget, Gate
from aiplays.core.mode import get_mode
from aiplays.core.moderator import Moderator
from aiplays.core.state import GameState, Player
from aiplays.db.repo import Repo
from aiplays.settings import get_catalog

log = logging.getLogger(__name__)


class GameSession:
    def __init__(self, cfg: GameConfig, repo: Repo):
        self.id, self.cfg, self.repo = uuid.uuid4().hex[:12], cfg, repo
        self.mode = get_mode(cfg.mode)
        seed = cfg.seed if cfg.seed is not None else random.randrange(1_000_000)
        rng = random.Random(seed)
        seats = list(cfg.seats)
        rng.shuffle(seats)  # models don't cluster around the table
        names = get_catalog().player_names
        players = [Player(id=f"p{i}", name=s.name or names[i], seat=i, model_id=s.model_id,
                          persona=s.persona) for i, s in enumerate(seats)]
        self.state = GameState(game_id=self.id, mode=cfg.mode, seed=seed, players=players)
        self.mode.assign_roles(self.state, rng, cfg.deck)
        self.bus = EventBus(self.id, sink=repo.add_event)
        self.gate, self.budget = Gate(), Budget(cfg.max_cost_usd)
        self.task: asyncio.Task | None = None

    async def start(self) -> None:
        if not self.cfg.fake:
            await load_prices()
        await self.repo.create_game(self.state, self.cfg)
        self.mod = Moderator(state=self.state, mode=self.mode, config=self.cfg,
                             agents=build_agents(self.state, self.mode, self.cfg),
                             bus=self.bus, gate=self.gate, budget=self.budget,
                             narrator=build_narrator(self.state, self.cfg))
        cat = get_catalog()
        await self.mod.emit(Kind.SETUP, f"{self.mode.name}: {len(self.state.players)} players",
                            data={"mode": self.mode.describe(), "seed": self.state.seed,
                                  "players": [{**vars(p), "model": cat.get(p.model_id).model_dump()}
                                              for p in self.state.players]})
        self.task = asyncio.create_task(self._run())

    async def _run(self) -> None:
        status = "finished"
        try:
            self.state.winner = await self.mode.play(self.mod)
            await self.mod.emit(Kind.GAME_OVER, f"The {self.state.winner} win!", data={
                "winner": self.state.winner, "cost": self.budget.spent,
                "roles": {p.id: p.role for p in self.state.players}})
        except asyncio.CancelledError:
            status = "cancelled"
            raise
        except Exception as e:
            status = "error"
            log.exception("game %s crashed", self.id)
            await self.mod.emit(Kind.ERROR, f"Game crashed: {e}")
        finally:
            await self.repo.finish_game(self.state, status, self.budget.spent)

    def control(self, action: str, amount: float = 5.0) -> None:
        if action == "pause":
            self.gate.pause()
        elif action == "resume":
            self.gate.resume()
        elif action == "step":
            self.gate.step()
        elif action == "raise_budget":
            self.budget.raise_cap(amount)
            self.gate.resume()

    @property
    def running(self) -> bool:
        return self.task is not None and not self.task.done()

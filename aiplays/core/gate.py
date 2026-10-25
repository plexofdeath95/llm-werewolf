"""Gate (pause / resume / step between LLM rounds) and Budget (per-game cost cap)."""
import asyncio


class Gate:
    def __init__(self) -> None:
        self._open = asyncio.Event()
        self._open.set()
        self._stepping = False

    @property
    def paused(self) -> bool:
        return not self._open.is_set()

    def pause(self) -> None:
        self._open.clear()

    def resume(self) -> None:
        self._stepping = False
        self._open.set()

    def step(self) -> None:
        """Let exactly one more round through, then pause again."""
        self._stepping = True
        self._open.set()

    async def wait(self) -> None:
        await self._open.wait()
        if self._stepping:
            self._open.clear()


class Budget:
    def __init__(self, max_usd: float):
        self.max_usd = max_usd
        self.spent = 0.0
        self._warned_at = 0.0

    def add(self, usd: float) -> bool:
        """Record spend; True when the cap was just crossed (caller should pause)."""
        self.spent += usd
        if self.spent >= self.max_usd and self._warned_at < self.max_usd:
            self._warned_at = self.max_usd
            return True
        return False

    def raise_cap(self, extra_usd: float) -> None:
        self.max_usd += extra_usd

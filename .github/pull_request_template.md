## What this changes

<!-- One or two sentences. Link an issue if there is one. -->

## Type

- [ ] Bug fix
- [ ] New role, game mode or model
- [ ] UI
- [ ] Shared games (files in `community/games/` only)
- [ ] Docs or tooling

## Checklist

- [ ] `uv run pytest` passes (offline, no API key needed)
- [ ] Every `.py`, `.ts` and `.tsx` file is at most 100 lines
- [ ] Existing modules are reused rather than duplicated (see CONTRIBUTING.md)
- [ ] Shared code stays game-agnostic; game rules live in `aiplays/modes/<mode>/`
- [ ] `cd frontend && npm run build` passes, if the frontend changed
- [ ] No `.env`, `data/`, API keys or music files are committed

## For shared games

- Models used:
- Rules, prompts, decks or speech style changed from the defaults:

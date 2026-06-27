# Invaders

A browser-ready shoot 'em up arcade game built with
[pygame](https://www.pygame.org). The game logic is plain Python and the main
loop is `async`, so the **same code runs both natively and in a web browser**
when compiled to WebAssembly with [pygbag](https://pypi.org/project/pygbag/).

---

## Play it online

**[Play on GitHub Pages >>](https://theericho.github.io/space_game_pygame/)**

---

## Controls

| Key | Action |
|-----|--------|
| **A** / **D** or **←** / **→** | Move the ship left / right |
| **Spacebar** | Fire a laser bolt |
| **S** | Start the game / continue after a death / play again |
| **P** | Pause / resume |
| **M** | Mute / unmute sound effects |
| **Esc** | Quit (desktop only) |

Clear every alien to advance to the next, faster wave. You have 3 lives — you
lose one when an alien bolt hits your ship, and the game ends if you run out of
lives or any alien reaches the defensive line.

---

## Run it natively (desktop)

```bash
pip install pygame
python main.py
```

Run this from **inside** the `space_game_pygame` folder so it can find the
`Images`, `Sounds`, and `Fonts` directories.

---

## Run it in a browser (locally hosted)

The game is packaged for the web with **pygbag**, which compiles it to
WebAssembly and serves it on a local web server.

```bash
pip install pygbag

# from the PARENT directory (the one containing space_game_pygame/):
python -m pygbag space_game_pygame
```

Then open the URL it prints (default <http://localhost:8000>) in your browser.

Notes:
- The entry point **must** be `main.py` with the `asyncio.run(main())` call —
  pygbag looks for it. That's already set up.
- Browsers only start audio after the first user interaction, so sound effects
  begin once you press a key (e.g. **S** to start).
- First load downloads the Python/WASM runtime (a few MB); afterwards it is
  cached.

### Rebuilding after code changes

```bash
python -m pygbag --build space_game_pygame      # rebuilds build/web/
cp build/web/index.html build/web/favicon.png \
   build/web/space_game_pygame.apk build/web/space_game_pygame.tar.gz docs/
```

Then commit `docs/` and push.



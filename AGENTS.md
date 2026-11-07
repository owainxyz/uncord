# AGENTS.md

Notes for AI coding agents (and people) working on uncord. Read this before changing anything.

## What this is

uncord is a Discord client for the terminal, written in Python on [discord.py-self](https://github.com/dolfies/discord.py-self) and [Textual](https://github.com/Textualize/textual), with hot paths in C and C++. It logs in as a user account. Linux only.

## Setup, build and run

```sh
python3 -m venv .venv && .venv/bin/pip install -e .
.venv/bin/python setup.py build_ext --inplace     # after editing _dsp.cpp or _rtp.cpp
.venv/bin/python setup.py build_rust --inplace --release   # after editing rust/ (pip install setuptools-rust, needs cargo)
.venv/bin/python -m uncord                         # run it (needs a Discord login)
.venv/bin/python -m uncord --doctor                # check ffmpeg, opus, chafa, mpv and so on
```

## Checks before you finish

```sh
.venv/bin/python -m unittest discover -s tests -t .   # the Opus tests skip if libopus isn't found (set UNCORD_OPUS)
pyflakes uncord tests
.venv/bin/python bench/render.py                   # rendering must not get slower
.venv/bin/python bench/opus.py                     # nor voice decoding
.venv/bin/python bench/picker.py                   # nor picker search
```

Tests run offline and never log in. Don't start the real app against someone's account to test a change; test the function directly, or drive a screen with Textual's `run_test` and a stub app.

## Layout

| Path | What's there |
| --- | --- |
| `uncord/app.py` | Main window, sidebar, chat, Discord event handlers, sending messages |
| `uncord/fmt.py` | Markdown and message rendering (Rich `Text`), link hints |
| `uncord/messages.py` | Message list and message widgets |
| `uncord/settings.py` | Settings screen (tabs, plugin switches and plugin options) |
| `uncord/plugins.py` | Plugin registry (`PLUGINS`) and the pure helpers plugins use |
| `uncord/commands.py` | Built-in slash commands and the F1 help text |
| `uncord/safety.py` | Control-character stripping, link checks, lookalike hosts, log scrubbing, file permissions |
| `uncord/config.py` | `config.json` defaults and loading |
| `uncord/voice.py`, `calls.py`, `golive.py`, `rtpvideo.py`, `streamview.py` | Voice, calls, screen sharing, video |
| `uncord/media.py`, `sixelview.py` | Image and video fetching, frame cache, terminal graphics |
| `uncord/_dsp.cpp` | Opus decoding, voice volume, mixing, levels, call sounds |
| `uncord/_rtp.cpp` | Video depacketizers, jitter buffer, RTCP, outgoing packets |
| `rust/` | `uncord._fast` (Rust, PyO3): message markdown (`md.rs`), picker search (`lib.rs`), sixel, Kitty chunks, PPM frames, H.264 and RTP parsing (`native.rs`). Required. New code that parses data from other people goes here. When porting something from Python, keep a test comparing the results with the old Python version |
| `uncord/icons.py` | Button and menu icons: Nerd Font glyphs with emoji fallbacks. Use `icon("name")` instead of writing emoji into the UI. The server and DM sidebar stays plain text |
| `uncord/snapshot.py` | The copy of the last chat and sidebar drawn at startup before Discord connects |
| `tests/` | `unittest` tests |
| `bench/` | Benchmarks |
| `packaging/` | AUR and Nix packages |

## Code style

- camelCase for functions, methods and variables. Config keys stay snake_case so old config files keep working
- Very few comments, written as `#lowercase and short`, only where the code can't explain itself. No docstrings
- Match the surrounding code; don't reformat files you aren't changing
- The server and DM sidebar stays plain text: no avatars, icons or images there

## Safety rules

- Never put text from Discord (names, messages, embeds) into Textual markup. Use `rich.text.Text`, or pass `markup=False` to `notify` and `Static`. A raw string with `[` in it can break or inject markup
- Run untrusted text through `safety.clean` before it reaches the terminal
- Open links only through `openExternal`, which checks `safety.safeUrl` and `safety.lookalike`
- Media loads only from Discord's servers (`media.fetch`), with the size cap
- The token must never reach the log, the environment of child processes or any file other than the token file

## Plugins

A plugin is one row in `PLUGINS` in `plugins.py`: `(key, Name, description, onByDefault)`. Put the logic in a pure function in `plugins.py` and add a test for it, then check `self.plugin("key")` where it applies in the app. Plugins are set up in **Settings → Plugins**, not with slash commands; options go in `SettingsScreen.PLUGIN_INPUTS` and their config keys go in `config.DEFAULTS`.

## Versions and releases

- The version lives only in `uncord/__init__.py`, always with two digits after the dot (`0.90`, then `0.91`; `0.9` would sort before `0.80`). A letter suffix like `0.90a` is for fix-only updates
- Bump it with every change that ships, and add a section to the top of `CHANGELOG.md`
- Changelog entries are plain sentences about what users notice, no trailing full stops, newest first
- A release is a `vX.YY` tag, a GitHub release with that changelog section, and updated `pkgver` and `sha256sums` in `packaging/aur/uncord/PKGBUILD`
- No GitHub Actions or other CI in this repo
- Commits and releases carry no AI attribution lines (`Co-Authored-By`, "Generated with …")

## Writing docs

README and changelog are written in plain, friendly English: short sentences, second person, no marketing words. Show the key or command, then say what it does.

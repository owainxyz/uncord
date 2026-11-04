# uncord

Discord in your terminal: servers, DMs, voice and video calls, images and GIFs, and screen sharing both ways. It logs in as your own account, so everything you see in the official app is here too.

Questions or ideas? Join the [uncord Discord server](https://discord.gg/fubfK8C6Cm).

> [!WARNING]
> Discord's terms don't allow third-party clients on user accounts. Plenty of people use them anyway, but your account could get flagged. Use it at your own risk.

## Contents

1. [Features](#features)
2. [Install](#install)
   - [Requirements](#requirements)
   - [Install script](#install-script)
   - [Nix](#nix)
   - [By hand](#by-hand)
   - [Updating and uninstalling](#updating-and-uninstalling)
3. [Getting started](#getting-started)
   - [Logging in](#logging-in)
   - [Files](#files)
   - [Environment variables](#environment-variables)
4. [Using uncord](#using-uncord)
   - [Keys](#keys)
   - [Voice, video and screen sharing](#voice-video-and-screen-sharing)
   - [Settings and plugins](#settings-and-plugins)
5. [Privacy and security](#privacy-and-security)
6. [Troubleshooting](#troubleshooting)
7. [For developers](#for-developers)
8. [Todo](#todo)
9. [Credits and license](#credits-and-license)

## Features

| | |
| --- | --- |
| **Chat** | servers, DMs, group DMs, threads and forums. Replies, edits, reactions, pins, search, and unread and mention counts |
| **Looks like Discord** | markdown and highlighted code, embeds, server tags, blurple APP badges, 🖥 📱 🌐 device icons and a members list |
| **Images** | pictures, GIFs, stickers and custom emoji. Sharpest in Kitty and Ghostty, sixel in foot, WezTerm, Konsole and others |
| **Voice and video** | per-person volume, automatic gain and mic sensitivity, your camera on or other people's cameras in view |
| **Screen sharing** | go live with one key, or watch someone else's stream right in the terminal |
| **Extras** | an inbox for unreads and mentions, bot slash commands, voice messages, Rich Presence for your games, and 25 plugins such as MessageLogger and ClearURLs |
| **Encryption** | calls and streams use Discord's DAVE end-to-end encryption, like the official app |
| **Fast** | the busiest code is compiled: image and video packets in C, voice mixing and levels in C++ |

## Install

### Requirements

- Linux (x86_64 or ARM, glibc or musl) with Python 3.10 or newer
- **To build:** gcc, g++ and the Python headers
- **For voice:** ffmpeg, libopus and PipeWire
- **Optional:** chafa (nicer images), mpv (pop-out video), wl-clipboard or xclip (pasting images), a notification daemon, gpu-screen-recorder (screen sharing and camera)

The install script and Nix sort these out for you.

### Install script

Works on Debian, Ubuntu, Fedora, Arch, openSUSE, Void, Alpine and Gentoo.

```sh
git clone https://github.com/owainxyz/uncord.git
cd uncord
./install.sh
```

It installs the system packages with your package manager (it asks first), puts uncord in `~/.local/share/uncord`, adds an `uncord` command and an app menu entry, then runs `uncord --doctor`.

| Flag | Does |
| --- | --- |
| `-y` | install without asking |
| `--no-system` | skip system packages |
| `--dry-run` | show what it would do |
| `--uninstall` | remove uncord (keeps your login and settings) |

### Nix

```sh
nix run github:owainxyz/uncord              # try it
nix profile install github:owainxyz/uncord  # install it
```

On NixOS, add the flake to your system with `inputs.uncord.url = "github:owainxyz/uncord";`, then add `uncord.packages.${system}.default` to your packages. uncord isn't in nixpkgs yet, so `nix-env -iA nixpkgs.uncord` won't find it.

### By hand

Install the [requirements](#requirements) first, then:

```sh
python3 -m venv ~/.local/share/uncord/venv
~/.local/share/uncord/venv/bin/pip install .
~/.local/share/uncord/venv/bin/uncord
```

### Updating and uninstalling

- **Update:** `uncord --update`. uncord also tells you when an update is out.
- **Uninstall:** `./install.sh --uninstall`. Your login and settings stay in `~/.config/uncord`.

## Getting started

### Logging in

The first time you run `uncord` it asks how to log in:

1. **QR code:** scan it with the Discord app on your phone (Settings → Scan QR Code). No password needed.
2. **Token:** paste one if you already have it.

| Command | Does |
| --- | --- |
| `uncord --login` | log in again |
| `uncord --logout` | forget your login |
| `uncord --doctor` | check what uncord found and what's missing |
| `uncord --env` | list every environment variable |

### Files

All of these are readable only by you.

| Path | What's in it |
| --- | --- |
| `~/.config/uncord/token` | your login |
| `~/.config/uncord/config.json` | settings |
| `~/.config/uncord/env` | optional environment variables |
| `~/.cache/uncord/uncord.log` | the log |

### Environment variables

Instead of the saved token you can set `UNCORD_TOKEN` (or `DISCORD_TOKEN`), or `UNCORD_TOKEN_CMD` to a command that prints it, like `pass show discord/token`. Folders, the log, theme, voice gate and tool paths have variables too. `uncord --env` lists them all.

They can also go in `~/.config/uncord/env` as `KEY=value` lines (see `uncord.env.example`). Real environment variables win over the file, and only uncord's own keys are read from it.

## Using uncord

### Keys

Press **F1** in uncord for the full list. Slash commands work too: type `/` to see them, including bot commands.

| Key | Does |
| --- | --- |
| **Moving around** | |
| Ctrl+K | jump to any chat, person or server |
| Tab / Esc | move between the message box and the sidebar |
| Alt+↑ / Alt+↓ | previous / next channel |
| Ctrl+B / F2 | sidebar / members list |
| F3 or ⚙ | settings |
| F4 | inbox |
| **Messages** | |
| ↑ in an empty message box | select messages: `r` reply, `e` edit, `d` delete, `+` react |
| Ctrl+G / Ctrl+E / Ctrl+T | GIFs, emoji, stickers |
| Ctrl+O | attach a file or record a voice message |
| Ctrl+F | search |
| **Calls** | |
| F5 / F6 / F7 / F8 | call, mute, deafen, leave |
| F9 | voice & video settings |
| F10 / F11 / F12 | share screen, watch a stream, camera |

### Voice, video and screen sharing

Click a voice channel to join, or press F5 in a DM to call. Click someone's name in the call bar to change their volume. Devices, volume and mic sensitivity are in **Settings → Voice & video** (F9).

| | |
| --- | --- |
| **Share your screen (F10)** | needs `gpu-screen-recorder`. On GNOME or KDE Wayland, pick "portal". Change the quality with `/share 1080p60` |
| **Camera (F12)** | turns your webcam on in the call |
| **Watch (F11)** | when someone goes live their name gets a red LIVE tag. In the viewer, `+`/`-` resize, `f` is full size, `p` opens it in mpv, `m` mutes and `esc` closes |

### Settings and plugins

Open settings with the ⚙ button by your name, F3 or `/settings`. Changes apply straight away.

| Tab | What's there |
| --- | --- |
| Appearance | theme, line spacing, images, layout, stream size |
| Notifications | desktop notifications, message previews |
| Chat | DM list size, translation language, file picker |
| Voice & video | devices, volumes, mic sensitivity, call sounds, screen share quality, camera |
| Privacy | link safety, Rich Presence, log out |
| Plugins | 25 Vencord-style extras, searchable |
| About | version, updates, what's installed |

## Privacy and security

**Your terminal**
- Messages, names and embeds can't send escape sequences to your terminal (things like clipboard writes or title changes). They're stripped before anything is drawn.

**Links and media**
- Masked links show where they really go, and a ⚠ when the text claims a different site.
- Only http and https links open in your browser. You can have uncord ask first.
- Images, videos and voice messages only load from Discord's servers (through its image proxy), so a link in an embed can't see your IP. Downloads are capped at 64 MB, and ffmpeg and mpv only get https links.

**Your token**
- It never goes into the log, not even inside error tracebacks.
- It's removed from uncord's environment once read, so ffmpeg, mpv, the voice helpers and anything else uncord starts never see it.
- A token or env file that's a symlink, belongs to another user or isn't a plain file is refused. Tokens with spaces or odd characters are refused too.
- `uncord --logout` overwrites the token file before deleting it.

**Rich Presence**
- The socket only accepts your own apps and drops oversized or malformed messages.

See [SECURITY.md](SECURITY.md) to report a problem.

## Troubleshooting

Run `uncord --doctor` first. It shows what uncord found and what's missing.

| Problem | Fix |
| --- | --- |
| `uncord: command not found` right after installing | open a new terminal. The installer puts `~/.local/bin` on your PATH, but terminals that were already open don't see it. `~/.local/bin/uncord` works straight away |
| Blocky images | your terminal can't draw images. Try Kitty, Ghostty, foot, WezTerm or Konsole |
| No sound or nobody hears you | pick the right devices in Settings → Voice & video. `/voicestats` shows what the audio is doing |
| Screen share fails | check `gpu-screen-recorder --list-monitors`, or use the portal option |
| uncord can't find a tool | point it there with `UNCORD_FFMPEG`, `UNCORD_OPUS`, `UNCORD_CHAFA` or `UNCORD_GSR` |
| Anything else | check `~/.cache/uncord/uncord.log`, or ask in the [Discord server](https://discord.gg/fubfK8C6Cm) |

## For developers

```sh
python3 -m venv .venv && .venv/bin/pip install -e .
.venv/bin/python setup.py build_ext --inplace   # rebuild after editing _native.c, _dsp.cpp or _rtp.cpp
.venv/bin/python -m uncord
```

| Path | What's in it |
| --- | --- |
| `uncord/app.py` | main window, sidebar, chat and Discord events |
| `uncord/settings.py` | the settings tabs |
| `uncord/voice.py`, `golive.py`, `rtpvideo.py` | calls, screen sharing and video |
| `uncord/fmt.py`, `messages.py` | turning messages into terminal text |
| `uncord/safety.py` | escape stripping, link checks, log scrubbing |
| `uncord/_native.c` | C: sixel encoding, kitty image chunks, ppm frames, h264 splitting |
| `uncord/_dsp.cpp` | C++: voice volume, mixing, levels and call sounds |
| `uncord/_rtp.cpp` | C++: video depacketizers, jitter buffer, rtcp and outgoing packets |
| `packaging/` | AUR and Nix packages |

See [CONTRIBUTING.md](CONTRIBUTING.md) and [CHANGELOG.md](CHANGELOG.md).

## Todo

- [ ] Put `uncord` and `uncord-git` on the AUR (AUR sign-ups are down, the packages are ready in `packaging/aur/`)
- [ ] Get uncord into nixpkgs (once it has been around a while)

## Credits and license

Thanks to [hakuxyz](https://github.com/hakuxyz) for help tracking down screen sharing bugs.

MIT, see [LICENSE](LICENSE).

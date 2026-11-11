# Changelog

## 1.10 (2026-11-11)

- Forwarded messages show up. Before, a forward looked like an empty message. Now you see the forwarded text and files, and its images draw in the chat
- Press **f** on a message to forward it to another chat
- Press **b** on a message to save it, and `/saved` lists your saved messages and jumps back to one. They're kept in your config, only on your computer
- New plugin, **SplitLongMessages**: a message over 2000 characters is sent in parts instead of failing. It cuts at line breaks and closes and reopens code blocks
- `/shrug`, `/tableflip`, `/unflip`, `/lenny`, `/me` and `/spoiler`, like the desktop app
- A tidier look:
  - Settings opens at its full size. It was squeezed into a small box that cut off half of every tab
  - dropdowns and text boxes in settings and popups are one line tall instead of three
  - popups have square corners
  - scrollbars are one column wide and grey
  - the server list no longer gets a sideways scrollbar from one long name
- The chat drawn at startup, before Discord connects, no longer has a blank line after every message

## 1.03 (2026-11-07)

- Much more of uncord is Rust now:
  - message rendering (markdown, spoilers, links, mentions, timestamps, quotes, headings and lists) is done in Rust, about 25% faster than before. It gives exactly the same output as the old Python renderer, checked against it on thousands of messages
  - sixel and Kitty image encoding, ffmpeg frame parsing, and H.264 and RTP packet parsing moved from C to Rust, so everything that reads data other people send is memory safe. Sixel encoding is about 20% faster and Kitty uploads about as fast as before. The output is byte for byte the same, and the C part is gone
- A link like `https://[x` in a message no longer breaks drawing that message

## 1.02 (2026-11-07)

- uncord opens much faster:
  - the chat you last had open and your server list appear straight away (about 0.5 s) from a copy saved when you last used it, then swap to the live ones once Discord connects
  - live is about 2.5 s instead of 4 s on an account with 64 servers. uncord no longer waits for every server's member list before showing anything (those load in the background, the open server first), it connects to Discord while your login is still being checked, and the last chat's messages download while Discord is still sending your account data
  - the saved copy is readable only by you, can be turned off in **Settings → Privacy**, and is deleted when you log out
- Buttons and menus use real icons instead of emoji: the voice panel, call bar, message menu, composer and user menus. They need a Nerd Font, and uncord uses emoji if none is installed. Choose in **Settings → Appearance → Icons**
- Rust is now required to install uncord. The install script installs it, and the AUR and Nix packages already build it

## 1.01 (2026-11-07)

- uncord now has a Rust part (`rust/`, built with PyO3). Searching in Ctrl+K, the emoji, sticker and GIF pickers and every other picker happens in Rust: 0.7 ms per key instead of 20 ms with 20,000 channels, people and servers, so typing in a big account doesn't lag
- Pickers now find the best matches in the whole list. Before, they stopped looking after the first 4,000 hits
- Stripping control characters from incoming text is quicker
- Rust is optional when installing: with cargo installed, the install script, pip, the AUR package and Nix build it, and without it Python does the search the same way as before. The install script now offers to install Rust as a nice-to-have

## 1.00 (2026-11-07)

uncord 1.0 is about speed, safety and being easier to work on.

- Voice is decoded in C++ instead of through Python's ctypes: about 2.3× faster per person talking (45 µs instead of 102 µs for each 20 ms of audio), and it no longer holds up the rest of the app while it decodes. Stream audio uses it too. The sound is bit-for-bit the same
- Messages draw faster again: 7.9 µs each in the benchmark, down from 21 µs in 0.80
- TextReplace swaps and KeywordNotify words are set in **Settings → Plugins**, in a box under each plugin, instead of with `/replace` and `/keywords`
- Lookalike links written entirely in another alphabet, like `аррӏе.com` in Cyrillic, are caught too, not just ones that mix alphabets
- Translate and Google Lens image search ask once before they first send anything to Google
- A display name with `$` in it can't run mpv property expansions in the pop-out window title
- A test suite (`tests/`, 30 tests that never log in), benchmarks (`bench/`) and [AGENTS.md](AGENTS.md) with the conventions for code, docs and releases

## 0.90 (2026-11-07)

- Five new plugins, 30 in total:
  - **TextReplace** swaps words in messages you send. `/replace idk => i don't know` adds a swap, `/replace -idk` removes it and `/replace` lists them. Code blocks are left alone
  - **SendTimestamps** turns `<t:18:30>`, `<t:2026-12-25 09:00>` or `<t:+2h>` into a Discord timestamp that everyone sees in their own time zone
  - **KeywordNotify** notifies you when a message anywhere says one of your words, set with `/keywords`
  - **FixEmbeds** (off to begin with) sends x.com, twitter.com and reddit.com links as fixupx, fxtwitter and rxddit links so they embed
  - **OwnerCrown** shows 👑 next to the server owner
- Messages draw about twice as fast. Plain messages skip the markdown parser entirely, the line patterns are compiled once, and highlighted code blocks are cached, so opening a busy channel or scrolling back through history is quicker. What you see is exactly the same as before
- Lookalike links are caught: an address that mixes normal letters with ones from another alphabet (`dіscord.com` with a Cyrillic `і`) gets a ⚠ with its real address, in plain and masked links. uncord always asks before opening one, even with link confirmation off

## 0.80 (2026-11-02)

- Drafts: whatever you've typed, the message you're replying to and any attached files stay with that chat when you switch away, and come back when you return. Typed drafts are kept when you quit too. Before, the text and files followed you into the next chat and could get sent to the wrong place
- Images, GIFs, videos and voice messages only load from Discord's own servers. A bot embed pointing at some other site can't get your IP address any more, as uncord uses Discord's image proxy instead, like the official app
- Downloads stop at 64 MB, so a huge file can't eat your memory
- ffmpeg only opens https links, so a crafted video or playlist can't make it read files on your computer
- Links handed to mpv can't be read as mpv options
- The frame file for streams in Kitty is created only readable by you and never follows a symlink someone else left in /dev/shm

## 0.77 (2026-10-26)

- Jumping to an old message (from pins, search or a reply) no longer strands you: scroll or press ↓ at the bottom to load newer messages, and G or the bar under the chat takes you back to the present. New messages that arrive meanwhile are counted on that bar instead of being stuck under old history
- `J` (or the message menu) jumps to the message a reply is answering, loading it if it's further back
- Bot slash commands with user, channel, role, true/false, number, file or choice options now work. Before, a user or role option failed outright and `flag:false` was sent as true. Mentions, IDs and names all work, choices ignore case, and bad values get a clear message
- If saving an edit or sending a reply fails, the edit or reply is kept, so pressing Enter again retries it instead of posting a new message
- When a message is deleted, the next one gets its name back if it was grouped under it, and an empty date line goes away
- Clicking a reaction a bunch of times quickly now sends one request for where you end up (or none if you end where you started) instead of one per click, so Discord stops rate limiting you
- Copy text in the message menu copies attachment links when the message has no text, like `y` does
- Muted chats no longer send desktop notifications while you're in them with the terminal unfocused

## 0.76a (2026-10-19)

- `uncord --login` uses the account you just logged in with even when `UNCORD_TOKEN` is set
- `/upload` works with paths that have spaces and checks the upload limit before sending
- An app clearing its Rich Presence no longer wipes another app's activity that's showing
- `Authorization: Bearer …` and `Bot …` headers are fully scrubbed from the log, not just the first word
- Env file values can have a trailing ` # comment`, `uncord --env` shows a token set through `DISCORD_TOKEN`, and a failing `UNCORD_TOKEN_CMD` says its exit code
- Fixing permissions on the token file no longer follows a symlink to change some other file
- The "token invalid" message points at `UNCORD_TOKEN` / `UNCORD_TOKEN_CMD` when those are how you logged in

## 0.76 (2026-10-19)

- Environment variables for the token and everything else: `UNCORD_TOKEN` (`DISCORD_TOKEN` still works), `UNCORD_TOKEN_CMD` to get it from a password manager, `UNCORD_TOKEN_FILE`, `UNCORD_CONFIG_DIR`, `UNCORD_CACHE_DIR`, `UNCORD_LOG_FILE`, `UNCORD_LOG_LEVEL` and `UNCORD_NO_UPDATE_CHECK`, on top of the existing ones. `uncord --env` lists them
- They can go in `~/.config/uncord/env` too (see `uncord.env.example`). Real environment variables win, and only uncord's own keys are read from it
- The token is taken out of the environment once read, so programs uncord starts (ffmpeg, mpv, pw-record, file pickers, git) don't inherit it
- Log scrubbing now runs on the finished line, so a token or Authorization header inside an error traceback is hidden too
- The token and env files are opened without following symlinks and refused if they belong to someone else. The token is saved atomically and checked for stray spaces or control characters
- `uncord --logout` and Log out in settings overwrite the token file before deleting it
- The terminal file picker writes its answer into a private temporary folder instead of a guessable path

## 0.75n (2026-10-15)

- Video receiving and screen sharing moved into a new C++ part (`_rtp.cpp`): the H.264, H.265, VP8, VP9 and AV1 depacketizers, the jitter buffer that reorders packets and asks for resends and keyframes, RTCP reports, outgoing video packets and cutting the capture into frames
- The built-in sixel encoder (used when libchafa isn't installed) is now C and about 15 times faster, and images with 256 colours or fewer keep their exact colours
- Kitty image uploads and ffmpeg's video frames for inline clips are split up in C

## 0.75m (2026-10-15)

- Stable AUR package checksum updated for the re-tagged v0.75b release

## 0.75l (2026-10-15)

- Voice audio maths (volume, mixing, levels, call sounds) moved from Python's `audioop` into a small C++ part. It mixes several people about a third faster, clips once instead of after every voice so loud calls distort less, and drops the `audioop-lts` dependency. Installing now needs g++ as well as gcc
- Background jobs (sending reactions, notifications, leaving calls…) can no longer be dropped halfway, their errors go to the log, and quitting cancels them cleanly instead of logging "Task was destroyed"
- Clicking reactions quickly sends them to Discord in order, so the end result matches what you clicked
- Someone's "is typing" clears the moment their message arrives
- A broken `config.json` is kept as `config.json.bad` instead of being overwritten with defaults, and a setting with the wrong type falls back to its default instead of crashing
- Attaching a big file no longer freezes the window while it's read
- Files over your upload limit (10 MB free, more with Nitro or a boosted server) are caught before uploading, and a failed upload always keeps your message and files
- `uncord --update` copes when the history on GitHub has been rewritten, as long as you have no commits of your own that would be lost

## 0.75k (2026-10-14)

- Calls: joining no longer asks Discord to pause every incoming stream, which could leave you hearing nobody. Only cameras you stop watching get paused
- The voice log shows which kinds of packets arrive, to pin down audio problems faster

## 0.75h (2026-10-14)

- The installer adds `~/.local/bin` to your PATH (bash, zsh, fish or `~/.profile`) so `uncord` is found, and says how to start it right away. Uninstalling removes the line

## 0.75g (2026-10-14)

- Installing works again: versions with a letter (0.75c to 0.75f) weren't valid for pip. The title bar still shows the letter, and pip sees 0.75g as 0.75.7

## 0.75b to 0.75f (2026-10-14)

Installing from GitHub failed from 0.75c to 0.75f, fixed in 0.75g.


- MIT license
- Readme: Nix install with `nix profile install`, AUR and nixpkgs listed as todos
- Stable AUR package builds from the v0.75b release
- Changelog, issue templates, contributing and security notes

## 0.75 (2026-10-14)

- The C part is required: install needs a C compiler and the Python headers, and uncord says how to fix it if it's missing

## 0.6 → 0.75 (2026-10-14)

- Settings is one screen with tabs (Appearance, Notifications, Chat, Voice & video, Privacy, Plugins, About), opened from ⚙, F3 or F9
- Voice settings are a settings tab, with the live mic meter
- C code for the busiest image and video paths (sixel scans, Kitty image rows, H.264 packets, RTP headers)
- Faster startup: libraries are looked up when first needed
- Security:
  - escape sequences in messages, names and embeds are stripped before they reach the terminal
  - only http and https links open, with an option to ask first
  - masked links show their real site, with a warning when the text names another one
  - tokens never reach the log, and the config, token and log are readable only by you
  - the Rich Presence socket only accepts your own apps and rejects oversized data
  - notification text can't inject markup or options
- APP, SYSTEM and WEBHOOK tags, your reactions and mentions of you use Discord blurple
- Device icons next to names in chat
- Members list shows online and offline counts
- Discord account notices show as a card instead of raw fields
- Nix flake (`nix run github:owainxyz/uncord`)

## 0.6 (2026-10-13)

- Settings screen (F3) with 25 plugins
- Server and channel menus: notifications, mute, nickname, invites, server info, leave
- Inbox (F4) for unreads and mentions
- Bot slash commands with autocomplete
- Rich Presence for games and apps
- Kitty graphics for images, GIFs, emoji and streams in Kitty and Ghostty
- Members list (F2), server tags, APP badges, device icons
- Embeds with colour bars, inline fields, footer and timestamp
- Highlighted code blocks, numbered lists, date lines and a new-messages marker
- Desktop notifications over D-Bus

## 0.5 (2026-10-13)

- First public release: servers, DMs, threads, voice and video calls, inline images and GIFs, screen sharing both ways, QR login

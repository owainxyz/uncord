# Road to 1.0

0.90 is the last big feature release before 1.0. 1.0 is about speed and stability more than new features: the busy parts move out of Python into compiled code, and everything gets tests.

## Speed

uncord already does video packets and sixel in C (`_native.c`, `_rtp.cpp`) and audio mixing in C++ (`_dsp.cpp`). 1.0 moves the rest of the hot paths over:

- [ ] **Message rendering in Rust.** Markdown, mentions, timestamps and link parsing become one native parser (PyO3) that returns ready-made spans. 0.90's fast paths made rendering about 2× faster; the goal for 1.0 is another 5× on busy channels
- [ ] **Gateway events off the UI thread.** Parse and filter Discord's event stream natively, so a flood of messages in a big server can't stall typing or scrolling
- [ ] **Opus decode and encode in native code.** Decode straight into the C++ mixer with no Python per packet, so calls with lots of people use less CPU
- [ ] **Image pipeline in native code.** Decode, scale and encode for sixel and Kitty without round trips through Pillow, with images reused between scrolls
- [ ] **Faster startup.** Lazy-load voice, video and plugins, and cache the sidebar from the last session, so the window is usable before the gateway is ready
- [ ] **Bounded memory.** Hard caps on cached messages, images and members per server, with old entries dropped first

## Stability

- [ ] A test suite for rendering, slash commands, plugins and the safety helpers, run before every release
- [ ] Benchmarks for rendering, startup and voice CPU, so a release can't get slower without anyone noticing
- [ ] Reconnects that keep your place: open chat, drafts, scroll position and call

## Install

- [ ] Prebuilt wheels with the native parts compiled, so installing doesn't need gcc, g++ or Rust
- [ ] Stable AUR and Nix packages that follow tagged releases

## Security

- [ ] Run ffmpeg and mpv with only the access they need (no network for local files, no home directory)
- [ ] A permission check for plugins that send data anywhere (Translate, ReverseImageSearch), shown the first time they're used
- [ ] Wider lookalike link detection, including addresses written entirely in another alphabet

Ideas and bug reports are welcome on the [issue tracker](https://github.com/owainxyz/uncord/issues) or the [uncord Discord server](https://discord.gg/fubfK8C6Cm).

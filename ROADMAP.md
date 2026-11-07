# Roadmap

## Done in 1.0

- [x] Opus decoding in C++ (`_dsp.cpp`), 2.3× faster than the ctypes path and bit-for-bit the same
- [x] Message rendering about 2.7× faster than 0.80 (fast paths for plain text, compiled patterns, cached code highlighting)
- [x] A test suite for rendering, plugins, the safety helpers, plugin settings and Opus, which never logs in
- [x] Benchmarks for rendering and Opus decoding
- [x] Lookalike links in mixed or entirely different alphabets
- [x] A one-time prompt before Translate or Google Lens sends anything to Google
- [x] Plugin options in Settings instead of slash commands

## After 1.0

Where the time goes now: most of what's left is Textual and Rich laying out widgets, Discord's own login data, and Python glue around libraries that are already native. These are the next steps, measured with `bench/` before and after:

- [ ] **Faster startup.** Show the sidebar from the last session straight away instead of waiting for Discord's login data
- [ ] **Gateway events off the UI thread.** Parse and filter Discord's event stream in the background, so a flood of messages in a big server can't stall typing
- [ ] **Native message spans.** Build the coloured spans for a message in one native pass (Rust or C++) instead of piece by piece in Python
- [ ] **Native Opus encoding** for your own mic, matching the decoder
- [ ] **Prebuilt wheels** so installing doesn't need a compiler
- [ ] **Stable AUR and Nix packages** that follow tagged releases
- [ ] **Tighter sandboxing** for ffmpeg and mpv

Ideas and bug reports are welcome on the [issue tracker](https://github.com/owainxyz/uncord/issues) or the [uncord Discord server](https://discord.gg/fubfK8C6Cm).

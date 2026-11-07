# uncord

Discord in your terminal: servers, DMs, voice and video calls, images and GIFs, and screen sharing both ways. It logs in as your own account, so everything you see in the official app is here too.

Questions or ideas? Join the [uncord Discord server](https://discord.gg/fubfK8C6Cm).

> [!WARNING]
> Discord's terms don't allow third-party clients on user accounts. Plenty of people use them anyway, but your account could get flagged. Use it at your own risk.

## Contents

1. [What it does](#what-it-does)
2. [Installing](#installing)
3. [Logging in](#logging-in)
4. [Getting around](#getting-around)
5. [Reading and sending messages](#reading-and-sending-messages)
6. [Voice and video calls](#voice-and-video-calls)
7. [Screen sharing](#screen-sharing)
8. [Settings](#settings)
9. [Plugins](#plugins)
10. [Slash commands](#slash-commands)
11. [Files and environment variables](#files-and-environment-variables)
12. [Privacy and security](#privacy-and-security)
13. [Troubleshooting](#troubleshooting)
14. [For developers](#for-developers)

## What it does

uncord covers almost everything you'd do in the desktop app. You get servers, DMs, group DMs, threads and forums, with replies, edits, reactions, pins, search, and unread and mention counts. Messages render with markdown, highlighted code, embeds, server tags and APP badges, and the members list shows which device each person is on.

Pictures, GIFs, stickers and custom emoji are drawn right in the terminal. They look sharpest in Kitty and Ghostty, and terminals with sixel support (foot, WezTerm, Konsole and others) work too.

You can join voice channels and call people. Volume can be set per person, mic gain is automatic and you can turn your camera on. You can go live with one key or watch someone else's stream in the terminal. Calls and streams use Discord's DAVE end-to-end encryption, the same as the official app.

It also has an inbox for unreads and mentions, bot slash commands, voice messages, Rich Presence for your games and 30 optional [plugins](#plugins). The busy parts are compiled so it stays quick. Image and video packets are handled in C, and voice mixing and levels in C++.

## Installing

uncord runs on Linux (x86_64 or ARM, glibc or musl) and needs Python 3.10 or newer.

### With the install script

This is the easiest way, and it works on Debian, Ubuntu, Fedora, Arch, openSUSE, Void, Alpine and Gentoo:

```sh
git clone https://github.com/owainxyz/uncord.git
cd uncord
./install.sh
```

The script asks before using your package manager to install the system packages uncord needs. It then puts uncord in `~/.local/share/uncord` and adds an `uncord` command and an app menu entry. At the end it runs `uncord --doctor` so you can see that everything was found.

Pass `-y` to skip the questions, `--no-system` if you'd rather install the system packages yourself, or `--dry-run` to see what it would do without changing anything.

### With Nix

```sh
nix run github:owainxyz/uncord              # try it without installing
nix profile install github:owainxyz/uncord  # install it
```

On NixOS, add the flake to your inputs with `inputs.uncord.url = "github:owainxyz/uncord";`, then put `uncord.packages.${system}.default` in your packages. uncord isn't in nixpkgs yet, so `nix-env -iA nixpkgs.uncord` won't find it.

### By hand

First install the build tools: gcc, g++ and your distro's Python headers (usually `python3-dev` or `python3-devel`). For voice you also need ffmpeg, libopus and PipeWire. Then:

```sh
python3 -m venv ~/.local/share/uncord/venv
~/.local/share/uncord/venv/bin/pip install .
~/.local/share/uncord/venv/bin/uncord
```

These extras are optional, and each one switches something on:

- **chafa** draws better images in terminals without kitty graphics.
- **mpv** pops videos and streams out into their own window.
- **wl-clipboard** (Wayland) or **xclip** (X11) lets you paste images into messages.
- **a notification daemon** gives you desktop notifications.
- **gpu-screen-recorder** is needed for screen sharing and your camera.

### Updating and removing

Run `uncord --update` to get the latest version. uncord also tells you when a new one is out.

To remove it, run `./install.sh --uninstall` from the folder you cloned. Your login and settings in `~/.config/uncord` are kept in case you come back, so delete that folder yourself if you want them gone.

## Logging in

The first time you run `uncord` it asks how you want to log in. The easiest way is the QR code: open the Discord app on your phone, go to Settings → Scan QR Code and point it at your terminal. You don't need your password for this. If you already have a token you can paste it in instead.

Your login is saved to `~/.config/uncord/token`, and only your user can read it. If you want to switch accounts, run `uncord --login`. To forget the login completely, run `uncord --logout`.

## Getting around

The screen is split the same way as Discord's. Your servers and DMs are down the left, the chat is in the middle and the members list is on the right. When you start uncord it opens the last chat you were in.

The quickest way to get anywhere is **Ctrl+K**. Start typing a person, DM, group, channel, thread or server and press Enter. You can also:

- press **Alt+↑** and **Alt+↓** to step through the channels in the current server, or **Alt+Shift+↑/↓** to jump only to channels with unread messages
- press **Ctrl+Alt+↑/↓** to switch servers, and **Alt+←/→** to go back and forward through chats you've visited
- press **Tab** or **Esc** to move between the message box and the sidebar
- press **Ctrl+B** to hide the sidebar and **F2** to show or hide the members list

In the sidebar, clicking a server (or pressing Enter on it) takes you back to where you left off there. Space folds folders and categories. Right-click a server to mark it all as read.

**F4** opens your inbox of unread messages and mentions. **Ctrl+U** opens your friends list and **Ctrl+S** sets your status. **F1** shows every key in uncord.

## Reading and sending messages

Type in the box at the bottom and press Enter to send. While you type, `@name`, `#channel` and `:emoji:` all autocomplete, and Tab or Enter picks the suggestion. Something like `:sob:` turns into 😭 as you type, and server emoji like `:pog:` are swapped in when the message is sent.

The buttons next to the message box each have a shortcut. **Ctrl+G** opens GIFs (favourites, trending and search), **Ctrl+E** the emoji picker and **Ctrl+T** stickers. **Ctrl+R** records a voice message: press it again to send or Esc to cancel. **Ctrl+O** attaches a file.

To act on a message that's already been sent, press **↑** in an empty message box. This lets you move through messages, and then:

- **r** replies, **e** edits, **d** deletes and **P** pins or unpins it
- **+** adds a reaction, **-** removes one, and **1–9** quickly toggles one of your recent emoji
- **v** shows an image, sticker or emoji full size, **o** opens a link and **s** reveals spoilers
- **y** copies the text and **c** copies a link to the message
- **t** opens its thread, **m** DMs the author and **p** shows their profile
- **J** jumps to the message it replied to, **g** and **G** go to the top and bottom, and **Esc** goes back

Pressing ↑ at the top of a chat loads older messages. After you've jumped back in time, ↓ at the bottom loads newer ones, and **G** (or clicking the bar under the chat) takes you back to the present. You can click reactions to add or remove yours, and click images and GIFs to enlarge them.

**Ctrl+F** searches messages, and Discord's filters work here too, for example `from:name`, `in:channel` and `has:link`, `has:image` or `has:file`.

## Voice and video calls

Click a 🔊 voice channel to join it. You stay in your current text chat, and right-clicking the channel opens its text chat instead. In a DM or group, **F5** starts a call or answers one.

While you're in a call, **F6** mutes, **F7** deafens and **F8** leaves. The panel in the bottom left has the same buttons. Right-click someone, or click their name in the call strip, to set their volume anywhere from 0 to 200%, or to mute them just for you. **F12** turns your camera on and off.

**F9** opens the voice settings, where you choose your mic and speakers, set the volume and mic sensitivity and turn call sounds on or off. You can also do this from the message box. `/vad <n>` sets mic sensitivity (0 is an open mic), `/vol <0-300>` sets output volume and `/sfx on|off` toggles call sounds. If audio is acting up, `/voicestats` shows what's going in and out.

## Screen sharing

To share your screen, press **F10** in a call. This needs `gpu-screen-recorder`, and on GNOME or KDE Wayland you should pick the "portal" option. The default quality can be changed with `/share 720p30`, `1080p30`, `1080p60` or `1440p60`, and `/share stop` ends the stream.

When someone goes live, a red **LIVE** tag appears next to their name. Click it or press **F11** to watch. In the viewer:

- **+** and **-** change the size and **f** makes it full size
- **p** pops it out into mpv
- **m** mutes the stream audio
- **Esc** closes it

You can watch someone's camera the same way, by clicking the 📷 next to their name.

## Settings

Open settings with the ⚙ button by your name, **F3** or `/settings`. Changes take effect straight away.

- **Appearance** covers the theme, line spacing, whether images show, the layout and how big streams are.
- **Notifications** controls desktop notifications and whether they show message previews.
- **Chat** has the DM list size, the language for translations and which file picker to use.
- **Voice & video** has your devices, volumes, mic sensitivity, call sounds, screen share quality and camera.
- **Privacy** covers link safety, Rich Presence and logging out.
- **Plugins** switches the [plugins](#plugins) on and off.
- **About** shows your version and what uncord found on your system, and lets you check for updates.

## Plugins

uncord has 30 small extras in the spirit of Vencord plugins. You can turn them on and off in **Settings → Plugins** or with `/plugins`.

These are on to begin with:

- **MessageLogger** keeps deleted messages and shows what edited ones said before.
- **PlatformIndicators** shows 🖥 📱 🌐 for the devices people are on.
- **TypingIndicator** puts ✎ next to channels and DMs where someone is typing.
- **CallTimer** shows how long you've been in a call.
- **ClearURLs** strips tracking junk (utm, fbclid, si and so on) from links you send.
- **FakeNitro** sends emoji you can't use in a server as image links instead of failing.
- **RelationshipNotifier** tells you when someone unfriends you or sends a friend request.
- **RichPresence** lets games and apps on your PC set your activity, like the desktop app does. Restart uncord after changing it.
- **Translate**, **ViewRaw**, **WhoReacted** and **ReverseImageSearch** add options to the message menu (Enter or right-click on a message).
- **PinDMs** lets you pin DMs to the top of the list by right-clicking them.
- **MemberCount** shows the online and total members in the title bar.
- **ShowConnections** shows someone's linked accounts, such as Steam or Spotify, on their profile.
- **ReplyTimestamp** shows when the message you're replying to was sent.
- **ValidReply** fetches replied-to messages that aren't loaded instead of saying they were deleted.
- **Unindent** trims the extra indent from code blocks.
- **TextReplace** swaps words in messages you send. Add a swap with `/replace idk => i don't know`, remove it with `/replace -idk`, and list them with `/replace`.
- **SendTimestamps** turns `<t:18:30>`, `<t:2026-12-25 09:00>` or `<t:+2h>` into a Discord timestamp, so everyone sees the time in their own time zone. A time that has already passed today means tomorrow.
- **KeywordNotify** notifies you when a message anywhere says one of your words, even in a muted channel. Add one with `/keywords uncord`, remove it with `/keywords -uncord`, and list them with `/keywords`.
- **OwnerCrown** shows 👑 next to the server owner.

These are off to begin with:

- **ShowMeYourName** shows @username next to nicknames.
- **NoReplyMention** makes your replies not ping the person you reply to.
- **SilentTyping** hides that you're typing.
- **NoBlockedMessages** hides messages from blocked people completely.
- **ShowHiddenChannels** lists channels you can't read, with a 🔒.
- **AnonymiseFileNames** uploads files with random names.
- **FixEmbeds** sends x.com, twitter.com and reddit.com links as fixupx, fxtwitter and rxddit links so they get a proper embed.
- **Moyai** 🗿

## Slash commands

Type `/` in the message box to see every command, including the ones from bots in the current server. To send a message that starts with a slash, begin it with `//`.

Commands for **chatting**:

- `/dm name` and `/group a, b` start a DM or a group.
- `/friends`, `/members` and `/whois name` show your friends, the members list or someone's profile.
- `/search` searches messages and `/pins` lists pinned messages.
- `/upload ~/file [caption]` sends a file. `/sticker` and `/emoji` open the pickers.
- `/read` marks the current chat as read and `/readall` marks everything as read.
- `/nick name` sets your nickname, and `/status` sets your status.
- `/replace` and `/keywords` manage the TextReplace swaps and KeywordNotify words.

Commands for **calls**:

- `/join`, `/answer`, `/decline` and `/leave` join or answer calls, and `/mute` and `/deafen` work like F6 and F7.
- `/share`, `/watch` and `/camera` are covered in [screen sharing](#screen-sharing) and [calls](#voice-and-video-calls).

Commands for **uncord itself**:

- `/settings`, `/plugins` and `/theme` open settings, plugins or the theme picker.
- `/media on|off` shows or hides images.
- `/quit` exits.

## Files and environment variables

uncord keeps its files in the usual places, and each one is readable only by you:

- `~/.config/uncord/token` holds your login.
- `~/.config/uncord/config.json` holds your settings.
- `~/.config/uncord/env` is an optional file for environment variables.
- `~/.cache/uncord/uncord.log` is the log, which is useful when something goes wrong.

You don't have to keep your token on disk. Set `UNCORD_TOKEN` (or `DISCORD_TOKEN`) to the token itself, or set `UNCORD_TOKEN_CMD` to a command that prints it, such as `pass show discord/token`.

Folders, the log, the theme, the voice gate and the paths to tools like ffmpeg all have variables too, and `uncord --env` lists them all. Instead of exporting them in your shell, you can put them in `~/.config/uncord/env` as `KEY=value` lines. `uncord.env.example` in the repo is a starting point. Variables set in the real environment win over the file, and uncord only reads its own keys from it.

## Privacy and security

Anything in a message, name or embed that would control your terminal (escape sequences that write to your clipboard or change the window title, for example) is stripped out before it's drawn.

Masked links show where they really go, with a ⚠ if the text claims to be a different site. Links whose address mixes normal letters with lookalikes from other alphabets, like `dіscord.com` with a Cyrillic `і`, get a ⚠ with the real address, and uncord always asks before opening one. Only http and https links open in your browser, and you can have uncord ask before it opens anything. Images, videos and voice messages only ever load through Discord's own servers, so a link in an embed can't get your IP address. Downloads are capped at 64 MB.

Your token is treated carefully:

- it never ends up in the log, even inside an error traceback
- it's removed from uncord's environment once it's been read, so ffmpeg, mpv and anything else uncord starts can't see it
- uncord refuses a token or env file that is a symlink, belongs to someone else or isn't a plain file
- `uncord --logout` overwrites the token file before deleting it

The Rich Presence socket only accepts connections from your own apps, and it drops messages that are too big or malformed.

To report a security problem, see [SECURITY.md](SECURITY.md).

## Troubleshooting

Start with `uncord --doctor`. It lists what uncord found on your system and what's missing.

**`uncord: command not found` right after installing.** Open a new terminal. The installer adds `~/.local/bin` to your PATH, but terminals that were already open won't see the change. Until then, `~/.local/bin/uncord` works.

**Images look blocky.** Your terminal can't draw real images. Try Kitty, Ghostty, foot, WezTerm or Konsole, or install chafa for better fallback images.

**No sound, or nobody can hear you.** Check that the right mic and speakers are picked in Settings → Voice & video. `/voicestats` shows whether audio is coming in and going out, and what your mic level is.

**Screen sharing fails.** Run `gpu-screen-recorder --list-monitors` to check that it can see your screens. On GNOME or KDE Wayland, use the portal option.

**uncord can't find ffmpeg, opus, chafa or gpu-screen-recorder.** If they're installed somewhere unusual, set `UNCORD_FFMPEG`, `UNCORD_OPUS`, `UNCORD_CHAFA` or `UNCORD_GSR` to the path.

**Anything else.** Look in `~/.cache/uncord/uncord.log`, or ask in the [Discord server](https://discord.gg/fubfK8C6Cm).

## For developers

To set up a development copy:

```sh
python3 -m venv .venv && .venv/bin/pip install -e .
.venv/bin/python setup.py build_ext --inplace   # rebuild after editing _native.c, _dsp.cpp or _rtp.cpp
.venv/bin/python -m uncord
```

uncord is built on [discord.py-self](https://github.com/dolfies/discord.py-self) and [Textual](https://github.com/Textualize/textual). Most of the app is in `uncord/app.py`: the main window, the sidebar, the chat and the Discord event handlers. Message rendering is in `fmt.py` and `messages.py`, and the settings screen is `settings.py`. Calls, screen sharing and video are in `voice.py`, `golive.py` and `rtpvideo.py`. `safety.py` handles escape stripping, link checks and log scrubbing.

There are three compiled extensions:

- `_native.c` handles sixel encoding, kitty image chunks, ppm frames and h264 splitting.
- `_dsp.cpp` handles voice volume, mixing, levels and call sounds.
- `_rtp.cpp` handles video depacketizing, the jitter buffer, rtcp and outgoing packets.

The AUR and Nix packages are in `packaging/`. See [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request, and [CHANGELOG.md](CHANGELOG.md) for what's changed. What's planned for 1.0 is in [ROADMAP.md](ROADMAP.md).

Still to do: put `uncord` and `uncord-git` on the AUR (the packages are ready in `packaging/aur/`, but AUR sign-ups are down), and get uncord into nixpkgs once it's been around a while.

## Credits and license

Thanks to [hakuxyz](https://github.com/hakuxyz) for help tracking down screen sharing bugs.

uncord is MIT licensed, see [LICENSE](LICENSE).

# Emily's Strange Arcade

A personal, mobile-first fan-made launcher for the original Emily the Strange browser games.

**Live site:** https://macyan0926.github.io/Emily-Arcade/

## What's included

- Six Emily browser-game entries: Drop Dead Dizzy, Strange Invaders, Deathtris, Nine Lives Forever, Homework Hexx, and Spiders and the Fly.
- Ruffle player for SWF files imported on each device.
- A Flashpoint 9o3o browser-player attempt and a link to the Flashpoint catalog.
- R.U.E.S.P. Quiz is omitted because its playable SWF was not recovered.
- Per-game local saves in IndexedDB, plus remove-saved-copy controls.
- A standalone Home Screen experience, an iPhone touch-friendly layout, fullscreen controls, and a cached app shell.

## Use on iPhone

1. Open the live site in Safari.
2. Tap **Share**.
3. Choose **Add to Home Screen**, then tap **Add**.

Launch Emily Arcade from the new Home Screen icon.

## Use on Mac

This is a static site; there is no build step or package installation. Clone the repository, open the project folder in Terminal, and run:

```sh
python3 -m http.server 8000
```

Then visit http://localhost:8000.

## Game files and offline behavior

The six SWF files have been collected separately, but they are not yet bundled into this public repository. To play on an iPhone, transfer the relevant `.swf` file to the iPhone (for example via iCloud Drive or AirDrop), then use **LOAD SWF** in the game window. Imported files are saved in IndexedDB for that browser on that device; they are not uploaded and do not sync between devices. The experimental Flashpoint browser player is a fallback, not a guaranteed iPhone-compatible player.

The app shell is cached after the first successful visit. First-time Ruffle loading and the online archive require an internet connection. Browser playback is not guaranteed for every archived title; some Flashpoint entries require the desktop Flashpoint app.

## Project notes

- No ads, subscriptions, analytics, or user accounts.
- This is an unofficial personal fan project and is not affiliated with the Emily the Strange rights holders.
- Original game assets and trademarks remain with their respective rights holders.

# Emily's Strange Arcade

A personal, mobile-first fan-made launcher for the original Emily the Strange browser games.

**Live site:** https://macyan0926.github.io/Emily-Arcade/

## What's included

- Six Emily browser-game entries: Drop Dead Dizzy, Strange Invaders, Deathtris, Nine Lives Forever, Homework Hexx, and Spiders and the Fly.
- Ruffle player that automatically loads the six bundled original SWF files on every device.
- A Flashpoint 9o3o browser-player attempt and a link to the Flashpoint catalog.
- R.U.E.S.P. Quiz is omitted because its playable SWF was not recovered.
- Per-game local saves in IndexedDB, plus remove-saved-copy controls; bundled games can play even when IndexedDB is unavailable.
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

All six recovered original SWF files are bundled in the public `games/` folder and load automatically when a game is opened. You do not need to transfer files from a Mac or import them manually on an iPhone. The game file is also saved in IndexedDB after its first successful load when the browser allows local storage; playback itself does not depend on IndexedDB. **LOAD DIFFERENT SWF** remains available if you want to try another file.

The app shell and fetched game files are cached by the service worker after loading. First-time Ruffle loading still requires an internet connection. Browser playback is not guaranteed for every archived title; some Flashpoint entries require the desktop Flashpoint app.

## Project notes

- No ads, subscriptions, analytics, or user accounts.
- This is an unofficial personal fan project and is not affiliated with the Emily the Strange rights holders.
- Original game assets and trademarks remain with their respective rights holders.

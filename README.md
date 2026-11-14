# Emily's Strange Arcade

A personal, mobile-first fan-made launcher for the original Emily the Strange browser games.

**Live site:** https://macyan0926.github.io/Emily-Arcade/

## What's included

- Six original Emily browser-game entries, with a Ruffle player for imported SWF files.
- A Flashpoint 9o3o browser-player attempt and a link to the Flashpoint catalog.
- The archived R.U.E.S.P. quiz page.
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

The original game files are not bundled into this repository. For a title without a locally saved copy, try the experimental Flashpoint browser player or import an original `.swf` file from the game window. Imported files are saved in IndexedDB for that browser on that device; they are not uploaded and do not sync between devices.

The app shell is cached after the first successful visit. First-time Ruffle loading and the online archive require an internet connection. Browser playback is not guaranteed for every archived title; some Flashpoint entries require the desktop Flashpoint app.

## Project notes

- No ads, subscriptions, analytics, or user accounts.
- This is an unofficial personal fan project and is not affiliated with the Emily the Strange rights holders.
- Original game assets and trademarks remain with their respective rights holders.

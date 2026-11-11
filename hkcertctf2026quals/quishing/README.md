# Quishing (QR Code Phishing)

## Quick Summary

- It is an in-game achievement, there is no flag (redeem code) to submit.
- This is a hidden achievement, i.e. the name of this achievement was unknown before solving.
- This achievement is unlocked through interacting with the Photo Kiosk in the game.

## Initial observations

It was Friday late night, AI agents were working hard to find flags in the game, when my friend joined in and started navigating around the game.

He pointed to the area with the 3 stations AI court, Photo Kiosk and FinSim. To our surprise, this area had not been explored yet.

With my teammate looking at AI prompting injections in the AI court, I quickly checked the Photo Kiosk.

The photo booth has four screens:

1. **Attract screen** — idle screen, waiting for a customer.
2. **Gallery** — pick one of the sample photos.
3. **Effect** — apply a filter ("Cool", "Warm", etc.).
4. **Share** — shows the final photo plus a QR code that opens an X intent link so the customer can tweet their photo.

The link is set to https://x.com/intent/tweet?text=%23401Unauthorized&url=https%3A%2F%2Funauthorized.cg.chal.sh - an ordinary promotion link on X.

## AI to the rescue

The link to X doesn't seem to provide anything. And on the screen there are no obvious visual clues for what to do. Therefore it is time to ask for help from our 4th teammate(s) - AI agents.

AI suggested two ideas:

- **Swipe gestures** - Kiosks running on tablets usually have an OS-level task switcher reachable by a swipe from the edge of the screen. The kiosk app itself is drawn on a 480×800 canvas (phone-sized), so swiping up from the very bottom edge is worth trying — exactly like exiting a kiosk-mode app on a real Android tablet.
- **Tapping around on every screen** - including areas that look blank, to see if there are any "hidden"/debug UI elements the attract screen doesn't advertise.

Doing the upward swipe from near the bottom edge dragging upward shows something like an app switcher as seen in phones.

And one of the "app" is "Setting / QR link". Tapping it shows a screen where we can edit the link that will be shown on screen.

As the link is set with a different one, we found the achievement "Quishing" is unlocked, with the description "Swap the kiosk's QR code for a link it should never show.", as the link has been changed through Setting.

## Reference: reproducing script

The kiosk is a server-rendered canvas driven over a WebSocket. User sends UI events (`tap`, `swipe`, `text`) to the server, and the server responds with JSON describing what to draw (text labels, image names, rectangles) plus some screen states (`screen`, `link_box`, `link_value`...).

Folder: `scripts/agent-5/scripts/`

```bash
python3 kiosk5.py \
  'swipe:240:798:240:500' \
  'tap:450:300' \
  'text:https://x.com/intent/post?url=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3DdQw4w9WgXcQ' \
  'tap:240:392'
```

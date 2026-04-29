# OS Compatibility and Captive Portal Behavior

This document describes how the captive portal handles each OS/device family, including known quirks and the reasoning behind device-specific logic.

---

## iOS

### Detection endpoints
- `/success.html` — iOS < 9 and pre-Yosemite macOS
- `/library/test/success.html` — other iOS versions
- `/hotspot-detect.html` — iOS 9+ and macOS Yosemite+

The `CaptiveNetworkSupport` user agent string identifies the OS-level captive portal probe agent. When this agent is detected after the initial interaction, `success.html` is returned to signal connectivity.

### Link behavior (`get_link_type`)

| iOS Version | Link Type | Notes |
|---|---|---|
| < 9 | TEXT | Older devices, link escapes not reliable |
| 9 | HREF | Can open links in system Safari |
| 10 | TEXT | Links open inside the captive portal browser (trapped) |
| 11+ | HREF | Apple restored system browser escape in iOS 11; iOS 12+ confirmed working |

iOS 10 is the only version where links are explicitly broken — all other versions from 9 onwards support HREF links.

---

## macOS

### Detection endpoints
- `/success.html` — pre-Yosemite (macOS < 10.10)
- `/hotspot-detect.html` — Yosemite (10.10) and later

### Link behavior (`get_link_type`)

| macOS Version | Link Type | Notes |
|---|---|---|
| < 10.12 (El Capitan and older) | TEXT | Cannot escape CP browser via links |
| 10.12 Sierra | HREF | First version with reliable link escape |
| 10.13 High Sierra | HREF | |
| 10.14 Mojave | HREF | |
| 10.15 Catalina | HREF | |
| 11 Big Sur | HREF | Apple changed major version from 10 to 11; ua_parser returns `major=11` |
| 12 Monterey | HREF | |
| 13 Ventura | HREF | |
| 14 Sonoma | HREF | |
| 15 Sequoia | HREF | |

**Important:** macOS 11+ (Big Sur onwards) uses a new version numbering scheme where the major version increments (11, 12, 13…) rather than the minor of 10.x. The `get_link_type` logic handles both schemes.

---

## Android

### Detection endpoints
- `/generate_204` — primary Android captive portal check
- `/gen_204` — fallback introduced in Android 7

### Three distinct user agents (Android 7.1+)
See [android-7.1.md](android-7.1.md) for full details on the X11, Dalvik, and WebKit agents.

### OK button (`device_requires_ok_press`)
Android 6+ receives an OK button on the connected page. This is required for Android 7.1+ to trigger the 204 response that signals internet access and prevents cellular fallback. Android 5 (Lollipop) does not receive the OK button because `device_requires_ok_press` returns `False` for versions below 6.

### Version summary

| Android Version | OK Button | Notes |
|---|---|---|
| < 6 | No | Tolerant of text-only flow |
| 6 (Marshmallow) | Yes | First version requiring OK press for clean flow |
| 7.1+ | Yes | X11 agent added; cellular fallback risk without 204 at right time |
| 10+ | Yes | Uses HTTPS for connectivity checks but HTTP fallback still works |

---

## Windows

### Detection endpoints
- `/ncsi.txt` — Windows Vista through Windows 8.1 (legacy NCSI)
- `/connecttest.txt` — Windows 10 and Windows 11 (modern NCSI via `msftconnecttest.com`)

Both endpoints return the captive portal page (`show_connected()`), which Windows interprets as "no internet" and triggers the captive portal notification.

Reference: https://technet.microsoft.com/en-us/library/cc766017(v=ws.10).aspx

---

## Amazon Kindle Fire

### Detection endpoint
- `/kindle-wifi/wifistub.html`

Always shows the captive portal page. No special session or OK-button logic.

---

## Unknown / other devices

All unmatched URLs are caught by the Flask 404 handler in `__init__.py` and routed to `show_connected()`. This covers any device or browser that probes an unexpected URL during captive portal detection.

# TeamTalk Xray

A real, from-source build of the [BearWare/TeamTalk5](https://github.com/BearWare/TeamTalk5)
Android client, extended with:

* **Blind-accessibility layer ("Xray")** – screen-reader announcements, a tactile
  event grammar (vibration patterns per event type), high-contrast theme, extra
  font scaling and large touch targets.
* **Admin panel** – the TeamTalk Plus administration screens ported onto the
  upstream 5.23 client: user accounts (create/edit/delete, rights, operator
  channels, codec limits, abuse prevention), server properties, moving users
  between channels, channel/server ban lists and un-banning, plus a live
  "server information" screen (server properties + real client counters).

Everything is compiled from upstream sources on GitHub Actions: the native
`libTeamTalk5-jni.so` and `TeamTalk5.jar` are built with CMake/NDK and the APK
with Gradle. The local `overlay/` tree is copied over the upstream checkout
before the build, so the project stays a thin patch instead of a fork.

## Layout

```
.github/workflows/build.yml   CI: clone upstream (pinned commit) -> apply overlay -> cmake/ninja -> gradlew assembleDebug
overlay/                      the patch applied to the upstream sources
tools/                        generators + static resource checker for the overlay
keys/                         signing key (xray.p12) used for the debug/release builds
```

## Package

`dk.bearware.gui.xray` – installed side by side with the original
`dk.bearware.gui` TeamTalk app.

## Credits

Upstream TeamTalk5 is © BearWare – Danmark. This overlay is an independent
extension and is not affiliated with BearWare or TeamTalk Plus.

سازنده: حسام بهمنی

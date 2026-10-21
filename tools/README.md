# Xray overlay generators

These scripts rebuild the `overlay/` directory that the CI workflow copies over
the upstream BearWare/TeamTalk5 sources (pinned commit in the workflow).

| script | what it generates |
|---|---|
| `mkoverlay.py` | blind-accessibility layer: `XrayA11y.java`, patched `MainActivity` / `ServerListActivity` / `PreferencesActivity`, `pref_xray.xml`, xray strings/arrays/styles |
| `mkadmin.py` | admin panel: TeamTalk Plus admin screens (user accounts, server properties, move users, channel/server bans), blind-friendly hub `XrayAdminActivity`, live `XrayServerInfoActivity` |
| `verify.py` | static resource checker (aapt2 cannot run on the phone, so missing `@string/@layout/@id/@color/@dimen/@drawable` are caught here) |

They expect this layout on disk:

```
/root/.buddy/work/teamtalk-xray/src        # upstream TeamTalk5 clone (pinned commit)
/root/.buddy/work/teamtalk-xray/ttp        # TeamTalkPlus sparse clone (java + res)
/root/.buddy/work/teamtalk-xray/ci/overlay # generated overlay
```

Run order: `python3 mkoverlay.py && python3 mkadmin.py && python3 verify.py`.

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Xray: in-app update checker (GitHub release) + CI release publishing.

Run after mkui.py: mkoverlay.py -> mkadmin.py -> mkui.py -> mkupdate.py -> verify.py
"""
import os
import sys

ROOT = '/root/.buddy/work/teamtalk-xray'
OV = ROOT + '/ci/overlay/Client/TeamTalkAndroid/src/main'
RES = OV + '/res'
JAV = OV + '/java'
WORKFLOW = ROOT + '/ci/.github/workflows/build.yml'


def read(p):
    with open(p, encoding='utf-8') as f:
        return f.read()


def write(p, s):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w', encoding='utf-8') as f:
        f.write(s)


def must(c, m):
    if not c:
        print('FAIL:', m)
        sys.exit(1)


UPDATER_JAVA = '''package dk.bearware.gui;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.DialogInterface;
import android.content.Intent;
import android.content.SharedPreferences;
import android.net.Uri;
import android.preference.PreferenceManager;
import android.widget.Toast;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;

/**
 * Checks the latest published GitHub release of the Xray build and offers the APK.
 * Written from scratch for this app (no third party library).
 */
public class XrayUpdater {

    private static final String API =
            "https://api.github.com/repos/hesam-1385/teamtalk-xray/releases/latest";
    private static final String PREFS = "xray_updater";
    private static final String KEY_SEEN = "last_seen_tag";

    public static void check(final Activity activity) {
        Toast.makeText(activity, R.string.xray_update_checking, Toast.LENGTH_SHORT).show();
        new Thread(new Runnable() {
            public void run() {
                String tag = null;
                String apkUrl = null;
                String pageUrl = "https://github.com/hesam-1385/teamtalk-xray/releases";
                String error = null;
                try {
                    HttpURLConnection conn = (HttpURLConnection) new URL(API).openConnection();
                    conn.setRequestProperty("User-Agent", "TeamTalkXray");
                    conn.setRequestProperty("Accept", "application/vnd.github+json");
                    conn.setConnectTimeout(12000);
                    conn.setReadTimeout(12000);
                    int code = conn.getResponseCode();
                    if (code != 200) {
                        throw new IllegalStateException("HTTP " + code);
                    }
                    BufferedReader r = new BufferedReader(
                            new InputStreamReader(conn.getInputStream(), "UTF-8"));
                    StringBuilder sb = new StringBuilder();
                    String line;
                    while ((line = r.readLine()) != null) {
                        sb.append(line);
                    }
                    r.close();
                    JSONObject o = new JSONObject(sb.toString());
                    tag = o.optString("tag_name", "");
                    String html = o.optString("html_url", "");
                    if (html.length() > 0) {
                        pageUrl = html;
                    }
                    JSONArray assets = o.optJSONArray("assets");
                    if (assets != null) {
                        for (int i = 0; i < assets.length(); i++) {
                            JSONObject a = assets.getJSONObject(i);
                            String name = a.optString("name", "");
                            if (name.endsWith(".apk")) {
                                apkUrl = a.optString("browser_download_url", "");
                                break;
                            }
                        }
                    }
                }
                catch (Exception e) {
                    error = e.getMessage() == null ? e.toString() : e.getMessage();
                }
                final String ftag = tag;
                final String fapk = apkUrl;
                final String fpage = pageUrl;
                final String ferr = error;
                activity.runOnUiThread(new Runnable() {
                    public void run() {
                        showResult(activity, ftag, fapk, fpage, ferr);
                    }
                });
            }
        }, "xray-update-check").start();
    }

    private static void showResult(final Activity activity, String tag, final String apkUrl,
            final String pageUrl, String error) {
        if (error != null) {
            Toast.makeText(activity,
                    activity.getString(R.string.xray_update_failed, error),
                    Toast.LENGTH_LONG).show();
            return;
        }
        if (tag == null || tag.length() == 0) {
            Toast.makeText(activity, R.string.xray_update_none, Toast.LENGTH_LONG).show();
            return;
        }
        String current = "";
        try {
            current = activity.getPackageManager()
                    .getPackageInfo(activity.getPackageName(), 0).versionName;
        }
        catch (Exception ignored) {
        }
        SharedPreferences prefs = activity.getSharedPreferences(PREFS, 0);
        prefs.edit().putString(KEY_SEEN, tag).apply();
        String msg = activity.getString(R.string.xray_update_body, current, tag);
        AlertDialog.Builder b = new AlertDialog.Builder(activity);
        b.setTitle(R.string.xray_update_title);
        b.setMessage(msg);
        final String target = (apkUrl != null && apkUrl.length() > 0) ? apkUrl : pageUrl;
        b.setPositiveButton(R.string.xray_update_download, new DialogInterface.OnClickListener() {
            public void onClick(DialogInterface d, int w) {
                try {
                    Intent i = new Intent(Intent.ACTION_VIEW, Uri.parse(target));
                    i.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                    activity.startActivity(i);
                }
                catch (Exception e) {
                    Toast.makeText(activity, R.string.xray_update_none, Toast.LENGTH_LONG).show();
                }
            }
        });
        b.setNegativeButton(R.string.xray_update_close, null);
        b.show();
    }
}
'''

STRINGS = {
    'xray_update_check': ('Check for updates', 'بررسی به‌روزرسانی'),
    'xray_update_checking': ('Checking GitHub…', 'در حال بررسی گیت‌هاب…'),
    'xray_update_title': ('Update', 'به‌روزرسانی'),
    'xray_update_body': ('Installed: %1$s\nLatest build: %2$s\n\nDownload and install the new build?',
                         'نصب‌شده: %1$s\nآخرین نسخه: %2$s\n\nنسخه‌ی جدید دانلود و نصب شود؟'),
    'xray_update_download': ('Download', 'دانلود'),
    'xray_update_close': ('Close', 'بستن'),
    'xray_update_failed': ('Update check failed: %1$s', 'بررسی به‌روزرسانی ناموفق: %1$s'),
    'xray_update_none': ('No published build found', 'نسخه‌ی منتشرشده‌ای پیدا نشد'),
    'xray_hub_update': ('Check for updates', 'بررسی به‌روزرسانی'),
}


def step_java():
    write(JAV + '/dk/bearware/gui/XrayUpdater.java', UPDATER_JAVA)
    print('OK updater java')


def step_strings():
    en = ['<?xml version="1.0" encoding="utf-8"?>\n<resources>']
    fa = ['<?xml version="1.0" encoding="utf-8"?>\n<resources>']
    for k in sorted(STRINGS):
        e, f = STRINGS[k]
        en.append('    <string name="%s">%s</string>' % (k, e))
        fa.append('    <string name="%s">%s</string>' % (k, f))
    en.append('</resources>\n')
    fa.append('</resources>\n')
    write(RES + '/values/xray_update_strings.xml', '\n'.join(en))
    write(RES + '/values-fa-rIR/xray_update_strings.xml', '\n'.join(fa))
    print('OK updater strings (%d)' % len(STRINGS))


def step_hub():
    lay = RES + '/layout/activity_xray_admin.xml'
    must(os.path.exists(lay), 'hub layout missing')
    l = read(lay)
    if 'btn_xray_update' not in l:
        tile = ('        <Button\n'
                '            android:id="@+id/btn_xray_update"\n'
                '            android:layout_width="match_parent"\n'
                '            android:layout_height="64dp"\n'
                '            android:layout_marginTop="8dp"\n'
                '            android:background="@drawable/xray_btn_ghost"\n'
                '            android:text="@string/xray_hub_update"\n'
                '            android:textColor="@color/xray_accent"\n'
                '            android:textSize="17sp" />\n')
        idx = l.rfind('</LinearLayout>')
        must(idx > 0, 'cannot patch hub layout')
        l = l[:idx] + tile + l[idx:]
        write(lay, l)

    p = JAV + '/dk/bearware/gui/XrayAdminActivity.java'
    a = read(p)
    if 'btn_xray_update' not in a:
        anchor = '        View share = findViewById(R.id.btn_xray_share);'
        must(anchor in a, 'cannot find hub share binding')
        block = ('        View upd = findViewById(R.id.btn_xray_update);\n'
                 '        if (upd != null) {\n'
                 '            upd.setOnClickListener(new View.OnClickListener() {\n'
                 '                public void onClick(View view) {\n'
                 '                    XrayUpdater.check(XrayAdminActivity.this);\n'
                 '                }\n'
                 '            });\n'
                 '        }\n')
        a = a.replace(anchor, block + anchor, 1)
        write(p, a)
    print('OK hub: update tile')


def step_workflow():
    w = read(WORKFLOW)
    if 'permissions:' not in w:
        w = w.replace('name: build-teamtalk\n',
                      'name: build-teamtalk\n\npermissions:\n  contents: write\n', 1)
    # Always drop a previous release block first, so the file can never end up
    # with duplicate 'Publish release' steps (duplicate steps are legal, but a
    # duplicated mapping key inside one step makes GitHub reject the workflow).
    idx = w.find('      - name: Publish release')
    if idx > 0:
        w = w[:idx].rstrip('\n') + '\n'
    add = '''
      - name: Publish release
        if: github.ref == 'refs/heads/main'
        continue-on-error: true
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          TAG="build-${GITHUB_RUN_NUMBER}"
          APK=tt/Client/TeamTalkAndroid/build/outputs/apk/debug/TeamTalkAndroid-arm64-v8a-debug.apk
          [ -f "$APK" ] || APK=tt/Client/TeamTalkAndroid/build/outputs/apk/debug/TeamTalkAndroid-universal-debug.apk
          gh release create "$TAG" "$APK" \\
            --title "TeamTalk Xray $TAG" \\
            --notes "Automatic build from ${GITHUB_SHA} (run ${GITHUB_RUN_NUMBER})." \\
            --latest
'''
    w = w.rstrip('\n') + '\n' + add
    # Last line of defence: never emit the same mapping key twice in a step.
    while 'continue-on-error: true\n        continue-on-error: true' in w:
        w = w.replace('continue-on-error: true\n        continue-on-error: true',
                      'continue-on-error: true')
    write(WORKFLOW, w)
    print('OK workflow: releases')


def main():
    step_java()
    step_strings()
    step_hub()
    step_workflow()
    print('UPDATE DONE')


if __name__ == '__main__':
    main()

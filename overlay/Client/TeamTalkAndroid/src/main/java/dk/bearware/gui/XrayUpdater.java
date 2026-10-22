package dk.bearware.gui;

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

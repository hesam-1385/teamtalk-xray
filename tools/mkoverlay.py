#!/usr/bin/env python3
# Generates the Xray overlay (blind-accessibility layer) for TeamTalk5 Android.
import os, re, shutil, sys

SRC = "/root/.buddy/work/teamtalk-xray/src/Client/TeamTalkAndroid"
OVL = "/root/.buddy/work/teamtalk-xray/ci/overlay/Client/TeamTalkAndroid"

def w(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("wrote", path)

def patch(path, old, new, count=1, regex=False):
    with open(path, encoding="utf-8") as f:
        data = f.read()
    if regex:
        new_data, n = re.subn(old, lambda m: new.replace("\\n", "\n"), data, count=count)
    else:
        n = data.count(old)
        if n != count:
            print("!! pattern not found (%d) in %s:\n%s" % (n, path, old[:200]))
            sys.exit(1)
        new_data = data.replace(old, new, count)
    if new_data == data:
        print("!! no change in", path)
        sys.exit(1)
    with open(path, "w", encoding="utf-8") as f:
        f.write(new_data)
    print("patched", path)

JAVA = "src/main/java/dk/bearware/gui"
RES = "src/main/res"

# ---------------------------------------------------------------- XrayA11y.java
XRAY_A11Y = '''package dk.bearware.gui;

import android.app.Activity;
import android.content.Context;
import android.content.SharedPreferences;
import android.os.Build;
import android.os.VibrationEffect;
import android.os.Vibrator;
import android.preference.PreferenceManager;
import android.view.View;
import android.view.accessibility.AccessibilityManager;

/**
 * Xray accessibility layer.
 *
 * TeamTalk shows who joined, who left, who is talking and what was said with
 * icons and colours. A blind user cannot see any of that, so every event is
 * translated into a tactile signature (a small grammar of vibration patterns)
 * and into a spoken announcement through the screen reader. The room becomes
 * something you can feel instead of something you cannot see.
 */
public class XrayA11y {

    /* tactile event types - every one of them has its own vibration pattern */
    public static final int EV_JOIN = 1;
    public static final int EV_LEAVE = 2;
    public static final int EV_MESSAGE = 3;
    public static final int EV_PRIVATE_MESSAGE = 4;
    public static final int EV_SPEAK_START = 5;
    public static final int EV_SPEAK_STOP = 6;
    public static final int EV_ALERT = 7;
    public static final int EV_USER_UPDATE = 8;

    /* preference keys */
    public static final String PREF_ANNOUNCE = "xray_announce";
    public static final String PREF_TACTILE = "xray_tactile";
    public static final String PREF_SPEAK_EVENTS = "xray_speak_events";
    public static final String PREF_CONTRAST = "xray_high_contrast";
    public static final String PREF_FONT_SCALE = "xray_font_scale";

    private final Activity activity;
    private final Vibrator vibrator;
    private final boolean screenReader;

    public XrayA11y(Activity activity) {
        this.activity = activity;
        this.vibrator = (Vibrator) activity.getSystemService(Context.VIBRATOR_SERVICE);
        AccessibilityManager am = (AccessibilityManager) activity.getSystemService(Context.ACCESSIBILITY_SERVICE);
        this.screenReader = am != null && am.isEnabled() && am.isTouchExplorationEnabled();
    }

    public static SharedPreferences prefs(Context ctx) {
        return PreferenceManager.getDefaultSharedPreferences(ctx);
    }

    public static boolean flag(Context ctx, String key, boolean def) {
        return prefs(ctx).getBoolean(key, def);
    }

    /** Extra font scaling factor, 1.0 = system default. */
    public static float fontScale(Context ctx) {
        try {
            String v = prefs(ctx).getString(PREF_FONT_SCALE, "1.0");
            if (v == null)
                return 1.0f;
            return Float.parseFloat(v);
        } catch (Exception e) {
            return 1.0f;
        }
    }

    /** Apply the high contrast theme. Call before super.onCreate(). */
    public static void applyContrastTheme(android.app.Activity act) {
        if (flag(act, PREF_CONTRAST, false))
            act.setTheme(R.style.AppTheme_Xray);
    }

    /**
     * Apply the extra font scale. Call in onCreate() before setContentView().
     */
    public static void applyFontScale(android.app.Activity act) {
        float scale = fontScale(act);
        if (scale > 1.0f) {
            android.content.res.Configuration override =
                    new android.content.res.Configuration(act.getResources().getConfiguration());
            override.fontScale = scale;
            act.applyOverrideConfiguration(override);
        }
    }

    public boolean isScreenReaderActive() {
        return screenReader;
    }

    /** Read a piece of text out loud through the active screen reader. */
    public void announce(String text) {
        if (text == null || text.trim().isEmpty())
            return;
        if (!flag(activity, PREF_ANNOUNCE, true))
            return;
        View root = activity.getWindow() != null ? activity.getWindow().getDecorView() : null;
        if (root != null)
            root.announceForAccessibility(text);
    }

    /** Distinct tactile signature per event type. */
    public void vibrate(int event) {
        if (!flag(activity, PREF_TACTILE, true))
            return;
        if (vibrator == null || !vibrator.hasVibrator())
            return;
        long[] pattern = patternFor(event);
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O)
            vibrator.vibrate(VibrationEffect.createWaveform(pattern, -1));
        else
            vibrator.vibrate(pattern, -1);
    }

    private long[] patternFor(int event) {
        switch (event) {
            case EV_JOIN:            /* two ticks, rising - somebody arrived */
                return new long[] {0, 40, 60, 40};
            case EV_LEAVE:           /* one long pulse - somebody left */
                return new long[] {0, 150};
            case EV_MESSAGE:         /* three ticks - a message */
                return new long[] {0, 25, 45, 25, 45, 25};
            case EV_PRIVATE_MESSAGE: /* two medium pulses - private message */
                return new long[] {0, 60, 50, 60};
            case EV_SPEAK_START:     /* one medium pulse - has the floor */
                return new long[] {0, 70};
            case EV_SPEAK_STOP:      /* one short soft pulse - floor released */
                return new long[] {0, 20};
            case EV_ALERT:           /* urgent triple */
                return new long[] {0, 30, 80, 30, 80, 30};
            case EV_USER_UPDATE:
                return new long[] {0, 15};
            default:
                return new long[] {0, 30};
        }
    }

    /** Announce and vibrate in one call. */
    public void event(int type, String text) {
        announce(text);
        vibrate(type);
    }
}
'''
w(os.path.join(OVL, JAVA, "XrayA11y.java"), XRAY_A11Y)

# ---------------------------------------------------------------- strings
STRINGS_EN = '''<resources>
    <string name="pref_header_xray">Accessibility for blind users</string>
    <string name="pref_cat_xray">Xray feel-the-room layer</string>
    <string name="pref_xray_announce">Announce events with the screen reader</string>
    <string name="pref_xray_announce_sum">Joins, leaves, messages and talking are read out loud</string>
    <string name="pref_xray_tactile">Vibration pattern for every event</string>
    <string name="pref_xray_tactile_sum">Each event has its own tactile signature</string>
    <string name="pref_xray_speak">Announce who starts and stops talking</string>
    <string name="pref_xray_speak_sum">You always know who has the floor</string>
    <string name="pref_xray_contrast">High contrast theme</string>
    <string name="pref_xray_contrast_sum">Black background, bright text, strong focus colour</string>
    <string name="pref_xray_font">Extra large font</string>
    <string name="pref_xray_font_sum">Scales every text in the app</string>
    <string name="xray_joined">%1$s joined channel %2$s</string>
    <string name="xray_left">%1$s left channel %2$s</string>
    <string name="xray_channel_message">Message from %1$s: %2$s</string>
    <string name="xray_private_message">Private message from %1$s: %2$s</string>
    <string name="xray_speaking">%1$s is talking</string>
    <string name="xray_stopped">%1$s stopped talking</string>
    <string name="xray_join_channel">Join channel %1$s</string>
    <string name="xray_message_user">Send a private message to %1$s</string>
    <string name="xray_channel_desc">%1$s, %2$d people, %3$s</string>
</resources>
'''

STRINGS_FA = '''<resources>
    <string name="pref_header_xray">دسترس‌پذیری برای نابیناها</string>
    <string name="pref_cat_xray">لایه حس‌گر Xray</string>
    <string name="pref_xray_announce">اعلام رویدادها با صفحه‌خوان</string>
    <string name="pref_xray_announce_sum">ورود، خروج، پیام و شروع صحبت بلند خوانده می‌شود</string>
    <string name="pref_xray_tactile">الگوی لرزش برای هر رویداد</string>
    <string name="pref_xray_tactile_sum">هر رویداد امضای لمسی مخصوص خودش را دارد</string>
    <string name="pref_xray_speak">اعلام شروع و پایان صحبت</string>
    <string name="pref_xray_speak_sum">همیشه می‌دانی نوبت حرف زدن دست کیست</string>
    <string name="pref_xray_contrast">پوسته کنتراست بالا</string>
    <string name="pref_xray_contrast_sum">پس‌زمینه مشکی، متن روشن، رنگ فوکوس قوی</string>
    <string name="pref_xray_font">فونت خیلی بزرگ</string>
    <string name="pref_xray_font_sum">اندازه همه متن‌های برنامه را تغییر می‌دهد</string>
    <string name="xray_joined">%1$s وارد کانال %2$s شد</string>
    <string name="xray_left">%1$s از کانال %2$s خارج شد</string>
    <string name="xray_channel_message">پیام از %1$s: %2$s</string>
    <string name="xray_private_message">پیام خصوصی از %1$s: %2$s</string>
    <string name="xray_speaking">%1$s دارد صحبت می‌کند</string>
    <string name="xray_stopped">%1$s ساکت شد</string>
    <string name="xray_join_channel">ورود به کانال %1$s</string>
    <string name="xray_message_user">ارسال پیام خصوصی به %1$s</string>
    <string name="xray_channel_desc">%1$s، %2$d نفر، %3$s</string>
</resources>
'''

ARRAYS_EN = '''<resources>
    <string-array name="xray_font_entries">
        <item>Normal</item>
        <item>Large</item>
        <item>Larger</item>
        <item>Largest</item>
    </string-array>
    <string-array name="xray_font_values">
        <item>1.0</item>
        <item>1.15</item>
        <item>1.3</item>
        <item>1.5</item>
    </string-array>
</resources>
'''

ARRAYS_FA = '''<resources>
    <string-array name="xray_font_entries">
        <item>معمولی</item>
        <item>بزرگ</item>
        <item>بزرگ‌تر</item>
        <item>بزرگ‌ترین</item>
    </string-array>
    <string-array name="xray_font_values">
        <item>1.0</item>
        <item>1.15</item>
        <item>1.3</item>
        <item>1.5</item>
    </string-array>
</resources>
'''

w(os.path.join(OVL, RES, "values", "xray_strings.xml"), STRINGS_EN)
w(os.path.join(OVL, RES, "values-fa-rIR", "xray_strings.xml"), STRINGS_FA)
w(os.path.join(OVL, RES, "values", "xray_arrays.xml"), ARRAYS_EN)
w(os.path.join(OVL, RES, "values-fa-rIR", "xray_arrays.xml"), ARRAYS_FA)

# ---------------------------------------------------------------- pref_xray.xml
PREF_XRAY = '''<?xml version="1.0" encoding="utf-8"?>
<PreferenceScreen xmlns:android="http://schemas.android.com/apk/res/android">

    <PreferenceCategory android:title="@string/pref_cat_xray">

        <CheckBoxPreference
            android:key="xray_announce"
            android:title="@string/pref_xray_announce"
            android:summary="@string/pref_xray_announce_sum"
            android:defaultValue="true" />

        <CheckBoxPreference
            android:key="xray_tactile"
            android:title="@string/pref_xray_tactile"
            android:summary="@string/pref_xray_tactile_sum"
            android:defaultValue="true" />

        <CheckBoxPreference
            android:key="xray_speak_events"
            android:title="@string/pref_xray_speak"
            android:summary="@string/pref_xray_speak_sum"
            android:defaultValue="true" />

    </PreferenceCategory>

    <PreferenceCategory android:title="@string/pref_header_xray">

        <CheckBoxPreference
            android:key="xray_high_contrast"
            android:title="@string/pref_xray_contrast"
            android:summary="@string/pref_xray_contrast_sum"
            android:defaultValue="false" />

        <ListPreference
            android:key="xray_font_scale"
            android:title="@string/pref_xray_font"
            android:summary="@string/pref_xray_font_sum"
            android:defaultValue="1.0"
            android:entries="@array/xray_font_entries"
            android:entryValues="@array/xray_font_values" />

    </PreferenceCategory>

</PreferenceScreen>
'''
w(os.path.join(OVL, RES, "xml", "pref_xray.xml"), PREF_XRAY)

# ---------------------------------------------------------------- pref_headers.xml
shutil.copy(os.path.join(SRC, RES, "xml", "pref_headers.xml"),
            os.path.join(OVL, RES, "xml", "pref_headers.xml"))
patch(os.path.join(OVL, RES, "xml", "pref_headers.xml"),
      "    <header\n        android:fragment=\"dk.bearware.gui.PreferencesActivity$AboutPreferenceFragment\"",
      "    <header\n        android:fragment=\"dk.bearware.gui.PreferencesActivity$XrayPreferenceFragment\"\n        android:title=\"@string/pref_header_xray\" />\n"
      "    <header\n        android:fragment=\"dk.bearware.gui.PreferencesActivity$AboutPreferenceFragment\"")

# ---------------------------------------------------------------- styles.xml
STYLES = '''<resources>

    <style name="AppTheme" parent="Theme.AppCompat.DayNight" />

    <style name="AppTheme.NoActionBar" parent="Theme.AppCompat.DayNight">
        <item name="windowActionBar">false</item>
        <item name="windowNoTitle">true</item>
    </style>

    <!-- Xray: high contrast theme for blind and low vision users -->
    <style name="AppTheme.Xray" parent="Theme.AppCompat.DayNight">
        <item name="android:colorBackground">#FF000000</item>
        <item name="android:windowBackground">#FF000000</item>
        <item name="android:textColorPrimary">#FFFFFFFF</item>
        <item name="android:textColorSecondary">#FFFFEB3B</item>
        <item name="android:textColorHint">#FFB0BEC5</item>
        <item name="android:textColorHighlight">#FF00E5FF</item>
        <item name="colorAccent">#FF00E5FF</item>
        <item name="android:textSize">18sp</item>
    </style>

</resources>
'''
w(os.path.join(OVL, RES, "values", "styles.xml"), STYLES)

# ---------------------------------------------------------------- PreferencesActivity.java
pa = os.path.join(OVL, JAVA, "PreferencesActivity.java")
shutil.copy(os.path.join(SRC, JAVA, "PreferencesActivity.java"), pa)
patch(pa,
      "            SoundSystemPreferenceFragment.class.getName().equals(fragmentName) ||",
      "            SoundSystemPreferenceFragment.class.getName().equals(fragmentName) ||\n"
      "            XrayPreferenceFragment.class.getName().equals(fragmentName) ||")
patch(pa,
      "    public static class AboutPreferenceFragment extends PreferenceFragment {",
      "    /**\n"
      "     * Accessibility settings for blind users (Xray feel-the-room layer).\n"
      "     */\n"
      "    public static class XrayPreferenceFragment extends PreferenceFragment {\n"
      "        @Override\n"
      "        public void onCreate(Bundle savedInstanceState) {\n"
      "            super.onCreate(savedInstanceState);\n"
      "            addPreferencesFromResource(R.xml.pref_xray);\n"
      "            bindPreferenceSummaryToValue(findPreference(XrayA11y.PREF_FONT_SCALE));\n"
      "\n"
      "            // font scale and contrast need a fresh activity to take effect\n"
      "            Preference visual = findPreference(XrayA11y.PREF_FONT_SCALE);\n"
      "            if (visual != null) {\n"
      "                visual.setOnPreferenceChangeListener((preference, value) -> {\n"
      "                    sBindPreferenceSummaryToValueListener.onPreferenceChange(preference, value);\n"
      "                    if (getActivity() != null) {\n"
      "                        getActivity().getWindow().getDecorView()\n"
      "                            .post(() -> getActivity().recreate());\n"
      "                    }\n"
      "                    return true;\n"
      "                });\n"
      "            }\n"
      "            Preference contrast = findPreference(XrayA11y.PREF_CONTRAST);\n"
      "            if (contrast != null) {\n"
      "                contrast.setOnPreferenceChangeListener((preference, value) -> {\n"
      "                    if (getActivity() != null) {\n"
      "                        getActivity().getWindow().getDecorView()\n"
      "                            .post(() -> getActivity().recreate());\n"
      "                    }\n"
      "                    return true;\n"
      "                });\n"
      "            }\n"
      "        }\n"
      "    }\n"
      "\n"
      "    public static class AboutPreferenceFragment extends PreferenceFragment {")
patch(pa,
      "    @Override\n    protected void onCreate(Bundle savedInstanceState) {\n        getDelegate().installViewFactory();",
      "    @Override\n"
      "    protected void attachBaseContext(Context newBase) {\n"
      "        super.attachBaseContext(newBase);\n"
      "        float scale = XrayA11y.fontScale(newBase);\n"
      "        if (scale > 1.0f) {\n"
      "            Configuration override = new Configuration(newBase.getResources().getConfiguration());\n"
      "            override.fontScale = scale;\n"
      "            applyOverrideConfiguration(override);\n"
      "        }\n"
      "    }\n"
      "\n"
      "    @Override\n    protected void onCreate(Bundle savedInstanceState) {\n"
      "        if (XrayA11y.flag(this, XrayA11y.PREF_CONTRAST, false))\n"
      "            setTheme(R.style.AppTheme_Xray);\n"
      "        getDelegate().installViewFactory();")

# ---------------------------------------------------------------- MainActivity.java
ma = os.path.join(OVL, JAVA, "MainActivity.java")
shutil.copy(os.path.join(SRC, JAVA, "MainActivity.java"), ma)

patch(ma,
      "    private PrefsHelper prefs;",
      "    private PrefsHelper prefs;\n"
      "    private XrayA11y xray;\n"
      "    private final java.util.HashSet<Integer> xraySpeaking = new java.util.HashSet<>();")

patch(ma,
      "import android.content.Intent;",
      "import android.content.Intent;\nimport android.content.res.Configuration;")

patch(ma,
      "    @Override\n    protected void onCreate(Bundle savedInstanceState) {\n        super.onCreate(savedInstanceState);\n        ctx = getApplicationContext();\n        prefs = new PrefsHelper(ctx);",
      "    @Override\n"
      "    protected void attachBaseContext(Context newBase) {\n"
      "        super.attachBaseContext(newBase);\n"
      "        float scale = XrayA11y.fontScale(newBase);\n"
      "        if (scale > 1.0f) {\n"
      "            Configuration override = new Configuration(newBase.getResources().getConfiguration());\n"
      "            override.fontScale = scale;\n"
      "            applyOverrideConfiguration(override);\n"
      "        }\n"
      "    }\n"
      "\n"
      "    @Override\n"
      "    protected void onCreate(Bundle savedInstanceState) {\n"
      "        if (XrayA11y.flag(this, XrayA11y.PREF_CONTRAST, false))\n"
      "            setTheme(R.style.AppTheme_Xray);\n"
      "        super.onCreate(savedInstanceState);\n"
      "        ctx = getApplicationContext();\n"
      "        prefs = new PrefsHelper(ctx);\n"
      "        xray = new XrayA11y(this);")

# join event
patch(ma,
      "                    if (ttsWrapper != null && prefs.get(\"channel_join_checkbox\", false)) {\n"
      "                        String name = Utils.getDisplayName(getBaseContext(), user);\n"
      "                        ttsWrapper.speak(name + \" \" + getResources().getString(R.string.text_tts_joined_chan));\n"
      "                    }\n"
      "                }\n"
      "                accessibilityAssistant.unlockEvents();",
      "                    if (ttsWrapper != null && prefs.get(\"channel_join_checkbox\", false)) {\n"
      "                        String name = Utils.getDisplayName(getBaseContext(), user);\n"
      "                        ttsWrapper.speak(name + \" \" + getResources().getString(R.string.text_tts_joined_chan));\n"
      "                    }\n"
      "                    if (xray != null) {\n"
      "                        String xrayName = Utils.getDisplayName(getBaseContext(), user);\n"
      "                        Channel jc = getService().getChannels().get(user.nChannelID);\n"
      "                        String jcName = (jc != null) ? jc.szName : \"\";\n"
      "                        int jcPop = Utils.getUsers(user.nChannelID, getService().getUsers()).size();\n"
      "                        xray.event(XrayA11y.EV_JOIN, getString(R.string.xray_joined, xrayName, jcName + \" (\" + jcPop + \")\"));\n"
      "                    }\n"
      "                }\n"
      "                accessibilityAssistant.unlockEvents();")

# leave event
patch(ma,
      "                if (ttsWrapper != null && prefs.get(\"channel_leave_checkbox\", false)) {\n"
      "                    String name = Utils.getDisplayName(getBaseContext(), user);\n"
      "                    ttsWrapper.speak(name + \" \" + getResources().getString(R.string.text_tts_left_chan));\n"
      "                }\n"
      "            }\n"
      "            accessibilityAssistant.unlockEvents();",
      "                if (ttsWrapper != null && prefs.get(\"channel_leave_checkbox\", false)) {\n"
      "                    String name = Utils.getDisplayName(getBaseContext(), user);\n"
      "                    ttsWrapper.speak(name + \" \" + getResources().getString(R.string.text_tts_left_chan));\n"
      "                }\n"
      "                if (xray != null) {\n"
      "                    String xrayName = Utils.getDisplayName(getBaseContext(), user);\n"
      "                    Channel lc = getService().getChannels().get(channelid);\n"
      "                    String lcName = (lc != null) ? lc.szName : \"\";\n"
      "                    int lcPop = Utils.getUsers(channelid, getService().getUsers()).size();\n"
      "                    xray.event(XrayA11y.EV_LEAVE, getString(R.string.xray_left, xrayName, lcName + \" (\" + lcPop + \")\"));\n"
      "                }\n"
      "            }\n"
      "            accessibilityAssistant.unlockEvents();")

# channel message
patch(ma,
      "                if (ttsWrapper != null && prefs.get(\"channel_message_checkbox\", false)) {\n"
      "                    sender = getService().getUsers().get(textmessage.nFromUserID);\n"
      "                    name = Utils.getDisplayName(getBaseContext(), sender);\n"
      "                    ttsWrapper.speak(getString(R.string.text_tts_channel_message, (sender != null) ? name : \"\", completemsg.szMessage));\n"
      "                }\n"
      "            }",
      "                if (ttsWrapper != null && prefs.get(\"channel_message_checkbox\", false)) {\n"
      "                    sender = getService().getUsers().get(textmessage.nFromUserID);\n"
      "                    name = Utils.getDisplayName(getBaseContext(), sender);\n"
      "                    ttsWrapper.speak(getString(R.string.text_tts_channel_message, (sender != null) ? name : \"\", completemsg.szMessage));\n"
      "                }\n"
      "                if (xray != null) {\n"
      "                    sender = getService().getUsers().get(textmessage.nFromUserID);\n"
      "                    name = Utils.getDisplayName(getBaseContext(), sender);\n"
      "                    xray.event(XrayA11y.EV_MESSAGE, getString(R.string.xray_channel_message, (sender != null) ? name : \"\", completemsg.szMessage));\n"
      "                }\n"
      "            }")

# private message
patch(ma,
      "            if (ttsWrapper != null && prefs.get(\"private_message_checkbox\", false))\n"
      "                ttsWrapper.speak(getString(R.string.text_tts_private_message, senderName, completemsg.szMessage));",
      "            if (ttsWrapper != null && prefs.get(\"private_message_checkbox\", false))\n"
      "                ttsWrapper.speak(getString(R.string.text_tts_private_message, senderName, completemsg.szMessage));\n"
      "            if (xray != null)\n"
      "                xray.event(XrayA11y.EV_PRIVATE_MESSAGE, getString(R.string.xray_private_message, senderName, completemsg.szMessage));")

# speaking start/stop
patch(ma,
      r"(public void onUserStateChange\(User user\) \{\s*users\.put\(user\.nUserID, user\);\s*)",
      "public void onUserStateChange(User user) {\\n"
      "        users.put(user.nUserID, user);\n"
      "\n"
      "        // Xray: feel who has the floor\n"
      "        if (xray != null && user.nUserID != getClient().getMyUserID()\n"
      "                && prefs.get(XrayA11y.PREF_SPEAK_EVENTS, true)) {\n"
      "            boolean speaking = (user.uUserState & UserState.USERSTATE_VOICE) != 0;\n"
      "            String xrayName = Utils.getDisplayName(getBaseContext(), user);\n"
      "            if (speaking && !xraySpeaking.contains(user.nUserID)) {\n"
      "                xraySpeaking.add(user.nUserID);\n"
      "                xray.event(XrayA11y.EV_SPEAK_START, getString(R.string.xray_speaking, xrayName));\n"
      "            } else if (!speaking && xraySpeaking.contains(user.nUserID)) {\n"
      "                xraySpeaking.remove(user.nUserID);\n"
      "                xray.event(XrayA11y.EV_SPEAK_STOP, getString(R.string.xray_stopped, xrayName));\n"
      "            }\n"
      "        }\n"
      "        \n",
      regex=True)

# join button content description
patch(ma,
      "                        join.setEnabled(channel.nChannelID != getClient().getMyChannelID());",
      "                        join.setEnabled(channel.nChannelID != getClient().getMyChannelID());\n"
      "                        join.setContentDescription(getString(R.string.xray_join_channel, name.getText()));")

# channel description with population
patch(ma,
      "                        if (channel.nMaxUsers > 0) {\n"
      "                            int population = Utils.getUsers(channel.nChannelID, getService().getUsers()).size();\n"
      "                            ((TextView)convertView.findViewById(R.id.population)).setText((population > 0) ? String.format(Locale.ROOT, \"(%d)\", population) : \"\");\n"
      "                        }",
      "                        if (channel.nMaxUsers > 0) {\n"
      "                            int population = Utils.getUsers(channel.nChannelID, getService().getUsers()).size();\n"
      "                            ((TextView)convertView.findViewById(R.id.population)).setText((population > 0) ? String.format(Locale.ROOT, \"(%d)\", population) : \"\");\n"
      "                        }\n"
      "                        int xrayPop = Utils.getUsers(channel.nChannelID, getService().getUsers()).size();\n"
      "                        name.setContentDescription(getString(R.string.xray_channel_desc, name.getText(), xrayPop, topic.getText()));")

# message button content description
patch(ma,
      "                sndmsg.setAccessibilityDelegate(accessibilityAssistant);",
      "                sndmsg.setAccessibilityDelegate(accessibilityAssistant);\n"
      "                sndmsg.setContentDescription(getString(R.string.xray_message_user, name));")

# ---------------------------------------------------------------- ServerListActivity.java
sl = os.path.join(OVL, JAVA, "ServerListActivity.java")
shutil.copy(os.path.join(SRC, JAVA, "ServerListActivity.java"), sl)
patch(sl,
      "import android.content.SharedPreferences;",
      "import android.content.SharedPreferences;\nimport android.content.res.Configuration;")
patch(sl,
      "    @Override\n    protected void onCreate(Bundle savedInstanceState) {\n        super.onCreate(savedInstanceState);",
      "    @Override\n"
      "    protected void attachBaseContext(Context newBase) {\n"
      "        super.attachBaseContext(newBase);\n"
      "        float scale = XrayA11y.fontScale(newBase);\n"
      "        if (scale > 1.0f) {\n"
      "            Configuration override = new Configuration(newBase.getResources().getConfiguration());\n"
      "            override.fontScale = scale;\n"
      "            applyOverrideConfiguration(override);\n"
      "        }\n"
      "    }\n"
      "\n"
      "    @Override\n"
      "    protected void onCreate(Bundle savedInstanceState) {\n"
      "        if (XrayA11y.flag(this, XrayA11y.PREF_CONTRAST, false))\n"
      "            setTheme(R.style.AppTheme_Xray);\n"
      "        super.onCreate(savedInstanceState);")

print("OK - overlay generated")

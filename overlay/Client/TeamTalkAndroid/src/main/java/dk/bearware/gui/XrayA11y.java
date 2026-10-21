package dk.bearware.gui;

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

package dk.bearware.gui;

import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.media.projection.MediaProjectionManager;
import android.os.Build;

/** Small helper that wires the system screen-capture consent to the recorder service. */
public class XrayScreenCapture {

    public static final int REQUEST_CODE = 4711;

    public static void request(Activity activity) {
        MediaProjectionManager mpm = (MediaProjectionManager)
                activity.getSystemService(Context.MEDIA_PROJECTION_SERVICE);
        if (mpm == null) {
            android.widget.Toast.makeText(activity, R.string.xray_rec_denied,
                    android.widget.Toast.LENGTH_LONG).show();
            return;
        }
        activity.startActivityForResult(mpm.createScreenCaptureIntent(), REQUEST_CODE);
    }

    public static void handleResult(Context ctx, int resultCode, Intent data, boolean share) {
        if (resultCode != Activity.RESULT_OK || data == null) {
            android.widget.Toast.makeText(ctx, R.string.xray_rec_denied,
                    android.widget.Toast.LENGTH_LONG).show();
            return;
        }
        Intent svc = new Intent(ctx, XrayRecorderService.class);
        svc.setAction(XrayRecorderService.ACTION_START);
        svc.putExtra(XrayRecorderService.EXTRA_RESULT_CODE, resultCode);
        svc.putExtra(XrayRecorderService.EXTRA_RESULT_DATA, data);
        svc.putExtra(XrayRecorderService.EXTRA_SHARE, share);
        if (Build.VERSION.SDK_INT >= 26) {
            ctx.startForegroundService(svc);
        }
        else {
            ctx.startService(svc);
        }
    }

    public static void stop(Context ctx) {
        Intent svc = new Intent(ctx, XrayRecorderService.class);
        svc.setAction(XrayRecorderService.ACTION_STOP);
        try {
            ctx.startService(svc);
        }
        catch (Exception e) {
            // service already gone
        }
    }
}

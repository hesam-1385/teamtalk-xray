package dk.bearware.gui;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.Service;
import android.content.Context;
import android.content.Intent;
import android.content.pm.ServiceInfo;
import android.hardware.display.DisplayManager;
import android.hardware.display.VirtualDisplay;
import android.media.MediaRecorder;
import android.media.projection.MediaProjection;
import android.media.projection.MediaProjectionManager;
import android.net.Uri;
import androidx.core.content.FileProvider;
import android.os.Build;
import android.os.Environment;
import android.os.IBinder;
import android.util.DisplayMetrics;
import android.util.Log;
import android.view.WindowManager;

import java.io.File;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;

/**
 * Records the screen (with microphone audio) using MediaProjection.
 * Started by XrayScreenCapture after the system consent dialog.
 */
public class XrayRecorderService extends Service {

    private static final String TAG = "XrayRecorder";
    public static final String ACTION_START = "dk.bearware.gui.xray.REC_START";
    public static final String ACTION_STOP = "dk.bearware.gui.xray.REC_STOP";
    public static final String EXTRA_RESULT_CODE = "xray_result_code";
    public static final String EXTRA_RESULT_DATA = "xray_result_data";
    public static final String EXTRA_SHARE = "xray_share";

    private static final String CHANNEL_ID = "xray_recording";
    private static final int NOTIF_ID = 4711;

    private static volatile boolean running = false;
    private static volatile String lastFile = null;

    private MediaProjection projection;
    private MediaRecorder recorder;
    private VirtualDisplay display;
    private File outFile;
    private boolean shareMode = false;
    private Thread stopper;

    public static boolean isRunning() {
        return running;
    }

    public static String lastFile() {
        return lastFile;
    }

    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        if (intent == null) {
            return START_NOT_STICKY;
        }
        if (ACTION_STOP.equals(intent.getAction())) {
            stopRecording(true);
            return START_NOT_STICKY;
        }
        if (running) {
            return START_STICKY;
        }
        shareMode = intent.getBooleanExtra(EXTRA_SHARE, false);
        createChannel();
        Notification n = buildNotification(getString(shareMode ? R.string.xray_rec_share : R.string.xray_rec_on));
        if (Build.VERSION.SDK_INT >= 29) {
            startForeground(NOTIF_ID, n, ServiceInfo.FOREGROUND_SERVICE_TYPE_MEDIA_PROJECTION);
        }
        else {
            startForeground(NOTIF_ID, n);
        }
        try {
            startRecording(intent);
        }
        catch (Exception e) {
            Log.e(TAG, "cannot start recording", e);
            toast(getString(R.string.xray_rec_failed));
            stopSelf();
        }
        return START_STICKY;
    }

    private void startRecording(Intent intent) throws Exception {
        int resultCode = intent.getIntExtra(EXTRA_RESULT_CODE, 0);
        Intent data;
        if (Build.VERSION.SDK_INT >= 33) {
            data = intent.getParcelableExtra(EXTRA_RESULT_DATA, Intent.class);
        }
        else {
            data = intent.getParcelableExtra(EXTRA_RESULT_DATA);
        }
        if (data == null || resultCode == 0) {
            throw new IllegalStateException("no projection data");
        }
        MediaProjectionManager mpm =
                (MediaProjectionManager) getSystemService(Context.MEDIA_PROJECTION_SERVICE);
        if (mpm == null) {
            throw new IllegalStateException("no media projection service");
        }
        projection = mpm.getMediaProjection(resultCode, data);
        if (projection == null) {
            throw new IllegalStateException("projection denied");
        }
        projection.registerCallback(new MediaProjection.Callback() {
            @Override
            public void onStop() {
                stopRecording(false);
            }
        }, null);

        DisplayMetrics metrics = new DisplayMetrics();
        WindowManager wm = (WindowManager) getSystemService(Context.WINDOW_SERVICE);
        if (wm != null) {
            wm.getDefaultDisplay().getRealMetrics(metrics);
        }
        int width = metrics.widthPixels & ~1;
        int height = metrics.heightPixels & ~1;
        int dpi = metrics.densityDpi;

        File dir = new File(getExternalFilesDir(Environment.DIRECTORY_MOVIES), "TeamTalkXray");
        if (!dir.exists() && !dir.mkdirs()) {
            throw new IllegalStateException("cannot create " + dir);
        }
        String stamp = new SimpleDateFormat("yyyyMMdd-HHmmss", Locale.US).format(new Date());
        outFile = new File(dir, "xray-" + stamp + ".mp4");

        recorder = new MediaRecorder();
        recorder.setAudioSource(MediaRecorder.AudioSource.MIC);
        recorder.setVideoSource(MediaRecorder.VideoSource.SURFACE);
        recorder.setOutputFormat(MediaRecorder.OutputFormat.MPEG_4);
        recorder.setVideoEncoder(MediaRecorder.VideoEncoder.H264);
        recorder.setAudioEncoder(MediaRecorder.AudioEncoder.AAC);
        recorder.setVideoSize(width, height);
        recorder.setVideoFrameRate(30);
        recorder.setVideoEncodingBitRate(6000000);
        recorder.setAudioEncodingBitRate(128000);
        recorder.setAudioSamplingRate(44100);
        recorder.setOutputFile(outFile.getAbsolutePath());
        recorder.prepare();
        display = projection.createVirtualDisplay("xray-recording", width, height, dpi,
                DisplayManager.VIRTUAL_DISPLAY_FLAG_AUTO_MIRROR, recorder.getSurface(), null, null);
        recorder.start();
        running = true;
        Log.i(TAG, "recording to " + outFile);
    }

    public void stopRecording(boolean notifyUser) {
        if (!running && recorder == null) {
            return;
        }
        running = false;
        try {
            if (recorder != null) {
                recorder.stop();
            }
        }
        catch (Exception e) {
            Log.w(TAG, "recorder stop failed", e);
        }
        try {
            if (recorder != null) {
                recorder.release();
            }
        }
        catch (Exception ignored) {
        }
        recorder = null;
        try {
            if (display != null) {
                display.release();
            }
        }
        catch (Exception ignored) {
        }
        display = null;
        try {
            if (projection != null) {
                projection.stop();
            }
        }
        catch (Exception ignored) {
        }
        projection = null;
        if (outFile != null && outFile.exists()) {
            lastFile = outFile.getAbsolutePath();
            try {
                sendBroadcast(new Intent(Intent.ACTION_MEDIA_SCANNER_SCAN_FILE,
                        Uri.fromFile(outFile)));
            }
            catch (Exception ignored) {
            }
            if (notifyUser) {
                toast(getString(R.string.xray_rec_saved, lastFile));
                if (shareMode) {
                    try {
                        Intent send = new Intent(Intent.ACTION_SEND);
                        android.net.Uri shareUri = FileProvider.getUriForFile(this,
                                getPackageName() + ".xrayfiles", outFile);
                        send.setType("video/mp4");
                        send.putExtra(Intent.EXTRA_STREAM, shareUri);
                        send.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
                        Intent chooser = Intent.createChooser(send,
                                getString(R.string.xray_rec_share_chooser));
                        chooser.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                        startActivity(chooser);
                    }
                    catch (Exception e) {
                        Log.w(TAG, "no share target", e);
                    }
                }
            }
        }
        stopForeground(true);
        stopSelf();
    }

    private void toast(final String msg) {
        android.os.Handler h = new android.os.Handler(getMainLooper());
        h.post(new Runnable() {
            @Override
            public void run() {
                android.widget.Toast.makeText(getApplicationContext(), msg,
                        android.widget.Toast.LENGTH_LONG).show();
            }
        });
    }

    private void createChannel() {
        if (Build.VERSION.SDK_INT >= 26) {
            NotificationManager nm =
                    (NotificationManager) getSystemService(Context.NOTIFICATION_SERVICE);
            if (nm != null && nm.getNotificationChannel(CHANNEL_ID) == null) {
                NotificationChannel ch = new NotificationChannel(CHANNEL_ID,
                        getString(R.string.xray_rec_channel), NotificationManager.IMPORTANCE_LOW);
                ch.setShowBadge(false);
                nm.createNotificationChannel(ch);
            }
        }
    }

    private Notification buildNotification(String text) {
        Intent open = new Intent(this, MainActivity.class);
        int flags = PendingIntent.FLAG_UPDATE_CURRENT;
        if (Build.VERSION.SDK_INT >= 23) {
            flags |= PendingIntent.FLAG_IMMUTABLE;
        }
        PendingIntent content = PendingIntent.getActivity(this, 0, open, flags);
        Intent stop = new Intent(this, XrayRecorderService.class).setAction(ACTION_STOP);
        PendingIntent stopPi = PendingIntent.getService(this, 1, stop, flags);
        Notification.Builder b;
        if (Build.VERSION.SDK_INT >= 26) {
            b = new Notification.Builder(this, CHANNEL_ID);
        }
        else {
            b = new Notification.Builder(this);
        }
        b.setSmallIcon(android.R.drawable.presence_video_online)
                .setContentTitle(getString(R.string.xray_rec_channel))
                .setContentText(text)
                .setOngoing(true)
                .setContentIntent(content)
                .addAction(new Notification.Action.Builder(
                        android.graphics.drawable.Icon.createWithResource(this,
                                android.R.drawable.ic_media_pause),
                        getString(R.string.xray_rec_stop_action), stopPi).build());
        return b.build();
    }

    @Override
    public void onDestroy() {
        if (running) {
            stopRecording(false);
        }
        super.onDestroy();
    }
}

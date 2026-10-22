package dk.bearware.gui;

import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.graphics.PixelFormat;
import android.hardware.display.DisplayManager;
import android.hardware.display.VirtualDisplay;
import android.media.Image;
import android.media.ImageReader;
import android.media.projection.MediaProjection;
import android.media.projection.MediaProjectionManager;
import android.os.Build;
import android.os.Handler;
import android.os.HandlerThread;
import android.os.SystemClock;
import android.util.DisplayMetrics;
import android.util.Log;
import android.view.WindowManager;
import android.widget.Toast;

import java.nio.ByteBuffer;

import dk.bearware.BitmapFormat;
import dk.bearware.Channel;
import dk.bearware.DesktopProtocol;
import dk.bearware.DesktopWindow;
import dk.bearware.StreamType;
import dk.bearware.TeamTalkBase;
import dk.bearware.User;

/**
 * Live desktop sharing: captures the Android screen with MediaProjection and pumps
 * RGB32 frames into the TeamTalk channel through TT_SendDesktopWindow.
 */
public class XrayDesktopShare {

    private static final String TAG = "XrayDesktopShare";
    public static final int REQUEST_CODE = 47921;
    private static final int MAX_WIDTH = 720;
    private static final int MIN_FRAME_GAP_MS = 110;

    private static volatile XrayDesktopShare instance;
    static volatile TeamTalkBase pendingClient;

    private final TeamTalkBase client;
    private MediaProjection projection;
    private VirtualDisplay display;
    private ImageReader reader;
    private HandlerThread thread;
    private Handler handler;
    private int width;
    private int height;
    private byte[] frame;
    private long nextFrameAt;
    private long frames;
    private volatile boolean running;

    private XrayDesktopShare(TeamTalkBase client) {
        this.client = client;
    }

    public static boolean isSharing() {
        XrayDesktopShare s = instance;
        return s != null && s.running;
    }

    public static void request(Activity activity, TeamTalkBase client) {
        if (client == null) {
            Toast.makeText(activity, R.string.xray_share_failed, Toast.LENGTH_LONG).show();
            return;
        }
        int channelId = client.getMyChannelID();
        if (channelId <= 0) {
            Toast.makeText(activity, R.string.xray_share_need_channel, Toast.LENGTH_LONG).show();
            return;
        }
        try {
            Channel channel = new Channel();
            User me = new User();
            if (client.getChannel(channelId, channel) && client.getUser(client.getMyUserID(), me)) {
                if (!Utils.isTransmitAllowed(me, channel, StreamType.STREAMTYPE_DESKTOP)) {
                    Utils.toggleTransmitUsers(me, channel, StreamType.STREAMTYPE_DESKTOP, true);
                    client.doUpdateChannel(channel);
                }
            }
        }
        catch (Exception e) {
            Log.w(TAG, "cannot allow desktop transmit", e);
        }
        pendingClient = client;
        MediaProjectionManager mpm =
                (MediaProjectionManager) activity.getSystemService(Context.MEDIA_PROJECTION_SERVICE);
        if (mpm == null) {
            Toast.makeText(activity, R.string.xray_share_failed, Toast.LENGTH_LONG).show();
            return;
        }
        activity.startActivityForResult(mpm.createScreenCaptureIntent(), REQUEST_CODE);
    }

    public static boolean start(Context ctx, TeamTalkBase client, int resultCode, Intent data) {
        stop();
        if (client == null || data == null || resultCode != Activity.RESULT_OK) {
            return false;
        }
        XrayDesktopShare s = new XrayDesktopShare(client);
        boolean ok = s.begin(ctx, resultCode, data);
        if (ok) {
            instance = s;
            Log.i(TAG, "desktop share started " + s.width + "x" + s.height);
        }
        return ok;
    }

    public static void stop() {
        XrayDesktopShare s = instance;
        instance = null;
        if (s != null) {
            s.finish();
        }
    }

    private boolean begin(Context ctx, int resultCode, Intent data) {
        try {
            MediaProjectionManager mpm = (MediaProjectionManager)
                    ctx.getSystemService(Context.MEDIA_PROJECTION_SERVICE);
            projection = mpm.getMediaProjection(resultCode, data);
            if (projection == null) {
                return false;
            }
            DisplayMetrics metrics = new DisplayMetrics();
            WindowManager wm = (WindowManager) ctx.getSystemService(Context.WINDOW_SERVICE);
            if (wm != null) {
                wm.getDefaultDisplay().getRealMetrics(metrics);
            }
            int sw = Math.min(MAX_WIDTH, metrics.widthPixels);
            int sh = (int) ((long) metrics.heightPixels * sw / Math.max(1, metrics.widthPixels));
            width = sw & ~1;
            height = sh & ~1;
            frame = new byte[width * height * 4];
            thread = new HandlerThread("xray-desktop");
            thread.start();
            handler = new Handler(thread.getLooper());
            reader = ImageReader.newInstance(width, height, PixelFormat.RGBA_8888, 2);
            reader.setOnImageAvailableListener(new ImageReader.OnImageAvailableListener() {
                public void onImageAvailable(ImageReader r) {
                    grab(r);
                }
            }, handler);
            display = projection.createVirtualDisplay("xray-desktop", width, height,
                    metrics.densityDpi,
                    DisplayManager.VIRTUAL_DISPLAY_FLAG_AUTO_MIRROR,
                    reader.getSurface(), null, handler);
            running = true;
            return true;
        }
        catch (Exception e) {
            Log.e(TAG, "cannot start", e);
            finish();
            return false;
        }
    }

    private void grab(ImageReader r) {
        Image img = null;
        try {
            img = r.acquireLatestImage();
        }
        catch (Exception e) {
            return;
        }
        if (img == null) {
            return;
        }
        try {
            long now = SystemClock.elapsedRealtime();
            if (now < nextFrameAt) {
                return;
            }
            nextFrameAt = now + MIN_FRAME_GAP_MS;
            Image.Plane plane = img.getPlanes()[0];
            ByteBuffer buffer = plane.getBuffer();
            int rowStride = plane.getRowStride();
            int pixelStride = plane.getPixelStride();
            int base = buffer.position();
            if (pixelStride == 4 && rowStride == width * 4) {
                buffer.position(base);
                int n = Math.min(frame.length, buffer.remaining());
                buffer.get(frame, 0, n);
                for (int i = 0; i + 3 < frame.length; i += 4) {
                    byte t = frame[i];
                    frame[i] = frame[i + 2];
                    frame[i + 2] = t;
                }
            }
            else {
                byte[] row = new byte[rowStride];
                int dst = 0;
                for (int y = 0; y < height; y++) {
                    buffer.position(base + y * rowStride);
                    int n = Math.min(rowStride, buffer.remaining());
                    if (n <= 0) {
                        break;
                    }
                    buffer.get(row, 0, n);
                    for (int x = 0; x < width; x++) {
                        int src = x * pixelStride;
                        frame[dst++] = row[src + 2];
                        frame[dst++] = row[src + 1];
                        frame[dst++] = row[src];
                        frame[dst++] = (byte) 0xFF;
                    }
                }
            }
            if (client != null && client.getMyChannelID() > 0) {
                DesktopWindow wnd = new DesktopWindow();
                wnd.nWidth = width;
                wnd.nHeight = height;
                wnd.bmpFormat = BitmapFormat.BMP_RGB32;
                wnd.nBytesPerLine = width * 4;
                wnd.nSessionID = 0;
                wnd.nProtocol = DesktopProtocol.DESKTOPPROTOCOL_ZLIB_1;
                wnd.frameBuffer = frame;
                client.sendDesktopWindow(wnd, BitmapFormat.BMP_RGB32);
                frames++;
            }
        }
        catch (Exception e) {
            Log.w(TAG, "frame dropped", e);
        }
        finally {
            try {
                img.close();
            }
            catch (Exception ignored) {
            }
        }
    }

    private void finish() {
        running = false;
        try {
            if (client != null) {
                client.closeDesktopWindow();
            }
        }
        catch (Exception ignored) {
        }
        try {
            if (display != null) {
                display.release();
            }
        }
        catch (Exception ignored) {
        }
        display = null;
        try {
            if (reader != null) {
                reader.close();
            }
        }
        catch (Exception ignored) {
        }
        reader = null;
        try {
            if (projection != null) {
                projection.stop();
            }
        }
        catch (Exception ignored) {
        }
        projection = null;
        if (thread != null) {
            thread.quitSafely();
            thread = null;
        }
        handler = null;
        Log.i(TAG, "desktop share stopped after " + frames + " frames");
    }

    /** Foreground service used while the projection is alive (required since Android 14). */
    public static class ShareService extends android.app.Service {

        public static final String ACTION_START = "dk.bearware.gui.xray.SHARE_START";
        public static final String ACTION_STOP = "dk.bearware.gui.xray.SHARE_STOP";
        public static final String EXTRA_RESULT_CODE = "xray_share_code";
        public static final String EXTRA_RESULT_DATA = "xray_share_data";
        private static final String CHANNEL_ID = "xray_share";
        private static final int NOTIF_ID = 4712;

        public static void startWithResult(Context ctx, TeamTalkBase client, int resultCode, Intent data) {
            pendingClient = client;
            Intent svc = new Intent(ctx, ShareService.class);
            svc.setAction(ACTION_START);
            svc.putExtra(EXTRA_RESULT_CODE, resultCode);
            svc.putExtra(EXTRA_RESULT_DATA, data);
            if (Build.VERSION.SDK_INT >= 26) {
                ctx.startForegroundService(svc);
            }
            else {
                ctx.startService(svc);
            }
        }

        public static void requestStop(Context ctx) {
            Intent svc = new Intent(ctx, ShareService.class);
            svc.setAction(ACTION_STOP);
            try {
                ctx.startService(svc);
            }
            catch (Exception ignored) {
            }
            XrayDesktopShare.stop();
        }

        @Override
        public android.os.IBinder onBind(Intent intent) {
            return null;
        }

        @Override
        public int onStartCommand(Intent intent, int flags, int startId) {
            if (intent == null) {
                return START_NOT_STICKY;
            }
            if (ACTION_STOP.equals(intent.getAction())) {
                stopSharing();
                return START_NOT_STICKY;
            }
            createChannel();
            android.app.Notification n = buildNotification();
            if (Build.VERSION.SDK_INT >= 29) {
                startForeground(NOTIF_ID, n,
                        android.content.pm.ServiceInfo.FOREGROUND_SERVICE_TYPE_MEDIA_PROJECTION);
            }
            else {
                startForeground(NOTIF_ID, n);
            }
            int code = intent.getIntExtra(EXTRA_RESULT_CODE, 0);
            Intent data;
            if (Build.VERSION.SDK_INT >= 33) {
                data = intent.getParcelableExtra(EXTRA_RESULT_DATA, Intent.class);
            }
            else {
                data = intent.getParcelableExtra(EXTRA_RESULT_DATA);
            }
            boolean ok = XrayDesktopShare.start(this, pendingClient, code, data);
            if (!ok) {
                toast(getString(R.string.xray_share_failed));
                stopSharing();
            }
            else {
                toast(getString(R.string.xray_share_on));
            }
            return START_NOT_STICKY;
        }

        private void stopSharing() {
            XrayDesktopShare.stop();
            stopForeground(true);
            stopSelf();
        }

        private void toast(final String msg) {
            new Handler(getMainLooper()).post(new Runnable() {
                public void run() {
                    Toast.makeText(getApplicationContext(), msg, Toast.LENGTH_SHORT).show();
                }
            });
        }

        private void createChannel() {
            if (Build.VERSION.SDK_INT >= 26) {
                android.app.NotificationManager nm = (android.app.NotificationManager)
                        getSystemService(Context.NOTIFICATION_SERVICE);
                if (nm != null && nm.getNotificationChannel(CHANNEL_ID) == null) {
                    android.app.NotificationChannel ch = new android.app.NotificationChannel(
                            CHANNEL_ID, getString(R.string.xray_share_channel),
                            android.app.NotificationManager.IMPORTANCE_LOW);
                    ch.setShowBadge(false);
                    nm.createNotificationChannel(ch);
                }
            }
        }

        private android.app.Notification buildNotification() {
            Intent open = new Intent(this, MainActivity.class);
            int flags = android.app.PendingIntent.FLAG_UPDATE_CURRENT;
            if (Build.VERSION.SDK_INT >= 23) {
                flags |= android.app.PendingIntent.FLAG_IMMUTABLE;
            }
            android.app.PendingIntent content =
                    android.app.PendingIntent.getActivity(this, 0, open, flags);
            Intent stop = new Intent(this, ShareService.class).setAction(ACTION_STOP);
            android.app.PendingIntent stopPi =
                    android.app.PendingIntent.getService(this, 1, stop, flags);
            android.app.Notification.Builder b;
            if (Build.VERSION.SDK_INT >= 26) {
                b = new android.app.Notification.Builder(this, CHANNEL_ID);
            }
            else {
                b = new android.app.Notification.Builder(this);
            }
            b.setSmallIcon(android.R.drawable.presence_video_online)
                    .setContentTitle(getString(R.string.xray_share_channel))
                    .setContentText(getString(R.string.xray_share_alive))
                    .setOngoing(true)
                    .setContentIntent(content);
            b.addAction(new android.app.Notification.Action.Builder(
                    android.graphics.drawable.Icon.createWithResource(this,
                            android.R.drawable.ic_media_pause),
                    getString(R.string.xray_share_stop_action), stopPi).build());
            return b.build();
        }

        @Override
        public void onDestroy() {
            XrayDesktopShare.stop();
            super.onDestroy();
        }
    }
}

package dk.bearware.gui;

import android.content.Context;
import android.content.Intent;
import android.graphics.Typeface;
import android.os.Bundle;
import android.view.ViewGroup;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;

import androidx.appcompat.app.AppCompatActivity;

import dk.bearware.ClientStatistics;
import dk.bearware.ServerProperties;
import dk.bearware.TeamTalkBase;
import dk.bearware.backend.TeamTalkConnection;
import dk.bearware.backend.TeamTalkConnectionListener;
import dk.bearware.backend.TeamTalkService;

/**
 * Live information about the server the user is connected to.
 * The TeamTalk 5 client API of this build has no server statistics
 * query, so the real server properties plus the real client counters
 * are shown instead.
 */
public class XrayServerInfoActivity extends AppCompatActivity implements TeamTalkConnectionListener {

    private TeamTalkConnection mConnection;
    private LinearLayout root;

    @Override
    protected void attachBaseContext(Context base) {
        super.attachBaseContext(base);
        float scale = XrayA11y.fontScale(base);
        if (scale > 1.0f) {
            android.content.res.Configuration override =
                    new android.content.res.Configuration(base.getResources().getConfiguration());
            override.fontScale = scale;
            applyOverrideConfiguration(override);
        }
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        if (XrayA11y.flag(this, XrayA11y.PREF_CONTRAST, false))
            setTheme(R.style.AppTheme_Xray);
        super.onCreate(savedInstanceState);

        ScrollView scroll = new ScrollView(this);
        root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        int pad = (int) (16 * getResources().getDisplayMetrics().density);
        root.setPadding(pad, pad, pad, pad);
        scroll.addView(root, new ViewGroup.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.WRAP_CONTENT));
        setContentView(scroll);

        addHeader(getString(R.string.xray_server_info));
        addLine(getString(R.string.xray_not_connected));
    }

    private void addHeader(String text) {
        TextView tv = new TextView(this);
        tv.setText(text);
        tv.setTextSize(22f);
        tv.setTypeface(null, Typeface.BOLD);
        tv.setContentDescription(text);
        root.addView(tv);
    }

    private void addLine(String text) {
        TextView tv = new TextView(this);
        tv.setText(text);
        tv.setTextSize(18f);
        tv.setContentDescription(text);
        tv.setPadding(0, 12, 0, 12);
        root.addView(tv);
    }

    @Override
    protected void onStart() {
        super.onStart();
        mConnection = new TeamTalkConnection(this);
        Intent intent = new Intent(this, TeamTalkService.class);
        bindService(intent, mConnection, Context.BIND_AUTO_CREATE);
    }

    @Override
    protected void onStop() {
        if (mConnection != null && mConnection.isBound()) {
            unbindService(mConnection);
            mConnection.setBound(false);
        }
        super.onStop();
    }

    @Override
    public void onServiceConnected(TeamTalkService service) {
        TeamTalkBase client = service.getTTInstance();
        if (client == null) return;
        ServerProperties prop = new ServerProperties();
        if (client.getServerProperties(prop)) {
            addLine(getString(R.string.xray_srv_name) + ": " + str(prop.szServerName));
            addLine(getString(R.string.xray_srv_version) + ": " + str(prop.szServerVersion));
            addLine(getString(R.string.xray_srv_motd) + ": " + str(prop.szMOTD));
            addLine(getString(R.string.xray_srv_max_users) + ": " + prop.nMaxUsers);
            addLine(getString(R.string.xray_srv_max_logins_ip) + ": " + prop.nMaxLoginsPerIPAddress);
            addLine(getString(R.string.xray_srv_login_delay) + ": " + prop.nLoginDelayMSec);
            addLine(getString(R.string.xray_srv_user_timeout) + ": " + prop.nUserTimeout);
            addLine(getString(R.string.xray_srv_ports) + ": " + prop.nTcpPort + " / " + prop.nUdpPort);
            addLine(getString(R.string.xray_srv_autosave) + ": " + (prop.bAutoSave ? "yes" : "no"));
        }
        ClientStatistics stats = new ClientStatistics();
        if (client.getClientStatistics(stats)) {
            addHeader(getString(R.string.xray_conn_stats));
            addLine(getString(R.string.xray_conn_ping) + ": " + stats.nTcpPingTimeMs + " / " + stats.nUdpPingTimeMs);
            addLine(getString(R.string.xray_conn_bytes) + ": " + stats.nUdpBytesSent + " / " + stats.nUdpBytesRecv);
            addLine("voice: " + stats.nVoiceBytesSent + " / " + stats.nVoiceBytesRecv);
            addLine("video: " + stats.nVideoCaptureBytesSent + " / " + stats.nVideoCaptureBytesRecv);
        }
    }

    private String str(String s) {
        return s == null || s.isEmpty() ? "-" : s;
    }

    @Override
    public void onServiceDisconnected(TeamTalkService service) {
    }
}

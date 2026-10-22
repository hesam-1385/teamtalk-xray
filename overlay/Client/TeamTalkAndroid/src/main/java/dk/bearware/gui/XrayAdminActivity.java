package dk.bearware.gui;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.TextView;

import androidx.appcompat.app.AppCompatActivity;

/**
 * Blind friendly hub for the server administration tools.
 * Every entry is a big button with a spoken label so it can be used
 * with TalkBack without seeing the screen.
 */
public class XrayAdminActivity extends AppCompatActivity {

    @Override
    protected void attachBaseContext(android.content.Context base) {
        super.attachBaseContext(base);
        float scale = XrayA11y.fontScale(base);
        if (scale > 1.0f) {
            android.content.res.Configuration override = new android.content.res.Configuration(base.getResources().getConfiguration());
            override.fontScale = scale;
            applyOverrideConfiguration(override);
        }
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        if (XrayA11y.flag(this, XrayA11y.PREF_CONTRAST, false))
            setTheme(R.style.AppTheme_Xray);
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_xray_admin);

        bind(R.id.btn_xray_user_accounts, UserAccountsActivity.class);
        bind(R.id.btn_xray_server_props, ServerPropActivity.class);
        bind(R.id.btn_xray_server_info, XrayServerInfoActivity.class);
        bind(R.id.btn_xray_move_users, MoveUsersActivity.class);
        bind(R.id.btn_xray_channel_bans, ChannelBannedUsersActivity.class);
        bind(R.id.btn_xray_server_bans, ServerBannedUsersActivity.class);

        TextView title = (TextView) findViewById(R.id.txt_xray_admin_title);
        title.setContentDescription(getString(R.string.xray_admin));
        title.postDelayed(new Runnable() {
            public void run() {
                title.announceForAccessibility(getString(R.string.xray_admin));
            }
        }, 400);

        View upd = findViewById(R.id.btn_xray_update);
        if (upd != null) {
            upd.setOnClickListener(new View.OnClickListener() {
                public void onClick(View view) {
                    XrayUpdater.check(XrayAdminActivity.this);
                }
            });
        }
        View share = findViewById(R.id.btn_xray_share);
        if (share != null) {
            share.setOnClickListener(new View.OnClickListener() {
                public void onClick(View view) {
                    if (XrayDesktopShare.isSharing()) {
                        XrayDesktopShare.ShareService.requestStop(XrayAdminActivity.this);
                    }
                    else {
                        XrayDesktopShare.request(XrayAdminActivity.this,
                                MainActivity.activeClient());
                    }
                }
            });
        }
    }

    private void bind(int id, final Class<?> cls) {
        View v = findViewById(id);
        v.setOnClickListener(new View.OnClickListener() {
            public void onClick(View view) {
                startActivity(new Intent(XrayAdminActivity.this, cls));
            }
        });
    }

    @Override
    protected void onStart() {
        super.onStart();
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, android.content.Intent data) {
        if (requestCode == XrayDesktopShare.REQUEST_CODE) {
            if (resultCode == RESULT_OK && data != null) {
                XrayDesktopShare.ShareService.startWithResult(this,
                        MainActivity.activeClient(), resultCode, data);
            }
            else {
                android.widget.Toast.makeText(this, R.string.xray_share_denied,
                        android.widget.Toast.LENGTH_LONG).show();
            }
            return;
        }
        super.onActivityResult(requestCode, resultCode, data);
    }
}

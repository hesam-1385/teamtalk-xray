#!/usr/bin/env python3
# Xray admin port: ports TeamTalkPlus admin features into upstream TeamTalk5 Android app
# (as an overlay applied by GitHub Actions CI). Idempotent.
import os, re, sys, shutil

ROOT = '/root/.buddy/work/teamtalk-xray'
SRC = ROOT + '/src/Client/TeamTalkAndroid'
TTP = ROOT + '/ttp/src/main'
OV = ROOT + '/ci/overlay/Client/TeamTalkAndroid'
JAV = OV + '/src/main/java/dk/bearware'
RES = OV + '/src/main/res'

def read(p):
    with open(p, encoding='utf-8') as f: return f.read()

def write(p, s):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w', encoding='utf-8') as f: f.write(s)

def must(c, m):
    if not c:
        print('FAIL:', m); sys.exit(1)

def extract_block(src, sig, label):
    m = re.search(sig, src)
    must(m is not None, 'cannot find block ' + label)
    i = src.find('{', m.end())
    depth = 0; j = i
    while j < len(src):
        if src[j] == '{': depth += 1
        elif src[j] == '}':
            depth -= 1
            if depth == 0:
                return src[m.start():j+1]
        j += 1
    must(False, 'unbalanced block ' + label)

def parse_strings(path):
    """name -> inner xml (raw)"""
    out = {}
    if not os.path.exists(path): return out
    txt = read(path)
    for m in re.finditer(r'<string\s+name="([^"]+)"([^>]*)>(.*?)</string>', txt, re.S):
        if m.group(1) not in out:
            out[m.group(1)] = m.group(3)
    return out

def parse_plurals(path):
    """name -> inner xml of the <plurals> block"""
    out = {}
    if not os.path.exists(path): return out
    txt = read(path)
    for m in re.finditer(r'<plurals\s+name="([^"]+)"[^>]*>(.*?)</plurals>', txt, re.S):
        out[m.group(1)] = m.group(2)
    return out

def defined_names(path):
    if not os.path.exists(path): return set()
    return set(parse_strings(path).keys())

def all_names_in_res_dir(d):
    names = set()
    if not os.path.isdir(d): return names
    for f in os.listdir(d):
        if f.endswith('.xml'):
            names |= defined_names(os.path.join(d, f))
    return names

# ---------------------------------------------------------------- 1. Utils overlay
def step_utils():
    up = read(SRC + '/src/main/java/dk/bearware/gui/Utils.java')
    tt = read(TTP + '/java/dk/bearware/gui/Utils.java')
    blocks = []
    for sig, label in [
        (r'public static void announceAccessibilityTitle\(android\.app\.Activity activity', 'announceAccessibilityTitle'),
        (r'public static boolean sameBan\(', 'sameBan'),
        (r'public static Vector<User> getUsers\(int chanid, Map<Integer, User> users, boolean recursive', 'getUsers4'),
        (r'private static void fillSubChannelIds\(', 'fillSubChannelIds'),
        (r'public static boolean hasSubChannels\(', 'hasSubChannels'),
        (r'private static void writeTrustedCertificate\(', 'writeTrustedCertificate'),
        (r'public static String generateServerEntryXml\(', 'generateServerEntryXml'),
        (r'public static boolean saveTTFileToDownloads\(', 'saveTTFileToDownloads'),
        (r'public interface OnChannelSelectedListener', 'OnChannelSelectedListener'),
        (r'public static void showChannelPicker\(', 'showChannelPicker'),
    ]:
        blocks.append(extract_block(tt, sig, label))
    # avoid duplicates with upstream definitions
    for name in ['announceAccessibilityTitle', 'sameBan', 'hasSubChannels', 'fillSubChannelIds',
                 'writeTrustedCertificate', 'generateServerEntryXml', 'saveTTFileToDownloads',
                 'showChannelPicker', 'OnChannelSelectedListener']:
        must((' ' + name + '(') not in up.replace('public static void ' + name, ''), 'upstream Utils already has ' + name)
    imports = ['android.content.ContentValues', 'android.provider.MediaStore', 'android.net.Uri',
               'java.io.OutputStream', 'java.nio.charset.StandardCharsets',
               'androidx.appcompat.app.AlertDialog', 'java.util.ArrayList', 'java.util.Collections',
               'java.util.HashSet', 'java.util.List', 'java.util.Objects', 'java.util.Set',
               'java.util.Locale', 'dk.bearware.backend.TeamTalkService']
    lines = up.split('\n')
    out = []
    for ln in lines:
        if ln.startswith('import ') and ln.endswith(';'):
            pkg = ln[len('import '):-1]
            if pkg in imports and ('import %s;' % pkg) not in up:
                out.append(ln); continue
        out.append(ln)
    up = '\n'.join(out)
    for imp in imports:
        if ('import %s;' % imp) not in up:
            # insert after last import line
            idx = up.rfind('\nimport ')
            end = up.index('\n', idx + 1)
            up = up[:end + 1] + 'import %s;\n' % imp + up[end + 1:]
    # append methods before final closing brace
    idx = up.rfind('}')
    up = up[:idx] + '\n' + '\n\n'.join(blocks) + '\n' + up[idx:]
    write(JAV + '/gui/Utils.java', up)
    print('OK Utils.java overlay (+%d methods)' % len(blocks))

# ---------------------------------------------------------------- 2. TTP admin java
ADMIN_JAVA = [
    ('gui/UserAccountsActivity.java', 'gui/UserAccountsActivity.java'),
    ('gui/UserAccountEditActivity.java', 'gui/UserAccountEditActivity.java'),
    ('gui/ServerPropActivity.java', 'gui/ServerPropActivity.java'),
    ('gui/MoveUsersActivity.java', 'gui/MoveUsersActivity.java'),
    ('gui/ChannelBannedUsersActivity.java', 'gui/ChannelBannedUsersActivity.java'),
    ('gui/ServerBannedUsersActivity.java', 'gui/ServerBannedUsersActivity.java'),
    ('gui/BannedUsersAdapter.java', 'gui/BannedUsersAdapter.java'),
]

STALE_FILES = [
    JAV + '/gui/ServerStatisticsActivity.java',
    RES + '/layout/activity_server_stats.xml',
    JAV + '/backend/TeamTalkConnectionListener.java',
]

def step_cleanup():
    for p in STALE_FILES:
        if os.path.exists(p):
            os.remove(p)
            print('removed stale', os.path.relpath(p, OV))

def step_java():
    for src_rel, dst_rel in ADMIN_JAVA:
        txt = read(TTP + '/java/dk/bearware/' + src_rel)
        txt = txt.replace('super.attachBaseContext(dk.bearware.gui.LocaleHelper.onAttach(base));',
                          'super.attachBaseContext(base);')
        txt = re.sub(r'LocaleHelper\.onAttach\(base\)', 'base', txt)
        txt = txt.replace('UserRight.USERRIGHT_DEFAULT', 'XrayAdmin.DEFAULT_USER_RIGHTS')
        must('LocaleHelper' not in txt, 'LocaleHelper left in ' + src_rel)
        must('USERRIGHT_DEFAULT' not in txt, 'USERRIGHT_DEFAULT left in ' + src_rel)
        # blind friendly: high contrast theme + extra font scale
        anchor = 'super.onCreate(savedInstanceState);'
        if anchor in txt and 'XrayA11y.applyContrastTheme' not in txt:
            txt = txt.replace(anchor,
                              'XrayA11y.applyContrastTheme(this);\n        ' + anchor, 1)
        a_anchor = '        super.attachBaseContext(base);\n    }'
        if a_anchor in txt and 'XrayA11y.fontScale(base)' not in txt:
            txt = txt.replace(a_anchor,
                '        super.attachBaseContext(base);\n'
                '        float scale = XrayA11y.fontScale(base);\n'
                '        if (scale > 1.0f) {\n'
                '            android.content.res.Configuration override =\n'
                '                new android.content.res.Configuration(base.getResources().getConfiguration());\n'
                '            override.fontScale = scale;\n'
                '            applyOverrideConfiguration(override);\n'
                '        }\n'
                '    }', 1)
        write(JAV + '/' + dst_rel, txt)
        print('OK java', dst_rel)

# ---------------------------------------------------------------- 3. XrayAdmin helper
XRAYADMIN_JAVA = '''package dk.bearware.gui;

import dk.bearware.UserRight;

/**
 * Xray admin helper: constants and utilities used by the ported
 * TeamTalk Plus administration screens.
 */
public class XrayAdmin {

    /** Default rights for a freshly created (non-admin) user account. */
    public static final int DEFAULT_USER_RIGHTS =
            UserRight.USERRIGHT_MULTI_LOGIN
            | UserRight.USERRIGHT_VIEW_ALL_USERS
            | UserRight.USERRIGHT_CREATE_TEMPORARY_CHANNEL
            | UserRight.USERRIGHT_MODIFY_CHANNELS
            | UserRight.USERRIGHT_TEXTMESSAGE_BROADCAST
            | UserRight.USERRIGHT_KICK_USERS
            | UserRight.USERRIGHT_BAN_USERS
            | UserRight.USERRIGHT_MOVE_USERS
            | UserRight.USERRIGHT_OPERATOR_ENABLE
            | UserRight.USERRIGHT_UPLOAD_FILES
            | UserRight.USERRIGHT_DOWNLOAD_FILES
            | UserRight.USERRIGHT_UPDATE_SERVERPROPERTIES
            | UserRight.USERRIGHT_TRANSMIT_VOICE
            | UserRight.USERRIGHT_TRANSMIT_VIDEOCAPTURE
            | UserRight.USERRIGHT_TRANSMIT_DESKTOP
            | UserRight.USERRIGHT_TRANSMIT_DESKTOPINPUT
            | UserRight.USERRIGHT_TRANSMIT_MEDIAFILE_AUDIO
            | UserRight.USERRIGHT_TRANSMIT_MEDIAFILE_VIDEO
            | UserRight.USERRIGHT_TEXTMESSAGE_USER
            | UserRight.USERRIGHT_TEXTMESSAGE_CHANNEL
            | UserRight.USERRIGHT_RECORD_VOICE
            | UserRight.USERRIGHT_VIEW_HIDDEN_CHANNELS;

    /** Rights that are only given to server administrators. */
    public static final int ADMIN_ONLY_RIGHTS =
            UserRight.USERRIGHT_UPDATE_SERVERPROPERTIES
            | UserRight.USERRIGHT_BAN_USERS
            | UserRight.USERRIGHT_KICK_USERS
            | UserRight.USERRIGHT_MOVE_USERS
            | UserRight.USERRIGHT_CREATE_TEMPORARY_CHANNEL
            | UserRight.USERRIGHT_MODIFY_CHANNELS
            | UserRight.USERRIGHT_VIEW_HIDDEN_CHANNELS;

    private XrayAdmin() {}
}
'''

# ---------------------------------------------------------------- 4. XrayAdminActivity hub
HUB_JAVA = '''package dk.bearware.gui;

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
}
'''

HUB_LAYOUT = '''<?xml version="1.0" encoding="utf-8"?>
<ScrollView xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:padding="12dp">

    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:orientation="vertical">

        <TextView
            android:id="@+id/txt_xray_admin_title"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:padding="8dp"
            android:text="@string/xray_admin"
            android:textSize="24sp"
            android:textStyle="bold" />

        <TextView
            android:id="@+id/txt_xray_admin_hint"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:paddingBottom="8dp"
            android:text="@string/xray_admin_hint"
            android:textSize="16sp" />

        <Button
            android:id="@+id/btn_xray_user_accounts"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:layout_marginBottom="8dp"
            android:contentDescription="@string/xray_user_accounts"
            android:minHeight="64dp"
            android:text="@string/xray_user_accounts"
            android:textSize="18sp" />

        <Button
            android:id="@+id/btn_xray_server_props"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:layout_marginBottom="8dp"
            android:contentDescription="@string/xray_server_props"
            android:minHeight="64dp"
            android:text="@string/xray_server_props"
            android:textSize="18sp" />

        <Button
            android:id="@+id/btn_xray_server_info"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:layout_marginBottom="8dp"
            android:contentDescription="@string/xray_server_info"
            android:minHeight="64dp"
            android:text="@string/xray_server_info"
            android:textSize="18sp" />

        <Button
            android:id="@+id/btn_xray_move_users"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:layout_marginBottom="8dp"
            android:contentDescription="@string/xray_move_users"
            android:minHeight="64dp"
            android:text="@string/xray_move_users"
            android:textSize="18sp" />

        <Button
            android:id="@+id/btn_xray_channel_bans"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:layout_marginBottom="8dp"
            android:contentDescription="@string/xray_channel_bans"
            android:minHeight="64dp"
            android:text="@string/xray_channel_bans"
            android:textSize="18sp" />

        <Button
            android:id="@+id/btn_xray_server_bans"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:layout_marginBottom="8dp"
            android:contentDescription="@string/xray_server_bans"
            android:minHeight="64dp"
            android:text="@string/xray_server_bans"
            android:textSize="18sp" />

    </LinearLayout>
</ScrollView>
'''

# ---------------------------------------------------------------- 4b. server info activity
SERVERINFO_JAVA = '''package dk.bearware.gui;

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
'''

# ---------------------------------------------------------------- 5. layouts + drawables
LAYOUTS = [
    'activity_user_accounts.xml', 'item_user_account.xml',
    'activity_user_account_edit.xml',
    'fragment_user_account_basic.xml', 'fragment_user_account_rights.xml',
    'fragment_user_account_operator.xml', 'fragment_user_account_codec.xml',
    'fragment_user_account_abuse.xml',
    'activity_server_properties.xml',
    'fragment_server_prop_general.xml', 'fragment_server_prop_bandwidth.xml',
    'fragment_server_prop_logging.xml', 'fragment_server_prop_abuse.xml',
    'activity_server_stats.xml', 'activity_move_users.xml',
    'activity_channel_banned_users.xml', 'list_item_banned.xml',
]

def step_layouts():
    for l in LAYOUTS:
        srcp = TTP + '/res/layout/' + l
        must(os.path.exists(srcp), 'missing TTP layout ' + l)
        write(RES + '/layout/' + l, read(srcp))
    print('OK %d layouts' % len(LAYOUTS))
    # drawables referenced by copied layouts
    refs = set()
    for l in LAYOUTS:
        txt = read(RES + '/layout/' + l)
        refs |= set(re.findall(r'@(?:drawable|mipmap)/([A-Za-z0-9_]+)', txt))
    missing = []
    for r in sorted(refs):
        found = False
        for d in os.listdir(SRC + '/src/main/res'):
            if d.startswith('drawable') or d.startswith('mipmap'):
                if os.path.exists(SRC + '/src/main/res/' + d + '/' + r + '.xml') or \
                   any(f.startswith(r + '.') for f in os.listdir(SRC + '/src/main/res/' + d)):
                    found = True; break
        if found: continue
        # copy from TTP
        copied = False
        for d in os.listdir(TTP + '/res'):
            if d.startswith('drawable') or d.startswith('mipmap'):
                p = TTP + '/res/' + d + '/' + r
                for cand in (p + '.xml', p + '.png', p + '.webp', p + '.jpg'):
                    if os.path.exists(cand):
                        os.makedirs(RES + '/' + d, exist_ok=True)
                        shutil.copy(cand, RES + '/' + d + '/' + os.path.basename(cand))
                        copied = True; break
            if copied: break
        if not copied:
            missing.append(r)
    print('drawables missing:', missing if missing else 'none')

# ---------------------------------------------------------------- 5b. our own strings
OWN_STRINGS = {
    'xray_admin': ('Extra features', 'قابلیت‌های اضافه'),
    'xray_admin_hint': ('User accounts, bans, moving users and server settings, like TeamTalk Plus. Server admin rights required.',
                         'حساب کاربری، بن، انتقال کاربر و تنظیمات سرور، مثل تیم‌تاک پلاس. دسترسی مدیر سرور لازمه.'),
    'xray_developer': ('Developer', 'توسعه‌دهنده'),
    'xray_developer_name': ('Amir Mahdi Fard', 'امیر مهدی فرد'),
    'xray_user_accounts': ('User accounts', 'حساب‌های کاربری'),
    'xray_server_props': ('Server properties', 'تنظیمات سرور'),
    'xray_server_info': ('Server information', 'اطلاعات سرور'),
    'xray_server_info_hint': ('Live information from the server you are connected to.',
                              'اطلاعات زنده از سروری که به آن وصلی.'),
    'xray_srv_name': ('Server name', 'نام سرور'),
    'xray_srv_version': ('Server version', 'نسخه سرور'),
    'xray_srv_motd': ('Message of the day', 'پیام خوش‌آمدگویی'),
    'xray_srv_max_users': ('Maximum users', 'بیشترین تعداد کاربر'),
    'xray_srv_max_logins_ip': ('Maximum logins per IP', 'بیشترین ورود از هر IP'),
    'xray_srv_login_delay': ('Login delay (ms)', 'تأخیر ورود (میلی‌ثانیه)'),
    'xray_srv_user_timeout': ('User timeout (seconds)', 'زمان بی‌خبری کاربر (ثانیه)'),
    'xray_srv_ports': ('TCP / UDP port', 'پورت TCP / UDP'),
    'xray_srv_autosave': ('Auto save', 'ذخیره خودکار'),
    'xray_conn_stats': ('Connection statistics', 'آمار اتصال'),
    'xray_conn_ping': ('Ping (TCP / UDP)', 'پینگ (TCP / UDP)'),
    'xray_conn_bytes': ('Bytes sent / received', 'بایت ارسالی / دریافتی'),
    'xray_not_connected': ('Not connected to a server', 'به سرور وصل نیستی'),
    'xray_move_users': ('Move users', 'انتقال کاربران'),
    'xray_channel_bans': ('Banned users in channel', 'کاربران مسدود کانال'),
    'xray_server_bans': ('Banned users on server', 'کاربران مسدود سرور'),
}

def step_own_strings():
    en = ['<string name=\"%s\">%s</string>' % (k, v[0]) for k, v in sorted(OWN_STRINGS.items())]
    fa = ['<string name=\"%s\">%s</string>' % (k, v[1]) for k, v in sorted(OWN_STRINGS.items())]
    xml_hdr = '<?xml version="1.0" encoding="utf-8"?>\n<resources>\n'
    xml_ftr = '\n</resources>\n'
    write(RES + '/values/xray_admin_strings.xml', xml_hdr + '\n'.join(en) + xml_ftr)
    write(RES + '/values-fa-rIR/xray_admin_strings.xml', xml_hdr + '\n'.join(fa) + xml_ftr)
    print('OK own strings: %d' % len(en))

# ---------------------------------------------------------------- 6. strings
def step_strings():
    en = parse_strings(TTP + '/res/values/strings.xml')
    en.update({k: v for k, v in parse_strings(TTP + '/res/values/strings_import.xml').items() if k not in en})
    fa = parse_strings(TTP + '/res/values-fa/strings.xml')
    fa.update({k: v for k, v in parse_strings(TTP + '/res/values-fa/strings_import.xml').items() if k not in fa})
    # names already defined upstream / overlay
    up_en = defined_names(SRC + '/src/main/res/values/strings.xml')
    up_fa = defined_names(SRC + '/src/main/res/values-fa-rIR/strings.xml')
    ov_en = all_names_in_res_dir(RES + '/values')
    ov_fa = all_names_in_res_dir(RES + '/values-fa-rIR')
    # collect referenced names
    refs = set()
    java_files = []
    for dirpath, _, files in os.walk(JAV):
        for f in files:
            if f.endswith('.java'): java_files.append(os.path.join(dirpath, f))
    for p in java_files:
        txt = read(p)
        refs |= set(re.findall(r'(?<!android\.)\bR\.string\.([A-Za-z0-9_]+)', txt))
    xml_files = []
    for dirpath, _, files in os.walk(RES):
        for f in files:
            if f.endswith('.xml'): xml_files.append(os.path.join(dirpath, f))
    for p in xml_files:
        txt = read(p)
        refs |= set(re.findall(r'@string/([A-Za-z0-9_]+)', txt))
    # manifest references count too
    mpath = OV + '/src/main/AndroidManifest.xml'
    if os.path.exists(mpath):
        refs |= set(re.findall(r'@string/([A-Za-z0-9_]+)', read(mpath)))
    # remove names we define ourselves in the xray files
    GEN = {'ttplus_strings.xml', 'xray_colors.xml', 'xray_dimens.xml'}
    def own_names(d):
        names = set()
        if not os.path.isdir(d): return names
        for f in os.listdir(d):
            if f.endswith('.xml') and f not in GEN:
                names |= defined_names(os.path.join(d, f))
        return names
    own = own_names(RES + '/values') | own_names(RES + '/values-fa-rIR')
    need = sorted(refs - up_en - own)
    # EN file
    en_body = []
    for n in need:
        if n in en:
            en_body.append('<string name="%s">%s</string>' % (n, en[n]))
        else:
            print('  !! no EN source for string:', n)
    # plurals
    en_pl = parse_plurals(TTP + '/res/values/strings.xml')
    fa_pl = parse_plurals(TTP + '/res/values-fa/strings.xml')
    up_pl = set(parse_plurals(SRC + '/src/main/res/values/strings.xml').keys())
    prefs = set()
    for p in java_files:
        prefs |= set(re.findall(r'(?<!android\.)\bR\.plurals\.([A-Za-z0-9_]+)', read(p)))
    for p in xml_files:
        prefs |= set(re.findall(r'@plurals/([A-Za-z0-9_]+)', read(p)))
    pl_body = []
    for n in sorted(prefs - up_pl):
        if n in en_pl:
            pl_body.append('<plurals name=\"%s\">%s</plurals>' % (n, en_pl[n]))
        else:
            print('  !! no EN source for plural:', n)
    if pl_body:
        en_body += pl_body
    fa_pl_body = []
    for n in sorted(prefs - up_pl):
        if n in fa_pl:
            fa_pl_body.append('<plurals name=\"%s\">%s</plurals>' % (n, fa_pl[n]))
    write(RES + '/values/ttplus_strings.xml',
          '<?xml version="1.0" encoding="utf-8"?>\n<resources>\n' + '\n'.join(en_body) + '\n</resources>\n')
    # FA file: names not already defined in upstream fa-rIR and not in our own fa files
    fa_need = [n for n in need if n not in up_fa]
    fa_body = []
    seen = set()
    for n in fa_need:
        if n in seen: continue
        seen.add(n)
        if n in fa:
            fa_body.append('<string name="%s">%s</string>' % (n, fa[n]))
        elif n in en:
            fa_body.append('<string name="%s">%s</string>' % (n, en[n]))
    if fa_pl_body:
        fa_body += fa_pl_body
    write(RES + '/values-fa-rIR/ttplus_strings.xml',
          '<?xml version="1.0" encoding="utf-8"?>\n<resources>\n' + '\n'.join(fa_body) + '\n</resources>\n')
    print('OK strings: EN %d, FA %d (of %d refs)' % (len(en_body), len(fa_body), len(refs)))

# ---------------------------------------------------------------- 7. colors / dimens
def step_res():
    refs_color = set(); refs_dimen = set()
    for dirpath, _, files in os.walk(RES):
        for f in files:
            if not f.endswith('.xml'): continue
            p = os.path.join(dirpath, f)
            if p.endswith('ttplus_strings.xml'): continue
            txt = read(p)
            refs_color |= set(re.findall(r'@color/([A-Za-z0-9_]+)', txt))
            refs_dimen |= set(re.findall(r'@dimen/([A-Za-z0-9_]+)', txt))
    up_colors = set(re.findall(r'<color\s+name="([^"]+)"', read(SRC + '/src/main/res/values/colors.xml'))) if os.path.exists(SRC + '/src/main/res/values/colors.xml') else set()
    up_dims = set(re.findall(r'<dimen\s+name="([^"]+)"', read(SRC + '/src/main/res/values/dimens.xml'))) if os.path.exists(SRC + '/src/main/res/values/dimens.xml') else set()
    ttp_colors = dict(re.findall(r'<color\s+name="([^"]+)"[^>]*>([^<]*)</color>', read(TTP + '/res/values/colors.xml'))) if os.path.exists(TTP + '/res/values/colors.xml') else {}
    ttp_dims = dict(re.findall(r'<dimen\s+name="([^"]+)"[^>]*>([^<]*)</dimen>', read(TTP + '/res/values/dimens.xml'))) if os.path.exists(TTP + '/res/values/dimens.xml') else {}
    cbody = ['<color name="%s">%s</color>' % (c, ttp_colors[c]) for c in sorted(refs_color - up_colors) if c in ttp_colors]
    dbody = ['<dimen name="%s">%s</dimen>' % (d, ttp_dims[d]) for d in sorted(refs_dimen - up_dims) if d in ttp_dims]
    missing_c = sorted((refs_color - up_colors) - set(ttp_colors))
    missing_d = sorted((refs_dimen - up_dims) - set(ttp_dims))
    if cbody:
        write(RES + '/values/xray_colors.xml', '<?xml version="1.0" encoding="utf-8"?>\n<resources>\n' + '\n'.join(cbody) + '\n</resources>\n')
    if dbody:
        write(RES + '/values/xray_dimens.xml', '<?xml version="1.0" encoding="utf-8"?>\n<resources>\n' + '\n'.join(dbody) + '\n</resources>\n')
    print('colors added %d (missing %s), dimens added %d (missing %s)' % (len(cbody), missing_c, len(dbody), missing_d))

# ---------------------------------------------------------------- 8. manifest
ACTIVITIES = [
    ('XrayAdminActivity', 'xray_admin'),
    ('UserAccountsActivity', 'user_accounts'),
    ('UserAccountEditActivity', 'user_accounts'),
    ('ServerPropActivity', 'tab_server_properties'),
    ('XrayServerInfoActivity', 'xray_server_info'),
    ('MoveUsersActivity', 'title_move_users'),
    ('ChannelBannedUsersActivity', 'title_activity_channel_banned_users'),
    ('ServerBannedUsersActivity', 'title_activity_server_banned_users'),
]

def step_manifest():
    m = read(SRC + '/src/main/AndroidManifest.xml')
    entries = []
    for cls, label in ACTIVITIES:
        entries.append('        <activity\n'
                       '            android:name="dk.bearware.gui.%s"\n'
                       '            android:exported="false"\n'
                       '            android:label="@string/%s"\n'
                       '            android:parentActivityName="dk.bearware.gui.MainActivity" />' % (cls, label))
    block = '\n'.join(entries) + '\n'
    must('</application>' in m, 'no </application> in manifest')
    m = m.replace('    </application>', block + '    </application>')
    write(OV + '/src/main/AndroidManifest.xml', m)
    print('OK manifest (+%d activities)' % len(entries))

# ---------------------------------------------------------------- 9. menu + MainActivity
def step_menu():
    m = read(SRC + '/src/main/res/menu/main.xml')
    if 'android:id="@+id/action_admin"' not in m:
        show = 'app:showAsAction' if 'xmlns:app' in m else 'android:showAsAction'
        item = ('        <item\n'
                '            android:id="@+id/action_admin"\n'
                '            android:orderInCategory="102"\n'
                '            android:title="@string/xray_admin"\n'
                '            %s="never" />\n' % show)
        idx = m.rfind('</menu>')
        m = m[:idx] + item + m[idx:]
    write(RES + '/menu/main.xml', m)
    print('OK menu/main.xml')

def step_mainactivity():
    p = JAV + '/gui/MainActivity.java'
    must(os.path.exists(p), 'overlay MainActivity.java missing')
    txt = read(p)
    if 'R.id.action_admin' not in txt:
        old = '        int itemId = item.getItemId();\n'
        must(old in txt, 'cannot patch MainActivity menu handler')
        anchor = '        if (itemId == R.id.action_join) {\n'
        must(anchor in txt, 'cannot find menu dispatch anchor')
        new = ('        if (itemId == R.id.action_admin) {\n'
               '            startActivity(new Intent(MainActivity.this, XrayAdminActivity.class));\n'
               '        } else if (itemId == R.id.action_join) {\n')
        txt = txt.replace(anchor, new, 1)
    write(p, txt)
    print('OK MainActivity action_admin')

# ---------------------------------------------------------------- 9b. prefs shortcut to admin tools
def step_prefs():
    p = RES + '/xml/pref_xray.xml'
    must(os.path.exists(p), 'overlay pref_xray.xml missing')
    txt = read(p)
    if 'xray_open_admin' not in txt:
        add = ('    <PreferenceCategory android:title="@string/xray_admin">\n'
               '        <Preference\n'
               '            android:key="xray_open_admin"\n'
               '            android:title="@string/xray_admin"\n'
               '            android:summary="@string/xray_admin_hint" />\n'
               '    </PreferenceCategory>\n\n')
        idx = txt.rfind('</PreferenceScreen>')
        must(idx > 0, 'cannot patch pref_xray.xml')
        txt = txt[:idx] + add + txt[idx:]
        write(p, txt)

    p2 = JAV + '/gui/PreferencesActivity.java'
    must(os.path.exists(p2), 'overlay PreferencesActivity.java missing')
    t2 = read(p2)
    if 'xray_open_admin' not in t2:
        anchor = '            bindPreferenceSummaryToValue(findPreference(XrayA11y.PREF_FONT_SCALE));\n'
        must(anchor in t2, 'cannot patch XrayPreferenceFragment')
        add = (anchor +
               '            Preference adminPref = findPreference("xray_open_admin");\n'
               '            if (adminPref != null) {\n'
               '                adminPref.setOnPreferenceClickListener(preference -> {\n'
               '                    if (getActivity() != null)\n'
               '                        getActivity().startActivity(new Intent(getActivity(), XrayAdminActivity.class));\n'
               '                    return true;\n'
               '                });\n'
               '            }\n')
        t2 = t2.replace(anchor, add, 1)
        write(p2, t2)
    print('OK prefs shortcut to admin tools')

# ---------------------------------------------------------------- 9c. about screen credits
def step_about():
    src = SRC + '/src/main/res/xml/pref_about.xml'
    must(os.path.exists(src), 'upstream pref_about.xml missing')
    txt = read(src)
    if 'xray_developer' not in txt:
        dup = ('        <EditTextPreference\n'
               '            android:enabled="false"\n'
               '            android:singleLine="true"\n'
               '            android:title="Amir Mahdi Fard" />\n')
        txt = txt.replace(dup, '')
        head = '<PreferenceScreen xmlns:android="http://schemas.android.com/apk/res/android" >'
        must(head in txt, 'cannot patch pref_about.xml')
        block = (head + '\n'
                 '    <PreferenceCategory android:title="@string/xray_developer">\n'
                 '        <EditTextPreference\n'
                 '            android:enabled="false"\n'
                 '            android:singleLine="true"\n'
                 '            android:title="@string/xray_developer_name" />\n'
                 '    </PreferenceCategory>\n')
        txt = txt.replace(head, block, 1)
    write(RES + '/xml/pref_about.xml', txt)
    print('OK about screen developer credit')

# ---------------------------------------------------------------- 10. build.gradle
def step_gradle():
    p = OV + '/build.gradle'
    txt = read(p)
    if 'viewpager2' not in txt:
        if '    implementation libs.material' in txt:
            txt = txt.replace('    implementation libs.material',
                              '    implementation libs.material\n    implementation "androidx.viewpager2:viewpager2:1.1.0"', 1)
        else:
            must('dependencies {' in txt, 'no dependencies block in build.gradle')
            txt = txt.replace('dependencies {', 'dependencies {\n    implementation "androidx.viewpager2:viewpager2:1.1.0"', 1)
    write(p, txt)
    print('OK build.gradle (viewpager2)')

def main():
    step_cleanup()
    step_utils()
    step_java()
    write(JAV + '/gui/XrayAdmin.java', XRAYADMIN_JAVA)
    write(JAV + '/gui/XrayAdminActivity.java', HUB_JAVA)
    write(JAV + '/gui/XrayServerInfoActivity.java', SERVERINFO_JAVA)
    write(RES + '/layout/activity_xray_admin.xml', HUB_LAYOUT)
    step_layouts()
    step_own_strings()
    step_manifest()
    step_strings()
    step_res()
    step_menu()
    step_mainactivity()
    step_prefs()
    step_about()
    step_gradle()
    print('DONE')

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Xray UI layer: modern graphics theme, screen recording + screen share, English credits.

Run order: mkoverlay.py -> mkadmin.py -> mkui.py -> verify.py
"""
import os
import re
import sys

ROOT = '/root/.buddy/work/teamtalk-xray'
SRC = ROOT + '/src/Client/TeamTalkAndroid/src/main'
OV = ROOT + '/ci/overlay/Client/TeamTalkAndroid/src/main'
JAV = OV + '/java'
RES = OV + '/res'


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


# ----------------------------------------------------------------- 1. palette
PALETTE = '''<?xml version="1.0" encoding="utf-8"?>
<resources>
    <color name="xray_bg">#0B0F14</color>
    <color name="xray_surface">#141B23</color>
    <color name="xray_surface2">#1B2530</color>
    <color name="xray_stroke">#24313D</color>
    <color name="xray_accent">#00E5FF</color>
    <color name="xray_accent_dim">#00A6BD</color>
    <color name="xray_text">#ECEFF1</color>
    <color name="xray_text_dim">#93A3B1</color>
    <color name="xray_ok">#2ECC71</color>
    <color name="xray_warn">#FFC94A</color>
    <color name="xray_danger">#FF5C6C</color>
    <color name="xray_tx">#E53935</color>
    <color name="xray_tx_dim">#B71C1C</color>
</resources>
'''


def step_palette():
    write(RES + '/values/xray_palette.xml', PALETTE)
    print('OK palette')


# ----------------------------------------------------------------- 2. drawables
DRAWABLES = {
    'xray_card.xml': '''<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <solid android:color="@color/xray_surface" />
    <corners android:radius="18dp" />
    <stroke android:width="1dp" android:color="@color/xray_stroke" />
</shape>
''',
    'xray_row.xml': '''<?xml version="1.0" encoding="utf-8"?>
<ripple xmlns:android="http://schemas.android.com/apk/res/android" android:color="#3300E5FF">
    <item>
        <shape android:shape="rectangle">
            <solid android:color="@color/xray_surface" />
            <corners android:radius="14dp" />
        </shape>
    </item>
</ripple>
''',
    'xray_pill.xml': '''<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <solid android:color="@color/xray_surface2" />
    <corners android:radius="12dp" />
</shape>
''',
    'xray_btn_primary.xml': '''<?xml version="1.0" encoding="utf-8"?>
<ripple xmlns:android="http://schemas.android.com/apk/res/android" android:color="#5500E5FF">
    <item>
        <shape android:shape="rectangle">
            <gradient android:startColor="@color/xray_accent" android:endColor="@color/xray_accent_dim"
                android:angle="0" />
            <corners android:radius="14dp" />
        </shape>
    </item>
</ripple>
''',
    'xray_btn_ghost.xml': '''<?xml version="1.0" encoding="utf-8"?>
<ripple xmlns:android="http://schemas.android.com/apk/res/android" android:color="#3300E5FF">
    <item>
        <shape android:shape="rectangle">
            <solid android:color="#00000000" />
            <corners android:radius="12dp" />
            <stroke android:width="1dp" android:color="@color/xray_accent" />
        </shape>
    </item>
</ripple>
''',
    'xray_tx_btn.xml': '''<?xml version="1.0" encoding="utf-8"?>
<ripple xmlns:android="http://schemas.android.com/apk/res/android" android:color="#55FFFFFF">
    <item>
        <shape android:shape="oval">
            <gradient android:startColor="@color/xray_tx" android:endColor="@color/xray_tx_dim"
                android:angle="270" />
        </shape>
    </item>
</ripple>
''',
    'xray_tx_btn_on.xml': '''<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="oval">
    <gradient android:startColor="#2ECC71" android:endColor="#1B8A4B" android:angle="270" />
</shape>
''',
    'xray_ic_record.xml': '''<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="24dp" android:height="24dp"
    android:viewportWidth="24" android:viewportHeight="24">
    <path android:fillColor="#ECEFF1"
        android:pathData="M12,2A10,10 0 1,0 22,12A10,10 0,0 0,12,2zM12,17A5,5 0 1,1 17,12A5,5 0,0 1,12,17z" />
</vector>
''',
    'xray_ic_share.xml': '''<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="24dp" android:height="24dp"
    android:viewportWidth="24" android:viewportHeight="24">
    <path android:fillColor="#ECEFF1"
        android:pathData="M4,3h16a2,2 0,0 1,2 2v10a2,2 0,0 1,-2 2h-4l0,2h2v2H6v-2h2v-2H4a2,2 0,0 1,-2 -2V5a2,2 0,0 1,2 -2zM12,7l-4,4h2.5v3h3v-3H16z" />
</vector>
''',
}


def step_drawables():
    for name, body in DRAWABLES.items():
        write(RES + '/drawable/' + name, body)
    print('OK drawables (%d)' % len(DRAWABLES))


# ----------------------------------------------------------------- 3. styles
VISUAL_THEME = '''    <!-- Xray: modern dark look for sighted users. Only colours, action bar,
         buttons and list styling live here. Contrast mode, font scaling,
         announcements and vibration are untouched. -->
    <style name="AppTheme" parent="Theme.AppCompat.DayNight">
        <item name="colorPrimary">@color/xray_surface</item>
        <item name="colorPrimaryDark">@color/xray_bg</item>
        <item name="colorAccent">@color/xray_accent</item>
        <item name="android:windowBackground">@color/xray_bg</item>
        <item name="android:colorBackground">@color/xray_bg</item>
        <item name="android:textColorPrimary">@color/xray_text</item>
        <item name="android:textColorSecondary">@color/xray_text_dim</item>
        <item name="android:textColorHint">@color/xray_text_dim</item>
        <item name="android:statusBarColor">@color/xray_bg</item>
        <item name="android:navigationBarColor">@color/xray_bg</item>
        <item name="actionBarStyle">@style/XrayActionBar</item>
        <item name="alertDialogTheme">@style/XrayDialogTheme</item>
        <item name="buttonStyle">@style/XrayButton</item>
        <item name="android:listViewStyle">@style/XrayListView</item>
    </style>
'''

VISUAL_NOACTION = '''<style name="AppTheme.NoActionBar" parent="Theme.AppCompat.DayNight">
        <item name="windowActionBar">false</item>
        <item name="windowNoTitle">true</item>
        <item name="colorPrimary">@color/xray_surface</item>
        <item name="colorAccent">@color/xray_accent</item>
        <item name="android:windowBackground">@color/xray_bg</item>
        <item name="android:colorBackground">@color/xray_bg</item>
        <item name="android:textColorPrimary">@color/xray_text</item>
        <item name="android:textColorSecondary">@color/xray_text_dim</item>
    </style>'''

VISUAL_EXTRA = '''
    <style name="XrayActionBar" parent="Widget.AppCompat.ActionBar.Solid">
        <item name="background">@color/xray_surface</item>
        <item name="elevation">6dp</item>
        <item name="titleTextStyle">@style/XrayActionBarTitle</item>
    </style>

    <style name="XrayActionBarTitle" parent="TextAppearance.Widget.AppCompat.Toolbar.Title">
        <item name="android:textColor">@color/xray_text</item>
        <item name="android:textSize">20sp</item>
        <item name="android:textStyle">bold</item>
    </style>

    <style name="XrayDialogTheme" parent="Theme.AppCompat.Dialog.Alert">
        <item name="colorAccent">@color/xray_accent</item>
        <item name="android:textColorPrimary">@color/xray_text</item>
        <item name="android:background">@color/xray_surface</item>
    </style>

    <style name="XrayButton" parent="Widget.AppCompat.Button">
        <item name="android:background">@drawable/xray_btn_primary</item>
        <item name="android:textColor">#FF06222A</item>
        <item name="android:textAllCaps">false</item>
        <item name="android:textStyle">bold</item>
        <item name="android:minHeight">48dp</item>
        <item name="android:paddingStart">18dp</item>
        <item name="android:paddingEnd">18dp</item>
    </style>

    <style name="XrayListView" parent="Widget.AppCompat.ListView">
        <item name="android:divider">@color/xray_bg</item>
        <item name="android:dividerHeight">6dp</item>
        <item name="android:paddingStart">10dp</item>
        <item name="android:paddingEnd">10dp</item>
        <item name="android:paddingTop">6dp</item>
        <item name="android:paddingBottom">6dp</item>
        <item name="android:clipToPadding">false</item>
    </style>

    <style name="XrayChatName">
        <item name="android:textColor">@color/xray_text</item>
        <item name="android:textSize">17sp</item>
        <item name="android:textStyle">bold</item>
        <item name="android:singleLine">true</item>
    </style>

    <style name="XrayChatSub">
        <item name="android:textColor">@color/xray_text_dim</item>
        <item name="android:textSize">13sp</item>
        <item name="android:singleLine">true</item>
    </style>

    <style name="XrayStat">
        <item name="android:textColor">@color/xray_text_dim</item>
        <item name="android:textSize">11sp</item>
        <item name="android:singleLine">true</item>
        <item name="android:paddingEnd">8dp</item>
    </style>
'''


def step_styles():
    """Patch the generated styles.xml - never replace the accessibility theme."""
    p = RES + '/values/styles.xml'
    must(os.path.exists(p), 'styles.xml missing (run mkoverlay.py first)')
    s = read(p)
    s = re.sub(r'<style name="AppTheme" parent="Theme\.AppCompat\.DayNight" />',
               VISUAL_THEME.strip(), s)
    s = re.sub(r'<style name="AppTheme\.NoActionBar".*?</style>',
               VISUAL_NOACTION.strip(), s, flags=re.S)
    if 'XrayChatName' not in s:
        s = s.replace('</resources>', VISUAL_EXTRA + '\n</resources>')
    must('<style name="AppTheme.Xray"' in s, 'accessibility theme removed')
    must('#FFFFEB3B' in s, 'accessibility colours changed')
    write(p, s)
    print('OK styles (visual only, accessibility theme untouched)')


# ----------------------------------------------------------------- 4. layouts
ACTIVITY_MAIN = '''<LinearLayout
    xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:background="@color/xray_bg"
    android:orientation="vertical"
    tools:context=".MainActivity" >

    <com.google.android.material.tabs.TabLayout
        android:id="@+id/tab_layout"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:background="@color/xray_surface"
        android:elevation="4dp"
        android:paddingBottom="6dp"
        android:paddingTop="6dp"
        app:tabIndicatorColor="@color/xray_accent"
        app:tabIndicatorHeight="3dp"
        app:tabSelectedTextColor="@color/xray_accent"
        app:tabTextColor="@color/xray_text_dim" />

    <androidx.viewpager.widget.ViewPager
        android:id="@+id/pager"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:layout_weight="1.0"
        android:background="@color/xray_bg" />

    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:layout_marginStart="8dp"
        android:layout_marginEnd="8dp"
        android:layout_marginBottom="8dp"
        android:background="@drawable/xray_card"
        android:gravity="center_vertical"
        android:orientation="horizontal"
        android:padding="12dp" >

        <LinearLayout
            android:layout_width="0dp"
            android:layout_height="wrap_content"
            android:layout_weight="1"
            android:orientation="vertical" >

            <LinearLayout
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="horizontal" >

                <TextView
                    android:id="@+id/connectionstat_textview"
                    style="@style/XrayStat"
                    android:layout_width="0dp"
                    android:layout_height="wrap_content"
                    android:layout_weight="1"
                    android:text=""
                    android:textColor="@color/xray_accent"
                    android:textStyle="bold" />

                <TextView
                    android:id="@+id/pingstat_textview"
                    style="@style/XrayStat"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:text="" />

                <TextView
                    android:id="@+id/totalstat_textview"
                    style="@style/XrayStat"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:text="" />
            </LinearLayout>

            <LinearLayout
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:gravity="center_vertical"
                android:orientation="horizontal" >

                <ImageButton
                    android:id="@+id/speakerBtn"
                    android:layout_width="44dp"
                    android:layout_height="44dp"
                    android:background="?android:attr/selectableItemBackgroundBorderless"
                    android:contentDescription="@string/speaker_mute"
                    android:src="@drawable/speaker_blue" />

                <LinearLayout
                    android:layout_width="0dp"
                    android:layout_height="wrap_content"
                    android:layout_weight="1"
                    android:orientation="vertical" >

                    <TextView
                        android:id="@+id/vollevel_text"
                        style="@style/XrayStat"
                        android:layout_width="match_parent"
                        android:layout_height="wrap_content"
                        android:text="" />

                    <SeekBar
                        android:id="@+id/master_volSeekBar"
                        android:layout_width="match_parent"
                        android:layout_height="wrap_content"
                        android:contentDescription="@string/mastervolume" />
                </LinearLayout>
            </LinearLayout>

            <LinearLayout
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:gravity="center_vertical"
                android:orientation="horizontal" >

                <ImageButton
                    android:id="@+id/voxSwitch"
                    android:layout_width="44dp"
                    android:layout_height="44dp"
                    android:background="?android:attr/selectableItemBackgroundBorderless"
                    android:contentDescription="@string/voice_activation_on"
                    android:src="@drawable/mic_green" />

                <LinearLayout
                    android:layout_width="0dp"
                    android:layout_height="wrap_content"
                    android:layout_weight="1"
                    android:orientation="vertical" >

                    <TextView
                        android:id="@+id/miclevel_text"
                        style="@style/XrayStat"
                        android:layout_width="match_parent"
                        android:layout_height="wrap_content"
                        android:text="" />

                    <SeekBar
                        android:id="@+id/mic_gainSeekBar"
                        android:layout_width="match_parent"
                        android:layout_height="wrap_content"
                        android:contentDescription="@string/micgain" />
                </LinearLayout>
            </LinearLayout>
        </LinearLayout>

        <Button
            android:id="@+id/transmit_voice"
            android:layout_width="86dp"
            android:layout_height="86dp"
            android:layout_marginStart="10dp"
            android:background="@drawable/xray_tx_btn"
            android:elevation="8dp"
            android:text="@string/button_tx"
            android:textColor="#FFFFFFFF"
            android:textSize="15sp"
            android:textStyle="bold" />
    </LinearLayout>

</LinearLayout>
'''

ITEM_CHANNEL = '''<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:background="@drawable/xray_row"
    android:gravity="center_vertical"
    android:minHeight="62dp"
    android:orientation="horizontal"
    android:paddingStart="12dp"
    android:paddingTop="10dp"
    android:paddingEnd="10dp"
    android:paddingBottom="10dp" >

    <ImageView
        android:id="@+id/channelicon"
        android:layout_width="24dp"
        android:layout_height="24dp"
        android:importantForAccessibility="no"
        android:src="@drawable/channel_green" />

    <LinearLayout
        android:layout_width="0dp"
        android:layout_height="wrap_content"
        android:layout_marginStart="10dp"
        android:layout_weight="1"
        android:orientation="vertical" >

        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:gravity="center_vertical"
            android:orientation="horizontal" >

            <TextView
                android:id="@+id/channelname"
                style="@style/XrayChatName"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="" />

            <TextView
                android:id="@+id/population"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:layout_marginStart="8dp"
                android:background="@drawable/xray_pill"
                android:paddingStart="8dp"
                android:paddingTop="2dp"
                android:paddingEnd="8dp"
                android:paddingBottom="2dp"
                android:singleLine="true"
                android:text=""
                android:textColor="@color/xray_accent"
                android:textSize="12sp"
                android:textStyle="bold" />
        </LinearLayout>

        <TextView
            android:id="@+id/chantopic"
            style="@style/XrayChatSub"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:text="" />
    </LinearLayout>

    <Button
        android:id="@+id/join_btn"
        android:layout_width="wrap_content"
        android:layout_height="40dp"
        android:background="@drawable/xray_btn_ghost"
        android:clickable="true"
        android:focusable="false"
        android:minWidth="0dp"
        android:paddingStart="14dp"
        android:paddingEnd="14dp"
        android:text="@string/action_join"
        android:textColor="@color/xray_accent"
        android:textSize="13sp" />

</LinearLayout>
'''

ITEM_USER = '''<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:background="@drawable/xray_row"
    android:gravity="center_vertical"
    android:minHeight="62dp"
    android:orientation="horizontal"
    android:paddingStart="12dp"
    android:paddingTop="10dp"
    android:paddingEnd="10dp"
    android:paddingBottom="10dp" >

    <ImageView
        android:id="@+id/usericon"
        android:layout_width="36dp"
        android:layout_height="36dp"
        android:importantForAccessibility="no"
        android:src="@drawable/man_blue" />

    <LinearLayout
        android:layout_width="0dp"
        android:layout_height="wrap_content"
        android:layout_marginStart="10dp"
        android:layout_weight="1"
        android:orientation="vertical" >

        <TextView
            android:id="@+id/nickname"
            style="@style/XrayChatName"
            android:layout_width="match_parent"
            android:layout_height="wrap_content" />

        <TextView
            android:id="@+id/status"
            style="@style/XrayChatSub"
            android:layout_width="match_parent"
            android:layout_height="wrap_content" />
    </LinearLayout>

    <Button
        android:id="@+id/msg_btn"
        android:layout_width="wrap_content"
        android:layout_height="40dp"
        android:background="@drawable/xray_btn_ghost"
        android:clickable="true"
        android:focusable="false"
        android:minWidth="0dp"
        android:paddingStart="14dp"
        android:paddingEnd="14dp"
        android:text="@string/button_msg"
        android:textColor="@color/xray_accent"
        android:textSize="13sp" />

</LinearLayout>
'''

FRAGMENT_CHANNELS = '''<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:background="@color/xray_bg"
    android:orientation="vertical" >

    <ListView
        android:id="@+id/listChannels"
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        android:clipToPadding="false"
        android:divider="@null"
        android:dividerHeight="0dp"
        android:paddingStart="8dp"
        android:paddingTop="8dp"
        android:paddingEnd="8dp"
        android:paddingBottom="8dp"
        android:scrollbarStyle="outsideOverlay" />

</LinearLayout>
'''


def step_layouts():
    write(RES + '/layout/activity_main.xml', ACTIVITY_MAIN)
    write(RES + '/layout/item_channel.xml', ITEM_CHANNEL)
    write(RES + '/layout/item_user.xml', ITEM_USER)
    write(RES + '/layout/fragment_main_channels.xml', FRAGMENT_CHANNELS)
    print('OK ui layouts (4)')


# ----------------------------------------------------------------- 5. menu
def step_menu():
    p = RES + '/menu/main.xml'
    must(os.path.exists(p), 'overlay menu/main.xml missing (run mkadmin.py first)')
    m = read(p)
    if 'action_record' not in m:
        item = ('    <item\n'
                '        android:id="@+id/action_record"\n'
                '        android:orderInCategory="98"\n'
                '        android:title="@string/xray_record"\n'
                '        app:showAsAction="never" />\n'
                '    <item\n'
                '        android:id="@+id/action_share_screen"\n'
                '        android:orderInCategory="99"\n'
                '        android:title="@string/xray_share_screen"\n'
                '        app:showAsAction="never" />\n')
        idx = m.rfind('</menu>')
        must(idx > 0, 'cannot patch menu/main.xml')
        m = m[:idx] + item + m[idx:]
        write(p, m)
    print('OK menu: record + share screen')


# ----------------------------------------------------------------- 6. strings
STRINGS = {
    'xray_record': ('Screen recording', 'ضبط صفحه'),
    'xray_record_stop': ('Stop recording', 'توقف ضبط'),
    'xray_share_screen': ('Share screen (with sound)', 'اشتراک صفحه (با صدا)'),
    'xray_rec_on': ('Recording the screen…', 'در حال ضبط صفحه…'),
    'xray_rec_share': ('Recording the screen to share…', 'در حال ضبط صفحه برای اشتراک…'),
    'xray_rec_saved': ('Saved: %1$s', 'ذخیره شد: %1$s'),
    'xray_rec_denied': ('Screen capture permission was not granted', 'اجازه‌ی ضبط صفحه داده نشد'),
    'xray_rec_failed': ('Screen recording failed', 'ضبط صفحه ناموفق بود'),
    'xray_rec_stop_action': ('Stop', 'توقف'),
    'xray_rec_channel': ('Screen recording', 'ضبط صفحه'),
    'xray_rec_share_chooser': ('Send the screen recording', 'ارسال ضبط صفحه'),
    'xray_hub_record': ('Record screen (with sound)', 'ضبط صفحه (با صدا)'),
    'xray_hub_share': ('Share screen (record + send)', 'اشتراک صفحه (ضبط و ارسال)'),
    'xray_hub_title': ('Extra features', 'قابلیت‌های اضافه'),
}


def step_strings():
    en = ['<?xml version="1.0" encoding="utf-8"?>\n<resources>']
    fa = ['<?xml version="1.0" encoding="utf-8"?>\n<resources>']
    for k in sorted(STRINGS):
        e, f = STRINGS[k]
        en.append('    <string name="%s">%s</string>' % (k, e))
        fa.append('    <string name="%s">%s</string>' % (k, f))
    en.append('</resources>\n')
    fa.append('</resources>\n')
    write(RES + '/values/xray_ui_strings.xml', '\n'.join(en))
    write(RES + '/values-fa-rIR/xray_ui_strings.xml', '\n'.join(fa))
    print('OK ui strings (%d)' % len(STRINGS))


# ----------------------------------------------------------------- 7. developer names in English
def step_credits():
    p = RES + '/values-fa-rIR/xray_admin_strings.xml'
    must(os.path.exists(p), 'xray_admin_strings.xml missing')
    t = read(p)
    t2 = re.sub(r'(<string name="xray_developer_name">)[^<]*(</string>)',
                r'\1Hesam Bahmani\2', t)
    if t2 != t:
        write(p, t2)
    # make sure the English-only developer string is in place
    txt = read(p)
    m = re.search(r'<string name="xray_developer_name">([^<]*)</string>', txt)
    must(m is not None and m.group(1) == 'Hesam Bahmani', 'developer name not English')
    print('OK credits in English')


# ----------------------------------------------------------------- 8. java: recorder
SERVICE_JAVA = '''package dk.bearware.gui;

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
'''

CAPTURE_JAVA = '''package dk.bearware.gui;

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
'''


def step_java_new():
    write(JAV + '/dk/bearware/gui/XrayRecorderService.java', SERVICE_JAVA)
    write(JAV + '/dk/bearware/gui/XrayScreenCapture.java', CAPTURE_JAVA)
    print('OK recorder java (2)')


# ----------------------------------------------------------------- 9. MainActivity wiring
def step_mainactivity():
    p = JAV + '/dk/bearware/gui/MainActivity.java'
    must(os.path.exists(p), 'overlay MainActivity.java missing')
    t = read(p)

    if 'REQUEST_SCREENCAST' not in t:
        old = '                     REQUEST_SELECT_FILE = 4;'
        must(old in t, 'cannot patch request codes')
        t = t.replace(old, '                     REQUEST_SELECT_FILE = 4,\n'
                           '                     REQUEST_SCREENCAST = XrayScreenCapture.REQUEST_CODE;', 1)

    if 'R.id.action_record' not in t:
        anchor = '        if (itemId == R.id.action_admin) {'
        must(anchor in t, 'cannot find action_admin dispatch')
        new = ('        if (itemId == R.id.action_record) {\n'
               '            toggleXrayRecording();\n'
               '        } else if (itemId == R.id.action_share_screen) {\n'
               '            toggleXrayShare();\n'
               '        } else ' + anchor.strip() + '\n')
        t = t.replace(anchor, new, 1)

    if 'XrayScreenCapture.handleResult' not in t:
        anchor = '        if ((requestCode == REQUEST_SELECT_FILE) && (resultCode == RESULT_OK)) {'
        must(anchor in t, 'cannot find onActivityResult anchor')
        t = t.replace(anchor,
                      '        if (requestCode == REQUEST_SCREENCAST) {\n'
                      '            XrayScreenCapture.handleResult(this, resultCode, data, xrayShareMode);\n'
                      '            return;\n'
                      '        }\n' + anchor, 1)

    if 'private boolean xrayShareMode' not in t:
        # field next to the request code declaration block
        anchor = '    public final int REQUEST_EDITCHANNEL = 1,'
        must(anchor in t, 'cannot find request code block start')
        t = t.replace(anchor, '    private boolean xrayShareMode = false;\n\n' + anchor, 1)

    flat = '        findViewById(R.id.transmit_voice).setBackgroundColor(txEnabled ? Color.GREEN : Color.RED);'
    if flat in t:
        t = t.replace(flat,
                      '        findViewById(R.id.transmit_voice).setBackgroundResource(txEnabled'
                      ' ? R.drawable.xray_tx_btn_on : R.drawable.xray_tx_btn);', 1)

    if 'private void toggleXrayRecording()' not in t:
        idx = t.rfind('}')
        must(idx > 0, 'cannot find class end')
        helpers = '''
    /** Xray: start / stop a screen recording with microphone audio. */
    private void toggleXrayRecording() {
        if (XrayRecorderService.isRunning()) {
            XrayScreenCapture.stop(this);
            Toast.makeText(this, R.string.xray_record_stop, Toast.LENGTH_SHORT).show();
        }
        else {
            xrayShareMode = false;
            XrayScreenCapture.request(this);
        }
    }

    /** Xray: record the screen with sound, then offer to send it. */
    private void toggleXrayShare() {
        if (XrayRecorderService.isRunning()) {
            XrayScreenCapture.stop(this);
        }
        else {
            xrayShareMode = true;
            XrayScreenCapture.request(this);
        }
    }
'''
        t = t[:idx] + helpers + t[idx:]

    write(p, t)
    print('OK MainActivity: record + share screen')


# ----------------------------------------------------------------- 10. hub tiles
def step_hub():
    lay = RES + '/layout/activity_xray_admin.xml'
    must(os.path.exists(lay), 'hub layout missing (run mkadmin.py first)')
    l = read(lay)
    if 'btn_xray_record' not in l:
        tile = ('        <Button\n'
                '            android:id="@+id/btn_xray_record"\n'
                '            android:layout_width="match_parent"\n'
                '            android:layout_height="64dp"\n'
                '            android:layout_marginTop="12dp"\n'
                '            android:background="@drawable/xray_btn_ghost"\n'
                '            android:text="@string/xray_hub_record"\n'
                '            android:textColor="@color/xray_accent"\n'
                '            android:textSize="17sp" />\n\n'
                '        <Button\n'
                '            android:id="@+id/btn_xray_share"\n'
                '            android:layout_width="match_parent"\n'
                '            android:layout_height="64dp"\n'
                '            android:layout_marginTop="8dp"\n'
                '            android:background="@drawable/xray_btn_ghost"\n'
                '            android:text="@string/xray_hub_share"\n'
                '            android:textColor="@color/xray_accent"\n'
                '            android:textSize="17sp" />\n')
        idx = l.rfind('</LinearLayout>')
        must(idx > 0, 'cannot patch hub layout')
        l = l[:idx] + tile + l[idx:]
        write(lay, l)

    p = JAV + '/dk/bearware/gui/XrayAdminActivity.java'
    must(os.path.exists(p), 'hub java missing')
    a = read(p)
    if 'btn_xray_record' not in a:
        anchor = '        }, 400);\n'
        must(anchor in a, 'cannot find hub announcement anchor')
        bind = (anchor +
                '\n'
                '        View rec = findViewById(R.id.btn_xray_record);\n'
                '        if (rec != null) {\n'
                '            rec.setOnClickListener(new View.OnClickListener() {\n'
                '                public void onClick(View view) {\n'
                '                    if (XrayRecorderService.isRunning()) {\n'
                '                        XrayScreenCapture.stop(XrayAdminActivity.this);\n'
                '                    }\n'
                '                    else {\n'
                '                        xrayShare = false;\n'
                '                        XrayScreenCapture.request(XrayAdminActivity.this);\n'
                '                    }\n'
                '                }\n'
                '            });\n'
                '        }\n'
                '        View share = findViewById(R.id.btn_xray_share);\n'
                '        if (share != null) {\n'
                '            share.setOnClickListener(new View.OnClickListener() {\n'
                '                public void onClick(View view) {\n'
                '                    if (XrayRecorderService.isRunning()) {\n'
                '                        XrayScreenCapture.stop(XrayAdminActivity.this);\n'
                '                    }\n'
                '                    else {\n'
                '                        xrayShare = true;\n'
                '                        XrayScreenCapture.request(XrayAdminActivity.this);\n'
                '                    }\n'
                '                }\n'
                '            });\n'
                '        }\n')
        a = a.replace(anchor, bind, 1)
        idx = a.rfind('}')
        extra = ('\n'
                 '    private boolean xrayShare = false;\n'
                 '\n'
                 '    @Override\n'
                 '    protected void onActivityResult(int requestCode, int resultCode, android.content.Intent data) {\n'
                 '        if (requestCode == XrayScreenCapture.REQUEST_CODE) {\n'
                 '            XrayScreenCapture.handleResult(this, resultCode, data, xrayShare);\n'
                 '            return;\n'
                 '        }\n'
                 '        super.onActivityResult(requestCode, resultCode, data);\n'
                 '    }\n')
        a = a[:idx] + extra + a[idx:]
        write(p, a)
    print('OK hub: record + share tiles')



FILE_PATHS = '''<?xml version="1.0" encoding="utf-8"?>
<paths xmlns:android="http://schemas.android.com/apk/res/android">
    <external-files-path name="xray_movies" path="Movies/" />
</paths>
'''


def step_file_paths():
    write(RES + '/xml/xray_file_paths.xml', FILE_PATHS)
    print('OK file provider paths')


# ----------------------------------------------------------------- 11. manifest
def step_manifest():
    p = OV + '/AndroidManifest.xml'
    must(os.path.exists(p), 'overlay manifest missing (run mkadmin.py first)')
    m = read(p)
    if 'FOREGROUND_SERVICE_MEDIA_PROJECTION' not in m:
        anchor = '<uses-permission android:name="android.permission.FOREGROUND_SERVICE_MICROPHONE">'
        must(anchor in m, 'cannot find foreground microphone permission')
        add = ('<uses-permission android:name="android.permission.FOREGROUND_SERVICE_MEDIA_PROJECTION"></uses-permission>\n'
               '    ')
        if anchor.endswith('</uses-permission>'):
            t = m.replace(anchor, anchor + '\n    ' + add.strip(), 1)
        else:
            t = m.replace(anchor, add + anchor, 1)
        m = t
    if 'xrayfiles' not in m:
        idx = m.rfind('</application>')
        must(idx > 0, 'cannot patch manifest application')
        prov = ('        <provider\n'
                '            android:name="androidx.core.content.FileProvider"\n'
                '            android:authorities="${applicationId}.xrayfiles"\n'
                '            android:exported="false"\n'
                '            android:grantUriPermissions="true">\n'
                '            <meta-data\n'
                '                android:name="android.support.FILE_PROVIDER_PATHS"\n'
                '                android:resource="@xml/xray_file_paths" />\n'
                '        </provider>\n')
        m = m[:idx] + prov + m[idx:]
    if 'XrayRecorderService' not in m:
        idx = m.rfind('</application>')
        must(idx > 0, 'cannot patch manifest application')
        svc = ('        <service\n'
               '            android:name="dk.bearware.gui.XrayRecorderService"\n'
               '            android:exported="false"\n'
               '            android:foregroundServiceType="mediaProjection" />\n')
        m = m[:idx] + svc + m[idx:]
    write(p, m)
    print('OK manifest: recorder permission + service')


def main():
    step_palette()
    step_drawables()
    step_styles()
    step_layouts()
    step_menu()
    step_strings()
    step_credits()
    step_java_new()
    step_mainactivity()
    step_hub()
    step_file_paths()
    step_manifest()
    print('UI DONE')


if __name__ == '__main__':
    main()

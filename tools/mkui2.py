#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Xray UI v2: real live desktop sharing (screen into the TeamTalk channel) + a
clean modern look. Replaces mkui.py.

Pipeline: mkoverlay.py -> mkadmin.py -> mkui2.py -> mkupdate.py -> verify.py
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


# --------------------------------------------------------------- 1. palette
PALETTE = '''<?xml version="1.0" encoding="utf-8"?>
<resources>
    <color name="xray_bg">#070A10</color>
    <color name="xray_bg2">#0C1119</color>
    <color name="xray_surface">#111925</color>
    <color name="xray_surface2">#18222F</color>
    <color name="xray_stroke">#23303F</color>
    <color name="xray_accent">#22D3EE</color>
    <color name="xray_accent_dim">#0E7490</color>
    <color name="xray_accent_soft">#3322D3EE</color>
    <color name="xray_violet">#8B5CF6</color>
    <color name="xray_text">#F1F5F9</color>
    <color name="xray_text_dim">#94A3B8</color>
    <color name="xray_ok">#34D399</color>
    <color name="xray_warn">#FBBF24</color>
    <color name="xray_danger">#F87171</color>
    <color name="xray_tx">#EF4444</color>
    <color name="xray_tx_dim">#991B1B</color>
    <color name="xray_tx_on">#10B981</color>
    <color name="xray_tx_on_dim">#047857</color>
</resources>
'''

DRAWABLES = {
    # background gradient used by the hero header
    'xray_hero.xml': '''<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <gradient android:startColor="#12202E" android:centerColor="#0E2A38" android:endColor="#111925"
        android:angle="315" />
    <corners android:radius="20dp" />
    <stroke android:width="1dp" android:color="#1E3A4C" />
</shape>
''',
    'xray_card.xml': '''<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <gradient android:startColor="#131C28" android:endColor="#0D141E" android:angle="270" />
    <corners android:radius="22dp" />
    <stroke android:width="1dp" android:color="@color/xray_stroke" />
</shape>
''',
    'xray_row.xml': '''<?xml version="1.0" encoding="utf-8"?>
<ripple xmlns:android="http://schemas.android.com/apk/res/android" android:color="#3322D3EE">
    <item>
        <shape android:shape="rectangle">
            <solid android:color="@color/xray_surface" />
            <corners android:radius="16dp" />
            <stroke android:width="1dp" android:color="#1B2634" />
        </shape>
    </item>
</ripple>
''',
    'xray_avatar.xml': '''<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="oval">
    <gradient android:startColor="#0E7490" android:endColor="#7C3AED" android:angle="315" />
    <stroke android:width="1dp" android:color="#3322D3EE" />
</shape>
''',
    'xray_pill.xml': '''<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <solid android:color="#1B2A38" />
    <corners android:radius="14dp" />
    <stroke android:width="1dp" android:color="#25455A" />
</shape>
''',
    'xray_pill_accent.xml': '''<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <solid android:color="@color/xray_accent_soft" />
    <corners android:radius="14dp" />
</shape>
''',
    'xray_btn_primary.xml': '''<?xml version="1.0" encoding="utf-8"?>
<ripple xmlns:android="http://schemas.android.com/apk/res/android" android:color="#6622D3EE">
    <item>
        <shape android:shape="rectangle">
            <gradient android:startColor="#22D3EE" android:endColor="#0891B2" android:angle="0" />
            <corners android:radius="16dp" />
        </shape>
    </item>
</ripple>
''',
    'xray_btn_ghost.xml': '''<?xml version="1.0" encoding="utf-8"?>
<ripple xmlns:android="http://schemas.android.com/apk/res/android" android:color="#3322D3EE">
    <item>
        <shape android:shape="rectangle">
            <solid android:color="#111B26" />
            <corners android:radius="14dp" />
            <stroke android:width="1dp" android:color="#2A4A5E" />
        </shape>
    </item>
</ripple>
''',
    'xray_tile.xml': '''<?xml version="1.0" encoding="utf-8"?>
<ripple xmlns:android="http://schemas.android.com/apk/res/android" android:color="#4422D3EE">
    <item>
        <shape android:shape="rectangle">
            <gradient android:startColor="#14202C" android:endColor="#0E1721" android:angle="270" />
            <corners android:radius="18dp" />
            <stroke android:width="1dp" android:color="#22364A" />
        </shape>
    </item>
</ripple>
''',
    'xray_tx_btn.xml': '''<?xml version="1.0" encoding="utf-8"?>
<ripple xmlns:android="http://schemas.android.com/apk/res/android" android:color="#66FFFFFF">
    <item>
        <shape android:shape="oval">
            <gradient android:startColor="#F87171" android:endColor="#B91C1C" android:angle="270" />
        </shape>
    </item>
</ripple>
''',
    'xray_tx_btn_on.xml': '''<?xml version="1.0" encoding="utf-8"?>
<ripple xmlns:android="http://schemas.android.com/apk/res/android" android:color="#66FFFFFF">
    <item>
        <shape android:shape="oval">
            <gradient android:startColor="#34D399" android:endColor="#059669" android:angle="270" />
        </shape>
    </item>
</ripple>
''',
    'xray_ic_share.xml': '''<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="24dp" android:height="24dp"
    android:viewportWidth="24" android:viewportHeight="24">
    <path android:fillColor="#22D3EE"
        android:pathData="M4,3h16a2,2 0,0 1,2 2v10a2,2 0,0 1,-2 2h-4v2h2v2H6v-2h2v-2H4a2,2 0,0 1,-2 -2V5a2,2 0,0 1,2 -2zM12,6l-4,4h2.5v4h3v-4H16z" />
</vector>
''',
    'xray_ic_update.xml': '''<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="24dp" android:height="24dp"
    android:viewportWidth="24" android:viewportHeight="24">
    <path android:fillColor="#22D3EE"
        android:pathData="M12,4V1L8,5l4,4V6a6,6 0,1 1,-6 6H4a8,8 0,1 0,8 -8z" />
</vector>
''',
    'xray_divider.xml': '''<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <solid android:color="#1B2634" />
    <size android:height="1dp" />
</shape>
''',
}


def step_assets():
    write(RES + '/values/xray_palette.xml', PALETTE)
    for name, body in DRAWABLES.items():
        write(RES + '/drawable/' + name, body)
    print('OK palette + %d drawables' % len(DRAWABLES))


# --------------------------------------------------------------- 2. styles
def step_styles():
    p = RES + '/values/styles.xml'
    must(os.path.exists(p), 'styles.xml missing (run mkoverlay first)')
    t = read(p)

    # keep AppTheme.Xray (accessibility) byte-for-byte; only retheme the base style
    body = '''
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
    '''
    t = re.sub(r'<style name="AppTheme" parent="Theme\.AppCompat\.DayNight"\s*/>',
               '<style name="AppTheme" parent="Theme.AppCompat.DayNight">' + body + '</style>', t, count=1)
    t = re.sub(r'<style name="AppTheme" parent="Theme\.AppCompat\.DayNight">.*?</style>',
               '<style name="AppTheme" parent="Theme.AppCompat.DayNight">' + body + '</style>', t, count=1, flags=re.S)
    t = re.sub(r'<style name="AppTheme\.NoActionBar"[^>]*>.*?</style>',
               '''<style name="AppTheme.NoActionBar" parent="Theme.AppCompat.DayNight">
        <item name="windowActionBar">false</item>
        <item name="windowNoTitle">true</item>
        <item name="colorPrimary">@color/xray_surface</item>
        <item name="colorPrimaryDark">@color/xray_bg</item>
        <item name="colorAccent">@color/xray_accent</item>
        <item name="android:windowBackground">@color/xray_bg</item>
        <item name="android:textColorPrimary">@color/xray_text</item>
        <item name="android:textColorSecondary">@color/xray_text_dim</item>
    </style>''', t, count=1, flags=re.S)

    if 'XrayActionBarTitle' not in t:
        extra = '''
    <style name="XrayActionBar" parent="Widget.AppCompat.ActionBar.Solid">
        <item name="background">@color/xray_surface</item>
        <item name="elevation">8dp</item>
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
        <item name="android:textColor">#04212B</item>
        <item name="android:textAllCaps">false</item>
        <item name="android:textStyle">bold</item>
        <item name="android:minHeight">48dp</item>
        <item name="android:stateListAnimator">@null</item>
    </style>

    <style name="XrayListView" parent="Widget.AppCompat.ListView">
        <item name="android:divider">@color/xray_bg</item>
        <item name="android:dividerHeight">6dp</item>
        <item name="android:paddingStart">10dp</item>
        <item name="android:paddingEnd">10dp</item>
        <item name="android:paddingTop">6dp</item>
        <item name="android:paddingBottom">6dp</item>
        <item name="android:clipToPadding">false</item>
        <item name="android:scrollbarStyle">outsideOverlay</item>
    </style>

    <style name="XrayChatName">
        <item name="android:textColor">@color/xray_text</item>
        <item name="android:textSize">17sp</item>
        <item name="android:textStyle">bold</item>
        <item name="android:letterSpacing">0.01</item>
    </style>

    <style name="XrayChatSub">
        <item name="android:textColor">@color/xray_text_dim</item>
        <item name="android:textSize">13sp</item>
    </style>

    <style name="XrayStat">
        <item name="android:textColor">@color/xray_text_dim</item>
        <item name="android:textSize">11sp</item>
        <item name="android:maxLines">1</item>
    </style>

    <style name="XrayTile">
        <item name="android:layout_width">match_parent</item>
        <item name="android:layout_height">62dp</item>
        <item name="android:layout_marginTop">10dp</item>
        <item name="android:background">@drawable/xray_tile</item>
        <item name="android:textColor">@color/xray_text</item>
        <item name="android:textAllCaps">false</item>
        <item name="android:textSize">16sp</item>
        <item name="android:gravity">center_vertical|start</item>
        <item name="android:paddingStart">18dp</item>
        <item name="android:paddingEnd">18dp</item>
        <item name="android:stateListAnimator">@null</item>
    </style>

    <style name="XrayAccentTile" parent="XrayTile">
        <item name="android:background">@drawable/xray_btn_ghost</item>
        <item name="android:textColor">@color/xray_accent</item>
        <item name="android:textStyle">bold</item>
    </style>
'''
        idx = t.rfind('</resources>')
        must(idx > 0, 'styles.xml has no resources end')
        t = t[:idx] + extra + t[idx:]
    write(p, t)
    print('OK styles (AppTheme.Xray untouched)')


# --------------------------------------------------------------- 3. layouts
ACTIVITY_MAIN = '''<LinearLayout
    xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:background="@color/xray_bg"
    android:orientation="vertical"
    tools:context=".MainActivity">

    <com.google.android.material.tabs.TabLayout
        android:id="@+id/tab_layout"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:background="@color/xray_bg"
        android:paddingTop="8dp"
        android:paddingBottom="4dp"
        app:tabGravity="fill"
        app:tabIndicatorColor="@color/xray_accent"
        app:tabIndicatorHeight="3dp"
        app:tabIndicatorFullWidth="false"
        app:tabRippleColor="@color/xray_accent_soft"
        app:tabSelectedTextColor="@color/xray_accent"
        app:tabTextColor="@color/xray_text_dim" />

    <View
        android:layout_width="match_parent"
        android:layout_height="1dp"
        android:background="@color/xray_stroke" />

    <androidx.viewpager.widget.ViewPager
        android:id="@+id/pager"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:layout_weight="1.0"
        android:background="@color/xray_bg" />

    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:layout_marginStart="10dp"
        android:layout_marginEnd="10dp"
        android:layout_marginBottom="10dp"
        android:background="@drawable/xray_card"
        android:elevation="10dp"
        android:orientation="vertical"
        android:padding="14dp">

        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:background="@drawable/xray_hero"
            android:gravity="center_vertical"
            android:orientation="horizontal"
            android:paddingStart="14dp"
            android:paddingTop="10dp"
            android:paddingEnd="14dp"
            android:paddingBottom="10dp">

            <TextView
                android:id="@+id/connectionstat_textview"
                android:layout_width="0dp"
                android:layout_height="wrap_content"
                android:layout_weight="1"
                android:ellipsize="end"
                android:maxLines="1"
                android:text=""
                android:textColor="@color/xray_accent"
                android:textSize="12sp"
                android:textStyle="bold" />

            <TextView
                android:id="@+id/pingstat_textview"
                style="@style/XrayStat"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:layout_marginEnd="10dp"
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
            android:orientation="horizontal"
            android:paddingTop="10dp">

            <ImageButton
                android:id="@+id/speakerBtn"
                android:layout_width="46dp"
                android:layout_height="46dp"
                android:background="?android:attr/selectableItemBackgroundBorderless"
                android:contentDescription="@string/speaker_mute"
                android:src="@drawable/speaker_blue" />

            <LinearLayout
                android:layout_width="0dp"
                android:layout_height="wrap_content"
                android:layout_weight="1"
                android:orientation="vertical">

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
                    android:contentDescription="@string/mastervolume"
                    android:maxHeight="4dp"
                    android:minHeight="4dp"
                    android:progressTint="@color/xray_accent"
                    android:thumbTint="@color/xray_accent"
                    android:progressBackgroundTint="@color/xray_stroke" />
            </LinearLayout>
        </LinearLayout>

        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:gravity="center_vertical"
            android:orientation="horizontal">

            <ImageButton
                android:id="@+id/voxSwitch"
                android:layout_width="46dp"
                android:layout_height="46dp"
                android:background="?android:attr/selectableItemBackgroundBorderless"
                android:contentDescription="@string/voice_activation_on"
                android:src="@drawable/mic_green" />

            <LinearLayout
                android:layout_width="0dp"
                android:layout_height="wrap_content"
                android:layout_weight="1"
                android:orientation="vertical">

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
                    android:contentDescription="@string/micgain"
                    android:maxHeight="4dp"
                    android:minHeight="4dp"
                    android:progressTint="@color/xray_violet"
                    android:thumbTint="@color/xray_violet"
                    android:progressBackgroundTint="@color/xray_stroke" />
            </LinearLayout>

            <Button
                android:id="@+id/transmit_voice"
                android:layout_width="84dp"
                android:layout_height="84dp"
                android:layout_marginStart="12dp"
                android:background="@drawable/xray_tx_btn"
                android:elevation="12dp"
                android:text="@string/button_tx"
                android:textColor="#FFFFFFFF"
                android:textSize="15sp"
                android:textStyle="bold" />
        </LinearLayout>
    </LinearLayout>
</LinearLayout>
'''

ITEM_CHANNEL = '''<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:background="@drawable/xray_row"
    android:gravity="center_vertical"
    android:minHeight="66dp"
    android:orientation="horizontal"
    android:paddingStart="12dp"
    android:paddingTop="10dp"
    android:paddingEnd="10dp"
    android:paddingBottom="10dp">

    <FrameLayout
        android:layout_width="40dp"
        android:layout_height="40dp"
        android:background="@drawable/xray_avatar">

        <ImageView
            android:id="@+id/channelicon"
            android:layout_width="22dp"
            android:layout_height="22dp"
            android:layout_gravity="center"
            android:importantForAccessibility="no"
            android:src="@drawable/channel_green" />
    </FrameLayout>

    <LinearLayout
        android:layout_width="0dp"
        android:layout_height="wrap_content"
        android:layout_marginStart="12dp"
        android:layout_weight="1"
        android:orientation="vertical">

        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:gravity="center_vertical"
            android:orientation="horizontal">

            <TextView
                android:id="@+id/channelname"
                style="@style/XrayChatName"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:ellipsize="end"
                android:maxLines="1"
                android:text="" />

            <TextView
                android:id="@+id/population"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:layout_marginStart="8dp"
                android:background="@drawable/xray_pill_accent"
                android:paddingStart="9dp"
                android:paddingTop="2dp"
                android:paddingEnd="9dp"
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
            android:ellipsize="end"
            android:maxLines="1"
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
        android:paddingStart="16dp"
        android:paddingEnd="16dp"
        android:stateListAnimator="@null"
        android:text="@string/action_join"
        android:textColor="@color/xray_accent"
        android:textSize="13sp"
        android:textStyle="bold" />
</LinearLayout>
'''

ITEM_USER = '''<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:background="@drawable/xray_row"
    android:gravity="center_vertical"
    android:minHeight="66dp"
    android:orientation="horizontal"
    android:paddingStart="12dp"
    android:paddingTop="10dp"
    android:paddingEnd="10dp"
    android:paddingBottom="10dp">

    <FrameLayout
        android:layout_width="40dp"
        android:layout_height="40dp"
        android:background="@drawable/xray_avatar">

        <ImageView
            android:id="@+id/usericon"
            android:layout_width="24dp"
            android:layout_height="24dp"
            android:layout_gravity="center"
            android:importantForAccessibility="no"
            android:src="@drawable/man_blue" />
    </FrameLayout>

    <LinearLayout
        android:layout_width="0dp"
        android:layout_height="wrap_content"
        android:layout_marginStart="12dp"
        android:layout_weight="1"
        android:orientation="vertical">

        <TextView
            android:id="@+id/nickname"
            style="@style/XrayChatName"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:ellipsize="end"
            android:maxLines="1" />

        <TextView
            android:id="@+id/status"
            style="@style/XrayChatSub"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:ellipsize="end"
            android:maxLines="1" />
    </LinearLayout>

    <Button
        android:id="@+id/msg_btn"
        android:layout_width="wrap_content"
        android:layout_height="40dp"
        android:background="@drawable/xray_btn_ghost"
        android:clickable="true"
        android:focusable="false"
        android:minWidth="0dp"
        android:paddingStart="16dp"
        android:paddingEnd="16dp"
        android:stateListAnimator="@null"
        android:text="@string/button_msg"
        android:textColor="@color/xray_accent"
        android:textSize="13sp"
        android:textStyle="bold" />
</LinearLayout>
'''

FRAGMENT_CHANNELS = '''<?xml version="1.0" encoding="utf-8"?>
<FrameLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:background="@color/xray_bg">

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
</FrameLayout>
'''

HUB_LAYOUT = '''<?xml version="1.0" encoding="utf-8"?>
<ScrollView xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:background="@color/xray_bg"
    android:fillViewport="true">

    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:orientation="vertical"
        android:paddingStart="14dp"
        android:paddingTop="14dp"
        android:paddingEnd="14dp"
        android:paddingBottom="24dp">

        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:background="@drawable/xray_hero"
            android:orientation="vertical"
            android:padding="18dp">

            <TextView
                android:id="@+id/txt_xray_admin_title"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:text="@string/xray_admin"
                android:textColor="@color/xray_text"
                android:textSize="22sp"
                android:textStyle="bold" />

            <TextView
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:layout_marginTop="4dp"
                android:text="@string/xray_admin_subtitle"
                android:textColor="@color/xray_text_dim"
                android:textSize="13sp" />
        </LinearLayout>

        <Button
            android:id="@+id/btn_xray_share"
            style="@style/XrayAccentTile"
            android:drawableStart="@drawable/xray_ic_share"
            android:drawablePadding="14dp"
            android:text="@string/xray_hub_share" />

        <Button
            android:id="@+id/btn_xray_user_accounts"
            style="@style/XrayTile"
            android:text="@string/xray_user_accounts" />

        <Button
            android:id="@+id/btn_xray_server_props"
            style="@style/XrayTile"
            android:text="@string/xray_server_props" />

        <Button
            android:id="@+id/btn_xray_server_info"
            style="@style/XrayTile"
            android:text="@string/xray_server_info" />

        <Button
            android:id="@+id/btn_xray_move_users"
            style="@style/XrayTile"
            android:text="@string/xray_move_users" />

        <Button
            android:id="@+id/btn_xray_channel_bans"
            style="@style/XrayTile"
            android:text="@string/xray_channel_bans" />

        <Button
            android:id="@+id/btn_xray_server_bans"
            style="@style/XrayTile"
            android:text="@string/xray_server_bans" />

        <Button
            android:id="@+id/btn_xray_update"
            style="@style/XrayTile"
            android:drawableStart="@drawable/xray_ic_update"
            android:drawablePadding="14dp"
            android:text="@string/xray_hub_update" />
    </LinearLayout>
</ScrollView>
'''


def step_layouts():
    write(RES + '/layout/activity_main.xml', ACTIVITY_MAIN)
    write(RES + '/layout/item_channel.xml', ITEM_CHANNEL)
    write(RES + '/layout/item_user.xml', ITEM_USER)
    write(RES + '/layout/fragment_main_channels.xml', FRAGMENT_CHANNELS)
    write(RES + '/layout/activity_xray_admin.xml', HUB_LAYOUT)
    print('OK layouts (5)')


# --------------------------------------------------------------- 4. menu
def step_menu():
    p = RES + '/menu/main.xml'
    must(os.path.exists(p), 'menu/main.xml missing (run mkadmin first)')
    m = read(p)
    # drop the old two entries
    m = re.sub(r'\s*<item\s+android:id="@\+id/action_record".*?/>\s*', '\n', m, flags=re.S)
    m = re.sub(r'\s*<item\s+android:id="@\+id/action_share_screen".*?/>\s*', '\n', m, flags=re.S)
    item = ('    <item\n'
            '        android:id="@+id/action_share_screen"\n'
            '        android:orderInCategory="98"\n'
            '        android:icon="@drawable/xray_ic_share"\n'
            '        android:title="@string/xray_share_screen"\n'
            '        app:showAsAction="never" />\n')
    idx = m.rfind('</menu>')
    must(idx > 0, 'menu/main.xml broken')
    m = m[:idx] + item + m[idx:]
    write(p, m)
    print('OK menu: single screen-share action')


# --------------------------------------------------------------- 5. strings
STRINGS = {
    'xray_share_screen': ('Share screen', 'اشتراک صفحه'),
    'xray_share_on': ('Screen sharing started', 'اشتراک صفحه شروع شد'),
    'xray_share_off': ('Screen sharing stopped', 'اشتراک صفحه قطع شد'),
    'xray_share_need_channel': ('Join a channel first', 'اول وارد یک کانال شو'),
    'xray_share_denied': ('Screen capture permission was not granted', 'اجازه‌ی ضبط صفحه داده نشد'),
    'xray_share_failed': ('Screen sharing failed', 'اشتراک صفحه انجام نشد'),
    'xray_share_channel': ('Screen sharing', 'اشتراک صفحه'),
    'xray_share_alive': ('Your screen is being shared in the channel', 'صفحه‌ات دارد در کانال به اشتراک گذاشته می‌شود'),
    'xray_share_stop_action': ('Stop', 'توقف'),
    'xray_hub_share': ('Share screen (live, with sound)', 'اشتراک صفحه (زنده، با صدا)'),
    'xray_admin_subtitle': ('Xray extras: live screen sharing, server tools, updates',
                            'قابلیت‌های Xray: اشتراک زنده‌ی صفحه، ابزارهای سرور، به‌روزرسانی'),
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
    print('OK strings (%d)' % len(STRINGS))


# --------------------------------------------------------------- 6. credits
def step_credits():
    p = RES + '/values-fa-rIR/xray_admin_strings.xml'
    must(os.path.exists(p), 'xray_admin_strings.xml missing')
    t = read(p)
    t2 = re.sub(r'(<string name="xray_developer_name">)[^<]*(</string>)',
                r'\1Hesam Bahmani\2', t)
    if t2 != t:
        write(p, t2)
    m = re.search(r'<string name="xray_developer_name">([^<]*)</string>', read(p))
    must(m is not None and m.group(1) == 'Hesam Bahmani', 'developer name not English')
    print('OK developer credit: English only')


# --------------------------------------------------------------- 7. share java
DESKTOP_JAVA = '''package dk.bearware.gui;

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
    static volatile String lastError = "";

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
        if (client == null) {
            lastError = "client null";
            return false;
        }
        if (data == null) {
            lastError = "intent null";
            return false;
        }
        if (resultCode != Activity.RESULT_OK) {
            lastError = "resultCode " + resultCode;
            return false;
        }
        XrayDesktopShare s = new XrayDesktopShare(client);
        boolean ok = s.begin(ctx, resultCode, data);
        if (ok) {
            instance = s;
            logCtx(ctx, "started " + s.width + "x" + s.height);
        }
        return ok;
    }

    public static String lastError() {
        return lastError == null ? "" : lastError;
    }

    static void logCtx(Context ctx, String msg) {
        Log.i(TAG, msg);
        try {
            java.io.File dir = ctx.getExternalFilesDir(null);
            if (dir == null) {
                return;
            }
            java.io.File f = new java.io.File(dir, "xray_share.log");
            if (f.length() > 60000) {
                f.delete();
            }
            java.io.FileWriter w = new java.io.FileWriter(f, true);
            w.write(new java.text.SimpleDateFormat("MM-dd HH:mm:ss", java.util.Locale.US)
                    .format(new java.util.Date()) + "  " + msg + "\n");
            w.close();
        }
        catch (Exception ignored) {
        }
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
                lastError = "projection null";
                return false;
            }
            DisplayMetrics metrics = ctx.getResources().getDisplayMetrics();
            int srcW = metrics.widthPixels;
            int srcH = metrics.heightPixels;
            int dpi = metrics.densityDpi;
            if (srcW < 2 || srcH < 2) {
                srcW = 720;
                srcH = 1280;
                dpi = 320;
            }
            int sw = Math.min(MAX_WIDTH, srcW);
            int sh = (int) ((long) srcH * sw / Math.max(1, srcW));
            width = Math.max(2, sw & ~1);
            height = Math.max(2, sh & ~1);
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
                    dpi,
                    DisplayManager.VIRTUAL_DISPLAY_FLAG_AUTO_MIRROR,
                    reader.getSurface(), null, handler);
            running = true;
            return true;
        }
        catch (Throwable e) {
            lastError = e.getClass().getSimpleName() + ": " + e.getMessage();
            logCtx(ctx, "begin failed: " + lastError);
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
                toast(getString(R.string.xray_share_failed) + " - " + lastError());
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
'''


def step_java():
    # drop the old recording implementation
    for old in ('XrayRecorderService.java', 'XrayScreenCapture.java', 'XrayDesktopShare.java'):
        p = JAV + '/dk/bearware/gui/' + old
        if old != 'XrayDesktopShare.java' and os.path.exists(p):
            os.remove(p)
            print('removed', old)
    write(JAV + '/dk/bearware/gui/XrayDesktopShare.java', DESKTOP_JAVA)
    print('OK XrayDesktopShare.java')


# --------------------------------------------------------------- 8. MainActivity
def step_mainactivity():
    p = JAV + '/dk/bearware/gui/MainActivity.java'
    must(os.path.exists(p), 'overlay MainActivity.java missing')
    t = read(p)

    # old wiring removal (from earlier generator versions)
    t = re.sub(r'\n\s*if \(itemId == R\.id\.action_record\) \{.*?\n\s*\} else ', '\n        ', t, count=1, flags=re.S)
    t = t.replace('                     REQUEST_SCREENCAST = XrayScreenCapture.REQUEST_CODE;',
                  '                     REQUEST_SCREENCAST = XrayDesktopShare.REQUEST_CODE;')
    if 'REQUEST_SCREENCAST' not in t:
        old = '                     REQUEST_SELECT_FILE = 4;'
        must(old in t, 'request codes not found')
        t = t.replace(old, '                     REQUEST_SELECT_FILE = 4,\n'
                           '                     REQUEST_SCREENCAST = XrayDesktopShare.REQUEST_CODE;', 1)

    # menu dispatch: single share toggle
    anchor = '        if (itemId == R.id.action_admin) {'
    must(anchor in t, 'action_admin dispatch not found')
    if 'toggleXrayShare' not in t:
        t = t.replace(anchor,
                      '        if (itemId == R.id.action_share_screen) {\n'
                      '            toggleXrayShare();\n'
                      '        }\n' + anchor, 1)

    # result handling
    if 'ShareService.startWithResult' not in t:
        anchor2 = '        if ((requestCode == REQUEST_SELECT_FILE) && (resultCode == RESULT_OK)) {'
        must(anchor2 in t, 'onActivityResult anchor missing')
        t = t.replace(anchor2,
                      '        if (requestCode == REQUEST_SCREENCAST) {\n'
                      '            if (resultCode == RESULT_OK && data != null) {\n'
                      '                XrayDesktopShare.ShareService.startWithResult(this, getClient(),\n'
                      '                        resultCode, data);\n'
                      '            }\n'
                      '            else {\n'
                      '                Toast.makeText(this, R.string.xray_share_denied, Toast.LENGTH_LONG).show();\n'
                      '            }\n'
                      '            return;\n'
                      '        }\n' + anchor2, 1)

    # helper
    if 'private void toggleXrayShare()' not in t:
        idx = t.rfind('}')
        must(idx > 0, 'class end not found')
        helper = '''
    /** Xray: one toggle for live screen / desktop sharing into the current channel. */
    private void toggleXrayShare() {
        if (XrayDesktopShare.isSharing()) {
            XrayDesktopShare.ShareService.requestStop(this);
            Toast.makeText(this, R.string.xray_share_off, Toast.LENGTH_SHORT).show();
        }
        else {
            XrayDesktopShare.request(this, getClient());
        }
    }
'''
        t = t[:idx] + helper + t[idx:]

    # transmit button background must stay the circular drawable
    t = t.replace('transmitBtn.setBackgroundColor(txEnabled ? Color.GREEN : Color.RED);',
                  'transmitBtn.setBackgroundResource(txEnabled ? R.drawable.xray_tx_btn_on : R.drawable.xray_tx_btn);')

    write(p, t)
    print('OK MainActivity: single live share toggle')


# --------------------------------------------------------------- 9. hub
def step_hub():
    p = JAV + '/dk/bearware/gui/XrayAdminActivity.java'
    must(os.path.exists(p), 'hub java missing')
    a = read(p)

    # strip previous record/share bindings, keep one share binding
    a = re.sub(r'\n\s*View rec = findViewById\(R\.id\.btn_xray_record\);.*?\n\s*\}\n', '\n', a, count=1, flags=re.S)
    a = re.sub(r'\n\s*View share = findViewById\(R\.id\.btn_xray_share\);.*?\n\s*\}\n', '\n', a, count=1, flags=re.S)

    if 'btn_xray_share' not in a:
        anchor = '        }, 400);\n'
        must(anchor in a, 'hub announcement anchor missing')
        block = (anchor +
                 '\n'
                 '        View share = findViewById(R.id.btn_xray_share);\n'
                 '        if (share != null) {\n'
                 '            share.setOnClickListener(new View.OnClickListener() {\n'
                 '                public void onClick(View view) {\n'
                 '                    if (XrayDesktopShare.isSharing()) {\n'
                 '                        XrayDesktopShare.ShareService.requestStop(XrayAdminActivity.this);\n'
                 '                    }\n'
                 '                    else {\n'
                 '                        XrayDesktopShare.request(XrayAdminActivity.this,\n'
                 '                                MainActivity.activeClient());\n'
                 '                    }\n'
                 '                }\n'
                 '            });\n'
                 '        }\n')
        a = a.replace(anchor, block, 1)

    # onActivityResult for the share consent dialog
    if 'onActivityResult' not in a:
        idx = a.rfind('}')
        extra = ('\n'
                 '    @Override\n'
                 '    protected void onActivityResult(int requestCode, int resultCode, android.content.Intent data) {\n'
                 '        if (requestCode == XrayDesktopShare.REQUEST_CODE) {\n'
                 '            if (resultCode == RESULT_OK && data != null) {\n'
                 '                XrayDesktopShare.ShareService.startWithResult(this,\n'
                 '                        MainActivity.activeClient(), resultCode, data);\n'
                 '            }\n'
                 '            else {\n'
                 '                android.widget.Toast.makeText(this, R.string.xray_share_denied,\n'
                 '                        android.widget.Toast.LENGTH_LONG).show();\n'
                 '            }\n'
                 '            return;\n'
                 '        }\n'
                 '        super.onActivityResult(requestCode, resultCode, data);\n'
                 '    }\n')
        a = a[:idx] + extra + a[idx:]
    write(p, a)
    print('OK hub: share tile')


def step_active_client():
    p = JAV + '/dk/bearware/gui/MainActivity.java'
    t = read(p)
    if 'public static dk.bearware.TeamTalkBase activeClient()' in t:
        return
    idx = t.rfind('}')
    must(idx > 0, 'MainActivity class end missing')
    extra = '''
    private static MainActivity xrayCurrent;

    /** The live client of the visible TeamTalk activity (used by the share service). */
    public static dk.bearware.TeamTalkBase activeClient() {
        MainActivity a = xrayCurrent;
        return a != null ? a.getClient() : null;
    }
'''
    t = t[:idx] + extra + t[idx:]
    # register instance in onCreate
    anchor = '        super.onCreate(savedInstanceState);'
    must(anchor in t, 'MainActivity onCreate anchor missing')
    t = t.replace(anchor, anchor + '\n        xrayCurrent = this;', 1)
    write(p, t)
    print('OK MainActivity.activeClient()')


# --------------------------------------------------------------- 10. manifest
def step_manifest():
    p = OV + '/AndroidManifest.xml'
    must(os.path.exists(p), 'overlay manifest missing')
    m = read(p)
    m = re.sub(r'\s*<service\s+android:name="dk\.bearware\.gui\.XrayRecorderService".*?/>\s*', '\n    ', m,
               flags=re.S)
    if 'XrayDesktopShare$ShareService' not in m:
        idx = m.rfind('</application>')
        must(idx > 0, 'manifest application end missing')
        svc = ('        <service\n'
               '            android:name="dk.bearware.gui.XrayDesktopShare$ShareService"\n'
               '            android:exported="false"\n'
               '            android:foregroundServiceType="mediaProjection" />\n')
        m = m[:idx] + svc + m[idx:]
    if 'FOREGROUND_SERVICE_MEDIA_PROJECTION' not in m:
        anchor = '<uses-permission android:name="android.permission.FOREGROUND_SERVICE_MICROPHONE">'
        must(anchor in m, 'mic foreground permission missing')
        m = m.replace(anchor,
                      '<uses-permission android:name="android.permission.FOREGROUND_SERVICE_MEDIA_PROJECTION"></uses-permission>\n    ' + anchor, 1)
    write(p, m)
    print('OK manifest: share service')


def main():
    step_assets()
    step_styles()
    step_layouts()
    step_menu()
    step_strings()
    step_credits()
    step_java()
    step_mainactivity()
    step_active_client()
    step_hub()
    step_manifest()
    print('UI2 DONE')


if __name__ == '__main__':
    main()

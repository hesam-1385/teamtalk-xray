#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Turn real Lucide SVG icons into Android vector drawables for the Xray tiles."""
import os
import re
import math

SRC = '/root/.buddy/work/design/icons/lucide/icons'
DST = '/root/.buddy/work/teamtalk-xray/ci/overlay/Client/TeamTalkAndroid/src/main/res/drawable'

# tile icon name -> lucide icon file
ICONS = {
    'xray_ic_users': 'users',
    'xray_ic_settings': 'settings',
    'xray_ic_info': 'info',
    'xray_ic_move': 'move',
    'xray_ic_ban': 'ban',
    'xray_ic_bans': 'shield-ban',
}

COLOR = '#22D3EE'


def path_of(el):
    tag = el[0]
    a = dict(el[1])
    if tag == 'path':
        return a.get('d', '')
    if tag == 'line':
        return 'M%s,%sL%s,%s' % (a['x1'], a['y1'], a['x2'], a['y2'])
    if tag == 'circle':
        cx, cy, r = float(a['cx']), float(a['cy']), float(a['r'])
        return ('M%f,%fA%f,%f 0 1,0 %f,%fA%f,%f 0 1,0 %f,%fZ'
                % (cx - r, cy, r, r, cx + r, cy, r, r, cx - r, cy))
    if tag == 'ellipse':
        cx, cy = float(a['cx']), float(a['cy'])
        rx, ry = float(a['rx']), float(a['ry'])
        return ('M%f,%fA%f,%f 0 1,0 %f,%fA%f,%f 0 1,0 %f,%fZ'
                % (cx - rx, cy, rx, ry, cx + rx, cy, rx, ry, cx - rx, cy))
    if tag == 'rect':
        x, y = float(a['x']), float(a['y'])
        w, h = float(a['width']), float(a['height'])
        r = float(a.get('rx', 0))
        if r <= 0:
            return 'M%f,%fH%fV%fH%fZ' % (x, y, x + w, y + h, x)
        return ('M%f,%fH%fA%f,%f 0 0,1 %f,%fV%fA%f,%f 0 0,1 %f,%fH%f'
                'A%f,%f 0 0,1 %f,%fV%fA%f,%f 0 0,1 %f,%fZ'
                % (x + r, y, x + w - r, r, r, x + w, y + r, y + h - r,
                   r, r, x + w - r, y + h, x + r,
                   r, r, x, y + h - r, y + r,
                   r, r, x + r, y))
    if tag in ('polyline', 'polygon'):
        nums = [float(v) for v in re.split(r'[\s,]+', a['points'].strip()) if v]
        pts = list(zip(nums[0::2], nums[1::2]))
        if not pts:
            return ''
        d = 'M%f,%f' % pts[0] + ''.join('L%f,%f' % p for p in pts[1:])
        return d + ('Z' if tag == 'polygon' else '')
    return ''


def convert(name, out_name):
    svg = open(os.path.join(SRC, name + '.svg'), encoding='utf-8').read()
    els = re.findall(r'<(path|line|circle|ellipse|rect|polyline|polygon)\b([^>]*)>', svg)
    ds = []
    for tag, attrs in els:
        a = dict(re.findall(r'([a-zA-Z:-]+)\s*=\s*"([^"]*)"', attrs))
        d = path_of((tag, a))
        if d:
            ds.append(d)
    if not ds:
        print('  !! no geometry in', name)
        return False
    body = '\n'.join(
        '    <path android:pathData="%s" android:strokeColor="%s"'
        ' android:strokeWidth="1.8" android:strokeLineCap="round"'
        ' android:strokeLineJoin="round" android:fillColor="#00000000" />' % (d, COLOR)
        for d in ds)
    xml = ('<?xml version="1.0" encoding="utf-8"?>\n'
           '<vector xmlns:android="http://schemas.android.com/apk/res/android"\n'
           '    android:width="24dp" android:height="24dp"\n'
           '    android:viewportWidth="24" android:viewportHeight="24">\n'
           + body + '\n</vector>\n')
    open(os.path.join(DST, out_name + '.xml'), 'w', encoding='utf-8').write(xml)
    return True


ok = 0
for out_name, src in ICONS.items():
    if convert(src, out_name):
        ok += 1
print('icons written:', ok, '/', len(ICONS))

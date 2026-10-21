#!/usr/bin/env python3
# Static resource-reference checker for the Xray overlay.
# Cannot compile Java on the device (PaX), so this catches aapt2 errors
# (missing @string/@layout/@id/@color/@dimen/@drawable/@array/@menu) before CI.
import os, re, sys, collections
import xml.etree.ElementTree as ET

ROOT = '/root/.buddy/work/teamtalk-xray'
SRC = ROOT + '/src/Client/TeamTalkAndroid/src/main'
OV = ROOT + '/ci/overlay/Client/TeamTalkAndroid/src/main'

def read(p):
    with open(p, encoding='utf-8') as f: return f.read()

def collect(res_root):
    """returns dict type -> set(names)"""
    res = {'string': set(), 'layout': set(), 'id': set(), 'color': set(),
           'dimen': set(), 'drawable': set(), 'array': set(), 'menu': set(),
           'style': set(), 'plurals': set(), 'bool': set(), 'integer': set()}
    for dirpath, dirs, files in os.walk(res_root):
        for f in files:
            p = os.path.join(dirpath, f)
            rel = os.path.relpath(p, res_root)
            d = os.path.dirname(rel)
            if d.startswith('drawable') or d.startswith('mipmap'):
                res['drawable'].add(f.rsplit('.', 1)[0])
            if not f.endswith('.xml'):
                continue
            txt = read(p)
            if d == 'layout':
                res['layout'].add(f[:-4])
            if d == 'menu':
                res['menu'].add(f[:-4])
            for m in re.finditer(r'<(string|color|dimen|string-array|array|integer-array|plurals|style|bool|integer)\s+name="([^"]+)"', txt):
                tag, name = m.group(1), m.group(2)
                if tag == 'string': res['string'].add(name)
                elif tag == 'color': res['color'].add(name)
                elif tag == 'dimen': res['dimen'].add(name)
                elif tag in ('string-array', 'array'): res['array'].add(name)
                elif tag == 'integer-array': res['array'].add(name)
                elif tag == 'plurals': res['plurals'].add(name)
                elif tag == 'style': res['style'].add(name.replace('.', '_'))
                elif tag == 'bool': res['bool'].add(name)
                elif tag == 'integer': res['integer'].add(name)
            for m in re.finditer(r'@\+id/([A-Za-z0-9_]+)', txt):
                res['id'].add(m.group(1))
    return res

def merge(a, b):
    out = dict(a)
    for k, v in b.items():
        out[k] = out.get(k, set()) | v
    return out

def scan_java(path, res, problems):
    txt = read(path)
    for typ, name in re.findall(r'(?<!android\.)\bR\.([a-z]+)\.([A-Za-z0-9_]+)', txt):
        if typ in res:
            if name not in res[typ]:
                problems.append(('java', path, typ, name))
    # forbidden leftovers
    for bad in ['LocaleHelper', 'USERRIGHT_DEFAULT', 'TeamTalkApplication', 'CustomViewPager']:
        if bad in txt:
            problems.append(('java-leftover', path, bad, ''))

def scan_xml(path, res, problems):
    txt = read(path)
    for typ, name in re.findall(r'@(string|layout|id|color|dimen|drawable|array|menu|style|plurals|bool|integer)/([A-Za-z0-9_.]+)', txt):
        base = name.split('.')[0]
        if typ in res and base not in res[typ]:
            problems.append(('xml', path, typ, base))

def main():
    res = merge(collect(SRC + '/res'), collect(OV + '/res'))
    problems = []
    for dirpath, _, files in os.walk(OV):
        for f in files:
            p = os.path.join(dirpath, f)
            if f.endswith('.java'):
                scan_java(p, res, problems)
            elif f.endswith('.xml'):
                scan_xml(p, res, problems)
                # aapt2 rejects malformed xml (bad prolog, literal \n, unbalanced tags)
                try:
                    ET.parse(p)
                except Exception as e:
                    problems.append(('malformed', p, 'xml', str(e)[:60]))
    # overlay java may also reference upstream-only resources: already merged.
    # extra: check upstream app java references (for patched files) too
    for dirpath, _, files in os.walk(OV + '/java'):
        pass
    grouped = collections.defaultdict(list)
    for kind, path, typ, name in problems:
        grouped[(kind, typ, name)].append(os.path.basename(path))
    if not grouped:
        print('VERIFY OK - no missing resources')
        return 0
    print('PROBLEMS (%d):' % len(grouped))
    for (kind, typ, name), files in sorted(grouped.items()):
        print('  %-14s %-8s %-40s %s' % (kind, typ, name, ','.join(sorted(set(files))[:4])))
    return 1

if __name__ == '__main__':
    sys.exit(main())

# -*- coding: utf-8 -*-
"""Kiem ket qua S3. Chay: python -X utf8 -I verify_s3.py <thu_muc_test>"""
import glob
import json
import os
import sys
from collections import Counter

t = sys.argv[1]
fails = []


def check(cond, name, got=None):
    if cond:
        print('  dat  ' + name)
    else:
        print('  LOI  %s (thuc te: %r)' % (name, got))
        fails.append(name)


def load(n):
    return json.load(open(os.path.join(t, n), encoding='utf-8'))


def sig(scan):
    return sorted((i['handle'], i['raw'], i['style'], i['charset']) for i in scan['items'])


before, after = load('before.json'), load('after.json')
plan, plan2 = load('plan.json'), load('plan2.json')
undo, cancel, tamper = load('after_undo.json'), load('after_cancel.json'), load('after_tamper.json')

print('Ke hoach')
check(len(plan['items']) == 11, '11 muc se doi', len(plan['items']))
check(Counter(i['kind'] for i in plan['items']) == {'TEXT': 4, 'MTEXT': 1, 'ATTRIB': 2, 'ATTDEF': 1, 'MLEADER': 1, 'TABLE_CELL': 2}, 'theo loai', Counter(i['kind'] for i in plan['items']))
sk = plan['skipped']
check(sum(v for k, v in sk.items() if k.startswith('layer khoa')) == 1, 'bo qua 1 muc layer khoa', sk)
check(sum(v for k, v in sk.items() if k.startswith('dimension')) == 1, 'bo qua 1 DIMENSION', sk)
check(len(plan['planId']) == 12, 'co ma ke hoach', plan['planId'])
check(plan2['items'] == [], 'lap ke hoach lan 2 rong (idempotent)', len(plan2['items']))

print('Sau khi ap dung')
check(after['summary']['byCharset'] == {'Unicode': 14, 'Tcvn3': 1, 'Vni': 1, 'Ascii': 4}, 'bang ma: Unicode 14, con TCVN3 1 (khoa), VNI 1 (dim), ASCII 4', after['summary']['byCharset'])
conv = [i for i in after['items'] if i['style'] in ('Arial Unicode MS_2', 'uv-abc')]
check(len(conv) == 11, '11 muc dung style dich (9 TrueType -> Arial Unicode MS_2, 2 nguon SHX txt.shx -> uv-abc)', len(conv))
check(len([i for i in conv if i['style'] == 'uv-abc']) == 2 and len([i for i in conv if i['style'] == 'Arial Unicode MS_2']) == 9, 'font nguon SHX di uv-abc, TrueType di Arial Unicode MS_2', Counter(i['style'] for i in conv))
long_full = '{' + 'Đà Nẵng ' * 70 + '}'
want = Counter({'Đà Nẵng': 5, 'Việt Nam': 5, long_full[:400]: 1})  # JSON quet cat raw o 400 ky tu
got = Counter(i['raw'] for i in conv)
check(got == want, 'noi dung sau doi dung 100% (5x Da Nang, 5x Viet Nam, 1 MTEXT dai 400 ky tu dau)', {k[:20]: v for k, v in got.items()})
check(sorted(i['length'] for i in conv if i['kind'] == 'MTEXT') == [len(long_full)], 'MTEXT dai: do dai day du %d ky tu' % len(long_full), [i['length'] for i in conv if i['kind'] == 'MTEXT'])
check(after['meta']['errors'] == 0, 'quet sau khong loi', after['meta']['errors'])
styles = {s['name']: s for s in after['styles']}
check('Arial Unicode MS_2' in styles and styles['Arial Unicode MS_2']['typeFace'] == 'Arial Unicode MS', 'style dich theo ten font: Arial Unicode MS_2 (Arial Unicode MS) duoc tao vi ten Arial Unicode MS da co voi font khac', styles.get('Arial Unicode MS_2'))
check(styles.get('Arial Unicode MS', {}).get('typeFace') == 'Times New Roman', 'style Arial Unicode MS cu (font Times New Roman) khong bi dung hay doi', styles.get('Arial Unicode MS'))
check(not any(n.upper().startswith('PKTTC_') for n in styles), 'khong co style nao bat dau bang PKTTC_', sorted(styles))
check(plan['options']['targetStyle'] == 'Arial Unicode MS_2', 'ke hoach ghi ten style dich da giai (Arial Unicode MS_2)', plan['options']['targetStyle'])
# muc khong nam trong ke hoach phai khong doi
planned = {i['handle'] for i in plan['items']}
bmap = {i['handle']: (i['raw'], i['style']) for i in before['items']}
unchanged = [i for i in after['items'] if i['handle'] not in planned and bmap.get((i['handle'])) != (i['raw'], i['style'])]
check(not unchanged, 'muc ngoai ke hoach khong bi doi (ke ca layer khoa va DIMENSION)', unchanged[:2])

print('Hinh hoc va nhat ky')
logs = glob.glob(os.path.join(t, '_backup', '*', '*_apply.json'))
check(len(logs) >= 1, 'co nhat ky ap dung', logs)
if logs:
    log = json.load(open(sorted(logs)[0], encoding='utf-8'))
    check(log['ok'] == 11 and log['errors'] == 0, 'nhat ky: 11 ok, 0 loi', (log['ok'], log['errors']))
    texts = [r for r in log['results'] if r['kind'] in ('TEXT', 'ATTRIB', 'ATTDEF')]
    meas = [r for r in texts if r['measured']]
    print('   (do duoc %d / %d muc chu don; do lech lon nhat %.2f%%, bi chan %d)' % (len(meas), len(texts), log['maxDeviation'] * 100, log['clamped']))
    check(len(meas) >= 5, 'do duoc chieu rong it nhat 5/7 muc chu don', len(meas))
    check(all(r['deviation'] <= 0.02 or r['clamped'] for r in meas), 'lech chieu rong <= 2% (hoac bi chan o gioi han)', [r['deviation'] for r in meas])
bk = glob.glob(os.path.join(t, '_backup', '*', '*_truoc_PKTEXT.dwg'))
check(len(bk) == 2 and all(os.path.getsize(b) > 10000 for b in bk), 'dung 2 tep sao luu DWG (kich ban A va B; C va D khong tao)', [os.path.getsize(b) for b in bk])
lg = os.path.join(t, '_backup', '_log.md')
check(os.path.exists(lg) and plan['planId'] in open(lg, encoding='utf-8').read(), 'nhat ky _log.md co ma ke hoach')

print('UNDO, huy, ke hoach bi sua')
check(sig(undo) == sig(before), 'UNDO mot buoc tra ve y nguyen (tung muc: noi dung, style, bang ma)')
check(sig(cancel) == sig(before), 'go khong phai YES: ban ve khong doi')
check(sig(tamper) == sig(before), 'ke hoach bi sua tay bi tu choi: ban ve khong doi')
out_d = open(os.path.join(t, 'D.out.txt'), encoding='utf-16-le', errors='replace').read()
check('bi sua' in out_d, 'thong bao ke hoach bi sua')
check(not any('Arial Unicode MS_2' in i['style'] for i in undo['items']), 'sau UNDO khong con muc nao dung style dich')

print()
print('KET QUA: %s' % ('DAT' if not fails else 'CO LOI (%d)' % len(fails)))
sys.exit(0 if not fails else 1)

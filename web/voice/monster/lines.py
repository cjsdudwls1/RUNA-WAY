"""괴물런 대사 후보(lines.txt) 읽기. 검수 페이지, 녹음 대본, 굽기가 같이 쓴다

  python3 web/voice/monster/lines.py        # 역할별 후보 수, 추천 수, 긴 대사
"""
import os, re

HERE = os.path.dirname(os.path.abspath(__file__))


def parse(path=os.path.join(HERE, 'lines.txt')):
    roles, role, sit = [], None, None
    for n, raw in enumerate(open(path, encoding='utf-8'), 1):
        line = raw.rstrip('\n')
        if line.startswith('# role '):
            rid, name, mode, who, note = [x.strip() for x in line[len('# role '):].split('|')]
            role = {'id': rid, 'name': name, 'mode': mode, 'who': who, 'note': note, 'sits': []}
            roles.append(role); sit = None
        elif line.startswith('## '):
            sid, name, cond, want, d = [x.strip() for x in line[3:].split('|')]
            sit = {'id': sid, 'name': name, 'cond': cond, 'want': int(want), 'dir': d, 'cands': []}
            role['sits'].append(sit)
        elif line.startswith('- '):
            text, _, d = line[2:].partition(' // ')
            i = len(sit['cands']) + 1
            sit['cands'].append({'id': f"{role['id']}.{sit['id']}.{i:02d}", 'text': text.strip(), 'dir': d.strip(), 'rec': i <= sit['want']})
        elif line.strip() and not line.startswith('#'):
            raise ValueError(f'{path}:{n} 알 수 없는 줄: {line}')
    for r in roles:
        for s in r['sits']:
            if s['want'] > len(s['cands']): raise ValueError(f"{r['id']}.{s['id']}: 고를 수 {s['want']} > 후보 {len(s['cands'])}")
    return roles


def syllables(t):
    return len(re.findall(r'[가-힣]', t))


if __name__ == '__main__':
    R = parse()
    tc = tw = 0
    for r in R:
        c = sum(len(s['cands']) for s in r['sits']); w = sum(s['want'] for s in r['sits'])
        tc += c; tw += w
        print(f"{r['name']:8s} {r['mode']} 녹음 {r['who']:4s} 상황 {len(r['sits']):2d} 후보 {c:3d} 고를 수 {w:3d}")
    print(f'합계 후보 {tc}, 고를 수 {tw}')
    long = [(syllables(c['text']), c['id'], c['text']) for r in R for s in r['sits'] for c in s['cands'] if syllables(c['text']) > 26]
    print(f'27음절 넘는 대사(약 4초 넘음) {len(long)}개')
    for x in sorted(long, reverse=True): print(' ', *x)

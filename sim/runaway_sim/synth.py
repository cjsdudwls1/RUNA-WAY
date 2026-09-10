"""합성 GPX 생성. 실주행이 없을 때 파이프라인·판정을 검증하기 위한 입력."""
import math
import random
from datetime import datetime, timedelta, timezone
from .geo import offset

LAT0, LON0 = 37.894, 127.200   # 포천 인근 임의 기준점


def loop_point(s_m, loop_len_m):
    """둘레 loop_len의 원형 코스 위 호길이 s에 해당하는 (north, east) m."""
    r = loop_len_m / (2 * math.pi)
    th = (s_m / loop_len_m) * 2 * math.pi
    return r * math.sin(th), r * (1 - math.cos(th))


def pace_steady(kmh):
    return lambda t: kmh / 3.6


def pace_intervals(base_kmh, fast_kmh, work_s=60, rest_s=120):
    def f(t):
        return (fast_kmh if (t % (work_s + rest_s)) < work_s else base_kmh) / 3.6
    return f


def generate(course_m=5000, pace=None, seed=1, noise_m=4.0, canyon=True, dropout=True, stop=True):
    """1Hz 합성 점 [(t, lat, lon, acc)]와 정답 누적거리 반환."""
    rng = random.Random(seed)
    pace = pace or pace_steady(10.0)
    pts, truth = [], []
    s = 0.0
    t = 0
    stop_at = course_m * 0.30 if stop else None
    stopped_until = -1
    drop_from = course_m * 0.40 if dropout else None
    RHO = 0.95                       # GPS 잡음은 자기상관. AR(1)
    nn, ne = 0.0, 0.0
    while s < course_m:
        v = pace(t)
        if stop_at is not None and s >= stop_at and stopped_until < 0:
            stopped_until = t + 45
            stop_at = None
        if t < stopped_until:
            v = 0.0
        s += v
        n, e = loop_point(s, course_m)
        acc = 6.0 + rng.random() * 4
        sigma = noise_m
        if canyon and (t // 420) % 2 == 1 and (t % 420) < 30:
            acc = 35 + rng.random() * 25
            sigma = 15.0
        k = sigma * math.sqrt(1 - RHO * RHO)
        nn = RHO * nn + rng.gauss(0, k)
        ne = RHO * ne + rng.gauss(0, k)
        lat, lon = offset(LAT0, LON0, n + nn, e + ne)
        if drop_from is not None and drop_from <= s < drop_from + 200:
            pass  # 점 자체를 기록하지 않음 → 파서가 dropout 처리
        else:
            pts.append((t, lat, lon, acc))
        truth.append((t, s))
        t += 1
    return pts, truth


def write_gpx(path, pts, name='synthetic'):
    t0 = datetime(2026, 9, 10, 6, 0, 0, tzinfo=timezone.utc)
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<gpx version="1.1" creator="runaway-sim" xmlns="http://www.topografix.com/GPX/1/1">',
             f'<trk><name>{name}</name><trkseg>']
    for (t, lat, lon, acc) in pts:
        ts = (t0 + timedelta(seconds=t)).strftime('%Y-%m-%dT%H:%M:%SZ')
        lines.append(f'<trkpt lat="{lat:.7f}" lon="{lon:.7f}"><time>{ts}</time>'
                     f'<extensions><accuracy>{acc:.1f}</accuracy></extensions></trkpt>')
    lines += ['</trkseg></trk>', '</gpx>']
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

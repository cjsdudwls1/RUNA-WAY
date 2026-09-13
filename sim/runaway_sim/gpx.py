"""GPX 파싱 → 1Hz 트랙. 입력 단계라 float 사용. 코어로 넘길 때 cm 정수로 변환."""
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from .geo import haversine_m

GATE_ACC_M = 30.0      # 이 값 초과 정확도는 폐기(직전 위치 유지)
GATE_SPEED_MS = 8.0    # 8 m/s 초과 이동은 폐기
DROPOUT_S = 20         # 이 시간 이상 점이 없으면 신호 소실로 처리


def _parse_time(s):
    s = s.strip().replace('Z', '+00:00')
    return datetime.fromisoformat(s).astimezone(timezone.utc)


def parse_gpx(path):
    """[(t_s, lat, lon, acc_m)] 원본 점. acc는 extensions의 accuracy 또는 hdop*5, 없으면 8."""
    tree = ET.parse(path)
    pts = []
    for el in tree.iter():
        if el.tag.endswith('trkpt'):
            lat, lon = float(el.get('lat')), float(el.get('lon'))
            t = None
            acc = None
            for c in el.iter():
                tag = c.tag.split('}')[-1]
                if tag == 'time' and c.text:
                    t = _parse_time(c.text)
                elif tag == 'accuracy' and c.text:
                    acc = float(c.text)
                elif tag == 'hdop' and c.text and acc is None:
                    acc = float(c.text) * 5.0
            if t is None:
                continue
            pts.append((t, lat, lon, 8.0 if acc is None else acc))
    if not pts:
        raise ValueError('trkpt 없음: ' + path)
    t0 = pts[0][0]
    return [((p[0] - t0).total_seconds(), p[1], p[2], p[3]) for p in pts]


def resample_1hz(raw):
    """선형 보간으로 1Hz. 20초 이상 공백은 dropout: 위치 유지, acc 99."""
    out = []
    i = 0
    t_end = int(raw[-1][0])
    for t in range(0, t_end + 1):
        while i + 1 < len(raw) and raw[i + 1][0] <= t:
            i += 1
        a = raw[i]
        if i + 1 < len(raw):
            b = raw[i + 1]
            if b[0] - a[0] > DROPOUT_S and t > a[0]:
                out.append((t, a[1], a[2], 99.0))
                continue
            f = 0.0 if b[0] == a[0] else (t - a[0]) / (b[0] - a[0])
            f = max(0.0, min(1.0, f))
            out.append((t, a[1] + (b[1] - a[1]) * f, a[2] + (b[2] - a[2]) * f, a[3] + (b[3] - a[3]) * f))
        else:
            out.append((t, a[1], a[2], a[3]))
    return out


SMOOTH_ALPHA = 0.35    # EMA. 백색 잡음 억제
JUMP_RESET_N = 3       # 연속 3회 점프면 새 앵커로 인정(실제 순간이동 복구)


def to_track(pts_1hz):
    """스무딩 + 게이트 필터 후 [(t, dist_cm 누적, speed_cms, acc_m)]. 코어 입력 형식."""
    track = []
    dist = 0.0
    slat = slon = plat = plon = float('nan')
    ignored = 0
    for (t, lat, lon, acc) in pts_1hz:
        if acc > GATE_ACC_M:
            track.append((t, int(round(dist * 100)), 0, acc))
            continue                      # 저정확도: 위치·거리 유지
        if slat != slat:                  # 게이트를 통과한 첫 점만 평활화 시드
            slat, slon = lat, lon
            plat, plon = lat, lon
        slat = SMOOTH_ALPHA * lat + (1 - SMOOTH_ALPHA) * slat
        slon = SMOOTH_ALPHA * lon + (1 - SMOOTH_ALPHA) * slon
        step = haversine_m(plat, plon, slat, slon)
        if step > GATE_SPEED_MS:
            ignored += 1
            if ignored >= JUMP_RESET_N:
                plat, plon = slat, slon   # 앵커 리셋, 거리는 더하지 않음
                ignored = 0
            step = 0.0
        else:
            ignored = 0
            plat, plon = slat, slon
        dist += step
        track.append((t, int(round(dist * 100)), int(round(step * 100)), acc))
    return track


def load_track(path):
    return to_track(resample_1hz(parse_gpx(path)))

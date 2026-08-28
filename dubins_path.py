import numpy as np


def _mod2pi(theta):
    return theta % (2 * np.pi)


def _normalize(p1, p2, R):
    x1, y1, theta1 = p1
    x2, y2, theta2 = p2
    dx, dy = x2 - x1, y2 - y1
    d = np.hypot(dx, dy) / R
    theta = np.arctan2(dy, dx)
    alpha = _mod2pi(theta1 - theta)
    beta = _mod2pi(theta2 - theta)
    return alpha, beta, d


def lsl(alpha, beta, d):
    sa, sb = np.sin(alpha), np.sin(beta)
    ca, cb = np.cos(alpha), np.cos(beta)
    c_ab = np.cos(alpha - beta)
    tmp = d + sa - sb
    p_sq = 2 + d**2 - 2 * c_ab + 2 * d * (sa - sb)
    if p_sq < 0:
        return None
    p = np.sqrt(p_sq)
    t = _mod2pi(-alpha + np.arctan2(cb - ca, tmp))
    q = _mod2pi(beta - np.arctan2(cb - ca, tmp))
    return t, p, q


def rsr(alpha, beta, d):
    sa, sb = np.sin(alpha), np.sin(beta)
    ca, cb = np.cos(alpha), np.cos(beta)
    c_ab = np.cos(alpha - beta)
    tmp = d - sa + sb
    p_sq = 2 + d**2 - 2 * c_ab + 2 * d * (sb - sa)
    if p_sq < 0:
        return None
    p = np.sqrt(p_sq)
    t = _mod2pi(alpha - np.arctan2(ca - cb, tmp))
    q = _mod2pi(-beta + np.arctan2(ca - cb, tmp))
    return t, p, q


def lsr(alpha, beta, d):
    sa, sb = np.sin(alpha), np.sin(beta)
    ca, cb = np.cos(alpha), np.cos(beta)
    c_ab = np.cos(alpha - beta)
    p_sq = -2 + d**2 + 2 * c_ab + 2 * d * (sa + sb)
    if p_sq < 0:
        return None
    p = np.sqrt(p_sq)
    tmp = np.arctan2(-ca - cb, d + sa + sb) - np.arctan2(-2, p)
    t = _mod2pi(-alpha + tmp)
    q = _mod2pi(-_mod2pi(beta) + tmp)
    return t, p, q


def rsl(alpha, beta, d):
    sa, sb = np.sin(alpha), np.sin(beta)
    ca, cb = np.cos(alpha), np.cos(beta)
    c_ab = np.cos(alpha - beta)
    p_sq = d**2 - 2 + 2 * c_ab - 2 * d * (sa + sb)
    if p_sq < 0:
        return None
    p = np.sqrt(p_sq)
    tmp = np.arctan2(ca + cb, d - sa - sb) - np.arctan2(2, p)
    t = _mod2pi(alpha - tmp)
    q = _mod2pi(beta - tmp)
    return t, p, q


def rlr(alpha, beta, d):
    sa, sb = np.sin(alpha), np.sin(beta)
    ca, cb = np.cos(alpha), np.cos(beta)
    c_ab = np.cos(alpha - beta)
    tmp = (6 - d**2 + 2 * c_ab + 2 * d * (sa - sb)) / 8
    if abs(tmp) > 1:
        return None
    p = _mod2pi(2 * np.pi - np.arccos(tmp))
    t = _mod2pi(alpha - np.arctan2(ca - cb, d - sa + sb) + p / 2)
    q = _mod2pi(alpha - beta - t + p)
    return t, p, q


def lrl(alpha, beta, d):
    sa, sb = np.sin(alpha), np.sin(beta)
    ca, cb = np.cos(alpha), np.cos(beta)
    c_ab = np.cos(alpha - beta)
    tmp = (6 - d**2 + 2 * c_ab + 2 * d * (sb - sa)) / 8
    if abs(tmp) > 1:
        return None
    p = _mod2pi(2 * np.pi - np.arccos(tmp))
    t = _mod2pi(-alpha + np.arctan2(-ca + cb, d + sa - sb) + p / 2)
    q = _mod2pi(beta - alpha - t + p)
    return t, p, q


_WORD_FUNCS = {"LSL": lsl, "RSR": rsr, "LSR": lsr, "RSL": rsl, "RLR": rlr, "LRL": lrl}


def dubins_path(p1, p2, R, word_types=None):
    if word_types is None:
        word_types = list(_WORD_FUNCS.keys())
    alpha, beta, d = _normalize(p1, p2, R)
    best = None
    for word in word_types:
        result = _WORD_FUNCS[word](alpha, beta, d)
        if result is None:
            continue
        t, p, q = result
        length = (t + p + q) * R
        if best is None or length < best["length"]:
            best = {"word": word, "length": length, "segments": (t, p, q)}
    return best


def sample_dubins_path(p1, p2, R, step=0.5, word_types=None):
    path_info = dubins_path(p1, p2, R, word_types=word_types)
    if path_info is None:
        return None, None

    word = path_info["word"]
    t, p, q = path_info["segments"]
    x0, y0, theta0 = p1

    points = [np.array([x0, y0, theta0])]
    x, y, theta = x0, y0, theta0

    for letter, val in zip(word, (t, p, q)):
        if letter in ("L", "R"):
            arc_len = val * R
            n_steps = max(1, int(np.ceil(arc_len / step)))
            dtheta_total = val if letter == "L" else -val
            sign = 1 if letter == "L" else -1
            for i in range(1, n_steps + 1):
                frac = i / n_steps
                dtheta = dtheta_total * frac
                th = theta + dtheta
                cx = x - sign * R * np.sin(theta)
                cy = y + sign * R * np.cos(theta)
                nx = cx + sign * R * np.sin(th)
                ny = cy - sign * R * np.cos(th)
                points.append(np.array([nx, ny, _mod2pi(th)]))
            theta = _mod2pi(theta + dtheta_total)
            x, y = points[-1][0], points[-1][1]
        else:
            seg_len = val * R
            n_steps = max(1, int(np.ceil(seg_len / step)))
            for i in range(1, n_steps + 1):
                frac = i / n_steps
                nx = x + seg_len * frac * np.cos(theta)
                ny = y + seg_len * frac * np.sin(theta)
                points.append(np.array([nx, ny, theta]))
            x, y = points[-1][0], points[-1][1]

    return np.array(points), path_info
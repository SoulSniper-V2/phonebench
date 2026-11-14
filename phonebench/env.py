"""Environment: start-state resets, the generic action space, and observation formatting."""
import re
import time

from . import device as d
from .safety import blocked
from .tasks import APPS

FIELD_ROLES = ('textbox', 'searchbox', 'text_field', 'search_field', 'text_view', 'secure_text_field')
TAPPABLE_ROLES = ('button', 'link', 'cell', 'tab', 'image', 'menu_item', 'static_text', 'text') + FIELD_ROLES


def label_of(e):
    return (e.get('label') or e.get('value') or '').strip()


def visible(e):
    b = e.get('bounds') or {}
    return b.get('h', 0) > 2 and b.get('w', 0) > 2 and b.get('y', 0) + b.get('h', 0) > 40 and b.get('y', 0) < 870


def has(s, *words):
    t = s.get('text', '').lower()
    return all(w.lower() in t for w in words)


# ---------------------------------------------------------------- resets
# phonedriver cannot force-quit apps on a physical iPhone, so every reset navigates the app back to a
# verified root view (navigation only, nothing is changed) and then returns to the Home screen.
def _tap(s, labels, ymin=0, ymax=900):
    for lab in labels:
        for e in d.elements(s):
            if label_of(e) == lab and visible(e) and ymin <= (e.get('bounds') or {}).get('y', 0) <= ymax:
                d.tap_element(e)
                return True
    return False


def _tab_selected(s, labels, ymin=740):
    return any(label_of(e) in labels and (e.get('bounds') or {}).get('y', 0) > ymin and 'SELECTED' in (e.get('state') or '') for e in d.elements(s))


ROOTS = {
    APPS['School portal']: dict(marker=lambda s: has(s, 'student profile | home'), steps=[('tap', ['Menu']), ('tap', ['Home'])]),
    APPS['YouTube']: dict(marker=lambda s: any(label_of(e) == 'Home' and 'SELECTED' in (e.get('state') or '') for e in d.elements(s)) and not has(s, 'collapse video'),
                          steps=[('tap', ['Pause video', 'Pause']), ('tap', ['Collapse video']), ('tap', ['Close miniplayer', 'Close', 'Cancel', 'Back']), ('tab', ['Home'])]),
    APPS['X']: dict(marker=lambda s: _tab_selected(s, ('Home', 'Home tab')), steps=[('tap', ['Cancel', 'Back', 'Navigate up']), ('tab', ['Home', 'Home tab'])]),
    APPS['Reddit']: dict(marker=lambda s: _tab_selected(s, ('Home',)), steps=[('tap', ['Cancel', 'Back', 'Close']), ('tab', ['Home'])]),
    APPS['App Store']: dict(marker=lambda s: any(label_of(e) == 'Today' and 'SELECTED' in (e.get('state') or '') for e in d.elements(s)), steps=[('tap', ['Cancel', 'Back']), ('tab', ['Search']), ('tap', ['Clear text', 'Cancel']), ('tab', ['Today'])]),
    APPS['Google Maps']: dict(marker=lambda s: any(label_of(e) in ('Explore', 'Explore tab') and 'SELECTED' in (e.get('state') or '') for e in d.elements(s)),
                              steps=[('tap', ['Close', 'Back', 'Cancel', 'Clear search']), ('tab', ['Explore', 'Explore tab'])]),
    APPS['Maps']: dict(marker=lambda s: not any(label_of(e) in ('Close', 'End', 'Clear') and visible(e) for e in d.elements(s)), steps=[('tap', ['Close', 'End', 'Clear', 'Cancel'])]),
    APPS['Calculator']: dict(marker=lambda s: True, steps=[('tap', ['All Clear', 'Clear'])]),
}
GENERIC_BACK = ['Cancel', 'Close', 'Done', 'Back']


def _canon(s):
    return re.sub(r'@?e\d+', '', s.get('text', ''))


def reset_app(app):
    if app == APPS['Safari']:
        d.driver('open', 'https://example.com', settle=True, timeout=65)
        return 'safari: example.com'
    d.launch_verified(app)
    time.sleep(1.0)
    root = ROOTS.get(app)
    s = d.snapshot()
    for _ in range(8):
        if root is None:
            if not _tap(s, GENERIC_BACK, ymax=140):
                d.back_gesture()
                s2 = d.snapshot()
                if _canon(s2) == _canon(s):
                    return f'{app}: backed out'
                s = s2
            else:
                s = d.snapshot()
            continue
        for kind, labels in root['steps']:
            if (_tap(s, labels) if kind == 'tap' else _tap(s, labels, ymin=740)):
                time.sleep(0.6)
                s = d.snapshot()
        if root['marker'](s):
            return f'{app}: root verified'
        d.back_gesture()
        s = d.snapshot()
    if root and not root['marker'](s):
        raise RuntimeError(f'RESET_FAILED: root view of {app} not verified')
    return f'{app}: backed out (limit)'


def reset(task):
    events = []
    for app in task['apps']:
        try:
            events.append(reset_app(app))
        except RuntimeError as e:
            if 'timed out' not in str(e):
                raise
            d.driver('press', 'home', timeout=40)
            events.append('retry: ' + reset_app(app))
    d.driver('press', 'home', settle=True)
    time.sleep(0.6)
    return events


# ---------------------------------------------------------------- action space (identical for every task)
def candidates(s, task):
    out, seen = {}, {}
    for e in d.elements(s):
        lab, role = label_of(e), e.get('role') or ''
        if not lab or not visible(e) or 'DISABLED' in (e.get('state') or ''):
            continue
        if role == 'switch' or not ('TAP' in (e.get('actions') or '') or role in TAPPABLE_ROLES) or blocked(lab):
            continue
        key = (role, lab[:60])
        seen[key] = seen.get(key, 0) + 1
        if seen[key] > 2:
            continue
        val = e.get('value')
        desc = f'Tap {role} "{lab[:90]}"' + (f' (value: {str(val)[:40]})' if val and val != lab else '') + f' at {d.center(e)}'
        out['tap_' + e['ref']] = {'kind': 'tap', 'point': d.center(e), 'label': lab[:90], 'description': desc}
        if role in FIELD_ROLES:
            for i, t in enumerate(task['params']):
                out[f'type_{e["ref"]}_{i}'] = {'kind': 'type', 'target': e['ref'], 'text': t, 'description': f'Type "{t}" into {role} "{lab[:50]}" (replaces its text)'}
    if (s.get('header') or {}).get('keyboard'):
        for i, t in enumerate(task['params']):
            out[f'type_focused_{i}'] = {'kind': 'type_focused', 'text': t, 'description': f'Type "{t}" into the focused text field'}
        out['enter'] = {'kind': 'enter', 'description': 'Press Return / Search / Go on the keyboard'}
    out['scroll_down'] = {'kind': 'scroll', 'direction': 'down', 'description': 'Scroll down to reveal more content'}
    out['scroll_up'] = {'kind': 'scroll', 'direction': 'up', 'description': 'Scroll up'}
    out['back'] = {'kind': 'back', 'description': 'Go back (swipe from the left edge)'}
    out['home'] = {'kind': 'home', 'description': 'Go to the Home screen'}
    cur = d.app_of(s)
    for name, bid in APPS.items():
        if bid != cur:
            out['open_' + re.sub(r'\W+', '_', name.lower())] = {'kind': 'launch', 'app': bid, 'description': f'Open the {name} app'}
    out['wait'] = {'kind': 'wait', 'description': 'Wait 1.5 seconds for content to load'}
    out['finish'] = {'kind': 'finish', 'description': 'FINISH: the goal is fully accomplished and the result is on screen now'}
    out['infeasible'] = {'kind': 'infeasible', 'description': 'INFEASIBLE: this goal cannot be accomplished on this phone (missing app or feature)'}
    return out


def execute(a):
    k = a['kind']
    if k == 'tap':
        return d.driver('tap', a['point'], settle=True)
    if k == 'type':
        return d.driver('type', a['text'], '--into', '@' + a['target'], settle=True)
    if k == 'type_focused':
        return d.driver('type', a['text'], settle=True)
    if k == 'enter':
        return d.driver('press', 'enter', settle=True)
    if k == 'scroll':
        return d.driver('scroll', a['direction'], settle=True)
    if k == 'back':
        return d.back_gesture()
    if k == 'home':
        return d.driver('press', 'home', settle=True)
    if k == 'launch':
        return d.launch_verified(a['app'])
    if k == 'wait':
        time.sleep(1.5)
        return 'waited'
    raise ValueError(k)


def screen_digest(s, limit=9000):
    lines = []
    for e in d.elements(s):
        lab = label_of(e)
        if lab and visible(e):
            v = e.get('value')
            lines.append(f'@{e["ref"]} {e.get("role")} "{lab[:100]}"' + (f' = {str(v)[:60]}' if v and v != lab else ''))
    return '\n'.join(lines)[:limit]

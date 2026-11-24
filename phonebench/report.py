"""Aggregate a release's trials.jsonl into summary.json (for the site) and RESULTS.md.

    python -m phonebench.report results/v0.7
"""
import collections
import json
import math
from pathlib import Path
import statistics
import sys

ORDER = ['jev-1.14', 'jev-1.13', 'gemini-decision-1', 'clef-flash', 'clef', 'clef-omni', 'strands-2b']
LABEL = {'jev-1.14': 'Jev 1.14', 'jev-1.13': 'Jev 1.13', 'gemini-decision-1': 'Gemini Decision 1',
         'clef-flash': 'Clef Flash', 'clef': 'Clef', 'clef-omni': 'Clef Omni', 'strands-2b': 'Strands Decider 2B (local)'}
MODES = ['pass', 'false_finish', 'wrong_answer', 'reached_no_finish', 'stuck_loop', 'timeout', 'false_infeasible',
         'missed_infeasible', 'wandered_infeasible', 'invalid_choice']


def wilson(k, n, z=1.96):
    if not n:
        return (0.0, 0.0)
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (max(0.0, c - h), min(1.0, c + h))


def q(xs, f):
    xs = sorted(x for x in xs if x is not None)
    if not xs:
        return None
    i = (len(xs) - 1) * f
    lo, hi = math.floor(i), math.ceil(i)
    return round(xs[lo] + (xs[hi] - xs[lo]) * (i - lo), 3)


def load(release):
    rows = [json.loads(l) for l in open(Path(release) / 'trials.jsonl')]
    scored = [r for r in rows if r['status'] == 'finished' and 'excluded_reason' not in r and r.get('obs_mode', 'tree+image') == 'tree+image' and r.get('device_kind', 'phone') == 'phone' and r.get('track') != 'judged']
    return rows, scored


def summarize(release):
    rows, scored = load(release)
    by = collections.defaultdict(list)
    for r in scored:
        by[r['provider']].append(r)
    providers = [p for p in ORDER if p in by] + sorted(p for p in by if p not in ORDER)
    tasks = sorted({r['task'] for r in scored})
    # Headline = mean over tasks of per-task pass rate, so tasks with more repeats don't dominate.
    models = []
    for p in providers:
        rs = by[p]
        per_task = collections.defaultdict(list)
        for r in rs:
            per_task[r['task']].append(r['success'])
        task_rate = statistics.mean(sum(v) / len(v) for v in per_task.values())
        k, n = sum(r['success'] for r in rs), len(rs)
        passes = [r for r in rs if r['success']]
        calls = [ms for r in rs for ms in r.get('model_ms_per_call', [])]
        feas = [r for r in rs if not r['infeasible']]
        modes = collections.Counter(r['failure_mode'] for r in rs)
        tot = sum(r['task_s'] for r in rs) or 1
        models.append({
            'id': p, 'label': LABEL.get(p, p), 'trials': n, 'passes': k, 'pass_rate': k / n, 'ci95': wilson(k, n),
            'task_macro_pass_rate': task_rate, 'tasks_covered': len(per_task),
            'median_task_s_pass': q([r['task_s'] for r in passes], .5), 'median_task_s': q([r['task_s'] for r in rs], .5),
            'median_actions_pass': q([r['n_actions'] for r in passes], .5),
            'decision_ms_p50': q(calls, .5), 'decision_ms_p90': q(calls, .9), 'decision_ms_p99': q(calls, .99),
            'median_input_tokens': q([r['input_tokens'] for r in rs], .5), 'median_output_tokens': q([r['output_tokens'] for r in rs], .5),
            'time_split': {'model': sum(r['model_s'] for r in rs) / tot, 'device': sum(r['action_s'] + r['observe_s'] for r in rs) / tot},
            'false_finish_rate': modes['false_finish'] / max(1, len(feas)),
            'failure_modes': {m: modes[m] for m in MODES if modes[m]},
            'by_category': {c: [sum(r['success'] for r in rs if r['category'] == c), sum(1 for r in rs if r['category'] == c)] for c in sorted({r['category'] for r in rs})},
            'by_difficulty': {c: [sum(r['success'] for r in rs if r['difficulty'] == c), sum(1 for r in rs if r['difficulty'] == c)] for c in ('easy', 'medium', 'hard')},
        })
    models.sort(key=lambda m: -m['task_macro_pass_rate'])
    matrix = {t: {p: [[r['success'], r['task_s'], r['n_actions'], r['failure_mode']] for r in by[p] if r['task'] == t] for p in providers} for t in tasks}
    meta = {t: next({'category': r['category'], 'difficulty': r['difficulty'], 'infeasible': r['infeasible']} for r in scored if r['task'] == t) for t in tasks}
    ablation = {}
    for r in rows:
        if r['status'] == 'finished' and 'excluded_reason' not in r:
            key = (r['provider'], r.get('obs_mode', 'tree+image'))
            ablation.setdefault(key, []).append(r['success'])
    excluded = collections.Counter((r.get('excluded_reason') or r['status'])[:60] for r in rows if r['status'] != 'finished' or 'excluded_reason' in r)
    return {'release': Path(release).name, 'n_trials': len(rows), 'n_scored': len(scored), 'n_tasks': len(tasks), 'models': models,
            'matrix': matrix, 'task_meta': meta, 'excluded': dict(excluded),
            'ablation': {f'{p}|{m}': [sum(v), len(v)] for (p, m), v in sorted(ablation.items())},
            'dates': sorted({r['trial'][:8] for r in rows})}


def markdown(S):
    pct = lambda x: f'{x * 100:.0f}%'
    o = [f"# PhoneBench results — {S['release']}", '',
         f"{S['n_scored']} scored trials on a physical iPhone, {S['n_tasks']} tasks, {len(S['models'])} decision models. "
         f"{S['n_trials'] - S['n_scored']} trials excluded for harness reasons (listed at the end), never counted as model failures.", '',
         '| Rank | Model | Score (task-macro) | Pass / trials | 95% CI | Median time to pass | Median actions to pass | Decision p50 / p90 | Input tokens / task | Model share of time | False finish rate |',
         '|---|---|---|---|---|---|---|---|---|---|---|']
    for i, m in enumerate(S['models'], 1):
        o.append(f"| {i} | {m['label']} | **{pct(m['task_macro_pass_rate'])}** | {m['passes']}/{m['trials']} | {pct(m['ci95'][0])}–{pct(m['ci95'][1])} | "
                 f"{m['median_task_s_pass']} s | {m['median_actions_pass']} | {m['decision_ms_p50']:.0f} / {m['decision_ms_p90']:.0f} ms | {m['median_input_tokens']:,.0f} | "
                 f"{pct(m['time_split']['model'])} | {pct(m['false_finish_rate'])} |")
    o += ['', '## By difficulty', '', '| Model | ' + ' | '.join(['easy', 'medium', 'hard']) + ' |', '|---|---|---|---|']
    for m in S['models']:
        o.append(f"| {m['label']} | " + ' | '.join(f"{a}/{b}" if b else '–' for a, b in (m['by_difficulty'][d] for d in ('easy', 'medium', 'hard'))) + ' |')
    cats = sorted({c for m in S['models'] for c in m['by_category']})
    o += ['', '## By category', '', '| Model | ' + ' | '.join(cats) + ' |', '|---|' + '---|' * len(cats)]
    for m in S['models']:
        o.append(f"| {m['label']} | " + ' | '.join(f"{m['by_category'][c][0]}/{m['by_category'][c][1]}" if c in m['by_category'] else '–' for c in cats) + ' |')
    o += ['', '## Failure modes', '', '| Model | ' + ' | '.join(MODES[1:]) + ' |', '|---|' + '---|' * (len(MODES) - 1)]
    for m in S['models']:
        o.append(f"| {m['label']} | " + ' | '.join(str(m['failure_modes'].get(x, 0)) for x in MODES[1:]) + ' |')
    o += ['', '## Every task', '', '✅ pass · ❌ fail, with seconds and actions per trial.', '',
          '| Task | Category | Difficulty | ' + ' | '.join(m['label'] for m in S['models']) + ' |', '|---|---|---|' + '---|' * len(S['models'])]
    for t, cells in S['matrix'].items():
        meta = S['task_meta'][t]
        row = []
        for m in S['models']:
            trials = cells.get(m['id'], [])
            row.append(' '.join(('✅' if ok else '❌') + f'{s:.0f}s/{a}' for ok, s, a, _ in trials) or '–')
        o.append(f"| `{t}` | {meta['category']} | {meta['difficulty']} | " + ' | '.join(row) + ' |')
    if S['ablation']:
        o += ['', '## Observation ablation', '', '| Model | Observation | Pass / trials |', '|---|---|---|']
        for k, (a, b) in S['ablation'].items():
            p, mode = k.split('|')
            o.append(f"| {LABEL.get(p, p)} | {mode} | {a}/{b} |")
    o += ['', '## Excluded trials', ''] + [f'- {v} × {k}' for k, v in sorted(S['excluded'].items(), key=lambda kv: -kv[1])]
    return '\n'.join(o) + '\n'


def main():
    release = Path(sys.argv[1] if len(sys.argv) > 1 else 'results/latest')
    S = summarize(release)
    (release / 'summary.json').write_text(json.dumps(S, indent=1, default=list) + '\n')
    (release / 'RESULTS.md').write_text(markdown(S))
    print(markdown(S)[:3000])


if __name__ == '__main__':
    main()

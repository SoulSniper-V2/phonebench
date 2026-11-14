"""Re-grade raw runs offline from their saved snapshots and export privacy-safe records.

    python -m phonebench.regrade RAW_DIR [RAW_DIR ...] --release results/2026-11-14

Grading is a pure function of the saved accessibility snapshots, so a fixed check can be re-applied
to every past trial. Raw runs (screenshots, screen text) never leave the machine; the export keeps only
ids, outcomes, counts and timings.
"""
import argparse
import glob
import json
from pathlib import Path

from .providers import usage_tokens
from .tasks import LEGACY_IDS, build, load_private

LEGACY_PROVIDERS = {'jev': 'jev-1.14', 'jev-1.13.0': 'jev-1.13', 'gemini': 'gemini-decision-1'}


def failure_mode(r):
    if r['success']:
        return 'pass'
    st = r.get('stop_reason')
    if r.get('infeasible'):
        return 'missed_infeasible' if st == 'model_finished' else ('wandered_infeasible' if st in ('stuck', 'time_limit') else st)
    if st == 'model_infeasible':
        return 'false_infeasible'
    if st == 'model_finished':
        return 'wrong_answer' if r.get('final_state_ok') else 'false_finish'
    if r.get('reached_goal_state_at_step') is not None:
        return 'reached_no_finish'
    return {'stuck': 'stuck_loop', 'time_limit': 'timeout', 'invalid_choice': 'invalid_choice'}.get(st, st or 'other')


def load_trace(folder):
    snaps = []
    for f in sorted(glob.glob(str(folder / '[0-9][0-9].snapshot.json'))):
        s = json.loads(Path(f).read_text())
        snaps.append(s)
    return snaps


def regrade(folder, suite, private):
    raw = json.loads((folder / 'trial.json').read_text())
    tid = LEGACY_IDS.get(raw['task'], raw['task'])
    prov = LEGACY_PROVIDERS.get(raw['provider'], raw['provider'])
    task = suite.get(tid)
    rec = {'trial': folder.name.split('-', 2)[0] + '-' + folder.name.split('-', 2)[1], 'task': tid, 'provider': prov,
           'repeat': raw.get('repeat', 0), 'version': raw.get('version', 6), 'obs_mode': raw.get('obs_mode', 'tree+image'),
           'status': raw.get('status'), 'category': task['cat'] if task else raw.get('category'),
           'difficulty': task['diff'] if task else raw.get('difficulty'), 'infeasible': bool(task and task['infeasible'])}
    if raw.get('status') != 'finished' or task is None:
        rec['excluded_reason'] = 'not in suite' if task is None else (raw.get('error') or raw.get('status'))[:160]
        return rec
    snaps = load_trace(folder)
    trace, reached = [], None
    for i, s in enumerate(snaps):
        trace.append(((s.get('header') or {}).get('app', {}).get('id'), s.get('text', '')))
        if reached is None and task['check'](s, list(trace), private):
            reached = i
    final_ok = bool(snaps and task['check'](snaps[-1], trace, private))
    stop = raw.get('stop_reason')
    steps = raw.get('steps', [])
    toks = [usage_tokens((x.get('decision') or {}).get('usage')) for x in steps]
    rec.update({
        'stop_reason': stop, 'final_state_ok': final_ok, 'reached_goal_state_at_step': reached,
        'answer_correct': raw.get('answer_correct'),
        'n_actions': sum(1 for x in steps if (x.get('action') or {}).get('kind') not in (None, 'finish', 'infeasible')),
        'action_kinds': [(x.get('action') or {}).get('kind') for x in steps if x.get('action')],
        'apps_visited': sorted({a for a, _ in trace if a}),
        'task_s': round(raw.get('task_ms', 0) / 1000, 2), 'reset_s': round(raw.get('reset_ms', 0) / 1000, 2),
        'model_s': round(raw.get('model_ms', 0) / 1000, 3), 'action_s': round(raw.get('action_ms', 0) / 1000, 2),
        'observe_s': round(sum((x.get('next_observation') or {}).get('observation_ms', 0) or x.get('observe_ms', 0) for x in steps) / 1000, 2),
        'model_ms_per_call': [round((x.get('decision') or {}).get('ms', 0), 1) for x in steps if x.get('decision')],
        'model_calls': sum(1 for x in steps if x.get('decision')) + (1 if raw.get('answer') else 0),
        'device_calls': raw.get('device_calls'), 'failed_actions': raw.get('failed_actions', 0),
        'input_tokens': sum(a for a, _ in toks), 'output_tokens': sum(b for _, b in toks),
        'images_sent': sum(1 for x in steps if x.get('image_sent')), 'mean_candidates': round(sum(x.get('n_candidates', 0) for x in steps) / max(1, len(steps)), 1),
        'rate_limit_wait_s': round(raw.get('rate_limit_wait_ms', 0) / 1000, 1),
    })
    if task['infeasible']:
        rec['success'] = stop == 'model_infeasible'
    else:
        rec['success'] = bool(final_ok and stop == 'model_finished' and rec['answer_correct'] is not False)
    rec['failure_mode'] = failure_mode(rec)
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('raw', nargs='+', type=Path)
    ap.add_argument('--release', type=Path, required=True)
    ap.add_argument('--private', default='config/private.json')
    a = ap.parse_args()
    private = load_private(a.private)
    suite = build(private)
    recs = []
    for root in a.raw:
        for f in sorted(root.glob('*/trial.json')):
            recs.append(regrade(f.parent, suite, private))
    a.release.mkdir(parents=True, exist_ok=True)
    with open(a.release / 'trials.jsonl', 'w') as f:
        for r in sorted(recs, key=lambda r: r['trial']):
            f.write(json.dumps(r, sort_keys=True) + '\n')
    ok = [r for r in recs if r['status'] == 'finished' and 'excluded_reason' not in r]
    print(f'{len(recs)} trials, {len(ok)} scored, {sum(r["success"] for r in ok)} passed -> {a.release}/trials.jsonl')


if __name__ == '__main__':
    main()

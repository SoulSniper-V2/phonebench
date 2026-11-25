#!/usr/bin/env python3
"""Benchmark-quality audit. Prints one line per failing criterion, then `failing=N`.

What makes a benchmark trustworthy, as checks (modelled on OSWorld / AndroidWorld practice and
public benches such as sandbox-bench): no private data, a hard non-saturated suite with infeasible
tasks, enough repeats for intervals, a grader validated by hand, reproducible numbers, and docs.
"""
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
CORE = ['jev-1.14', 'jev-1.13', 'gemini-decision-1']
fails = []


def check(name, ok, detail=''):
    if not ok:
        fails.append(f'FAIL {name}' + (f': {detail}' if detail else ''))


def sh(*cmd):
    return subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)


# ---------------------------------------------------------------- privacy
private_path = ROOT / 'config/private.json'
deny = json.loads(private_path.read_text()).get('pii_denylist', []) if private_path.exists() else []
check('privacy.denylist_present', len(deny) >= 5, 'config/private.json needs a pii_denylist')
files = [f for f in sh('git', 'ls-files', '-co', '--exclude-standard').stdout.split('\n') if f]
leaks = []
for f in files:
    p = ROOT / f
    if not p.is_file() or p.stat().st_size > 5_000_000:
        continue
    try:
        t = p.read_text(errors='ignore')
    except OSError:
        continue
    leaks += [f'{f}: {w[:3]}…' for w in deny if w and w in t]
    if '/Users/' in t and f != 'scripts/audit.py':
        leaks.append(f'{f}: absolute home path')
check('privacy.no_leaks', not leaks, '; '.join(leaks[:5]))
for f in files:
    if f.endswith(('.png', '.jpg')) and not f.startswith('site/'):
        check('privacy.no_raw_screenshots', False, f)
        break

# ---------------------------------------------------------------- code health
r = sh(sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-q')
check('tests.pass', r.returncode == 0, r.stderr.strip().splitlines()[-1] if r.stderr.strip() else '')

# ---------------------------------------------------------------- suite design
from phonebench.tasks import build, load_private  # noqa: E402
suite = build(load_private(str(private_path)))
public = build(None)
check('suite.size>=25', len(suite) >= 25, f'{len(suite)} tasks')
check('suite.infeasible>=2', sum(t['infeasible'] for t in suite.values()) >= 2)
hard = sum(t['diff'] == 'hard' for t in suite.values()) / max(1, len(suite))
check('suite.hard_share>=35%', hard >= 0.35, f'{hard:.0%}')
check('suite.multi_step_reasoning>=3', sum(t['cat'] in ('multi-app', 'reasoning') for t in suite.values()) >= 3)
check('suite.public_runs_without_private', len(public) >= 20, f'{len(public)} public tasks')
tasks_md = (ROOT / 'docs/TASKS.md').read_text() if (ROOT / 'docs/TASKS.md').exists() else ''
missing = [t for t in suite if f'`{t}`' not in tasks_md]
check('docs.every_task_documented', not missing, ', '.join(missing[:6]))

# ---------------------------------------------------------------- results
rels = sorted(p for p in (ROOT / 'results').glob('v*') if (p / 'trials.jsonl').exists())
check('results.release_exists', bool(rels))
if rels:
    rel = rels[-1]
    rows = [json.loads(l) for l in open(rel / 'trials.jsonl')]
    scored = [r for r in rows if r['status'] == 'finished' and 'excluded_reason' not in r and r.get('obs_mode', 'tree+image') == 'tree+image']
    for m in CORE:
        thin = [t for t in suite if sum(1 for r in scored if r['provider'] == m and r['task'] == t) < 3]
        check(f'coverage.{m}>=3_per_task', not thin, f'{len(thin)} tasks under 3 trials')
    clef = [m for m in ('clef-flash', 'clef', 'clef-omni') if {r['task'] for r in scored if r['provider'] == m} >= set(suite)]
    check('coverage.clef_family_full_pass', bool(clef))
    feas = [t for t in suite if not suite[t]['infeasible']]
    never = [t for t in feas if not any(r['success'] for r in scored if r['task'] == t)]
    check('suite.every_task_solvable', not never, 'never passed: ' + ', '.join(never[:6]))
    S_path = rel / 'summary.json'
    if S_path.exists():
        S = json.loads(S_path.read_text())
        best = max((m['task_macro_pass_rate'] for m in S['models']), default=1)
        check('suite.not_saturated(best<=85%)', best <= 0.85, f'best {best:.0%}')
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td) / rel.name
            tmp.mkdir()
            (tmp / 'trials.jsonl').write_text((rel / 'trials.jsonl').read_text())
            sh(sys.executable, '-m', 'phonebench.report', str(tmp))
            again = json.loads((tmp / 'summary.json').read_text()) if (tmp / 'summary.json').exists() else None
        check('results.reproducible', again == S, 'summary.json differs from regenerated')
        res_md = (rel / 'RESULTS.md').read_text() if (rel / 'RESULTS.md').exists() else ''
        check('results.has_confidence_intervals', '95% CI' in res_md)
        abl = {k.split('|')[0] for k, v in S.get('ablation', {}).items() if k.endswith('|tree') and v[1] >= 10}
        check('analysis.observation_ablation>=2_models', len(abl) >= 2, f'{len(abl)} models')
    else:
        check('results.summary_exists', False)
    audit_p = rel / 'grader_audit.json'
    if audit_p.exists():
        A = json.loads(audit_p.read_text())
        fails_ids = {r['trial'] for r in scored if not r['success']}
        pass_ids = {r['trial'] for r in scored if r['success']}
        covered = set(A)
        check('grader.audits_all_failures', fails_ids <= covered, f'{len(fails_ids - covered)} unaudited failures')
        check('grader.audits_25%_of_passes', len(pass_ids & covered) >= 0.25 * len(pass_ids), f'{len(pass_ids & covered)}/{len(pass_ids)}')
        by_trial = {r['trial']: r for r in scored}
        dis = [k for k, v in A.items() if k in by_trial and v['human_success'] != by_trial[k]['success']]
        check('grader.agreement>=95%', len(dis) <= 0.05 * max(1, len(covered)), f'{len(dis)} disagreements: {dis[:3]}')
    else:
        check('grader.audit_exists', False)

# ---------------------------------------------------------------- docs & visuals
readme = (ROOT / 'README.md').read_text() if (ROOT / 'README.md').exists() else ''
for sec in ('## Results', '## How it works', '## Tasks', '## Reproduce', '## Limitations'):
    check(f'docs.readme{sec[2:].lower().replace(" ", "_")}', sec in readme)
check('docs.method', (ROOT / 'docs/METHOD.md').exists())
for img in ('leaderboard.png', 'speed.png', 'failures.png'):  # matrix dropped: owner found it unreadable
    p = ROOT / 'site/assets' / img
    ok = p.exists() and rels and p.stat().st_mtime >= (rels[-1] / 'summary.json').stat().st_mtime - 1 if (rels and (rels[-1] / 'summary.json').exists()) else False
    check(f'visuals.{img}_fresh', bool(ok))
    check(f'docs.readme_embeds_{img}', f'site/assets/{img}' in readme)
check('site.index', (ROOT / 'site/index.html').exists())

for f in fails:
    print(f)
print(f'failing={len(fails)}')

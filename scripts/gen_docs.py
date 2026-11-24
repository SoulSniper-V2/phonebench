#!/usr/bin/env python3
"""Regenerate docs/TASKS.md from the task suite (private values never printed)."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from phonebench.tasks import build  # noqa: E402

PLACEHOLDER = {'school_portal': {'class': '<class>', 'grade': '<grade>', 'grade_options': ['<grade>'], 'assignment_class': '<class>',
                                 'lowest_class': '<class>', 'class_options': ['<class>']}}
suite = build(PLACEHOLDER)
cats = ['navigate', 'info', 'reasoning', 'multi-app', 'compute', 'write', 'infeasible', 'judged']
o = ['# Tasks', '',
     f'{len(suite)} tasks across {len({a for t in suite.values() for a in t["apps"]})} apps. Every task starts on the Home screen after its apps are '
     'reset to a verified root view. The model sees only the goal; there are no per-task hints or click recipes.', '',
     '**Typeable strings** are the text the user supplies. Decision models choose among options and cannot invent text, so any '
     'text a task needs is offered as an option. All other actions are generic and shared by every task.', '',
     '**Pass** means the programmatic check holds on the final screen when the model says FINISH, and, for tasks with a question, '
     'the multiple-choice answer is right. For infeasible tasks, pass means the model says INFEASIBLE.', '',
     '| Difficulty | Count |', '|---|---|'] + [f'| {d} | {sum(t["diff"] == d for t in suite.values())} |' for d in ('easy', 'medium', 'hard')] + ['']
for c in cats:
    ts = [t for t in suite.values() if t['cat'] == c]
    if not ts:
        continue
    o += [f'## {c}', '', '| Task | Difficulty | Goal | Typeable strings | Pass check | Asks |', '|---|---|---|---|---|---|']
    for t in ts:
        goal = t.get('public_goal') or t['goal']
        if t['private']:
            goal = goal.replace('<class>', '<a named class>')
        check = 'reviewer rubric (scored separately)' if t.get('judged') else 'says INFEASIBLE' if t['infeasible'] else ('final screen + trajectory' if t['cat'] == 'multi-app' else 'final screen')
        ask = 'multiple choice' if t['answer'] else ''
        o.append(f"| `{t['id']}` | {t['diff']} | {goal}{' *(private config)*' if t['private'] else ''} | {', '.join(f'`{p}`' for p in t['params']) if not t['private'] else '–'} | {check} | {ask} |")
    o.append('')
(ROOT / 'docs/TASKS.md').write_text('\n'.join(o))
print(f'docs/TASKS.md: {len(suite)} tasks')

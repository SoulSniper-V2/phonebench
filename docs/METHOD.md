# Method

PhoneBench measures whether a **decision model** — a fast model that answers typed questions
(choice / probability / score) instead of generating text — can operate a real iPhone end to end.
The design follows computer-use benchmarks such as OSWorld and AndroidWorld, adapted to what a
decision model can and cannot do.

## The loop

```
reset task apps to a verified root view → Home screen → start clock
repeat:
    observe   accessibility tree (phonedriver) + screenshot
    ask       one `choice` question: "which action next?" over every legal action
    act       execute that one action through phonedriver, wait for the UI to settle
until  FINISH | INFEASIBLE | wall-time limit (240 s) | stuck (same action, unchanged screen, 6×)
grade  programmatic check on the final phone state (+ trajectory for multi-app tasks)
```

## What the model sees

| Input | Detail |
|---|---|
| Goal | One natural-language sentence. No hints, no plan, no click recipe. |
| Screen elements | Every visible accessibility element with role, label, value (≤ 9 000 chars). |
| Screenshot | Same screen, PNG at 1 px per point. Omitted for Mail/Messages/Gmail (privacy) and in the `tree` ablation. |
| History | The last 12 actions it chose, and the driver's result for the last one (e.g. "no element changed"). |

## What the model can do

The action space is generated from the current screen and is **identical for every task**:

| Action | Notes |
|---|---|
| Tap any visible element | Except switches (no setting is ever flipped) and anything the safety filter blocks. |
| Type a task string | Into any text field, or the focused one. Decision models can't write text, so the strings a user would supply (a search term, a note's text) are offered as options. |
| Return, scroll up/down, back (edge swipe), Home | |
| Open any of 26 apps | Including look-alikes (Apple Maps vs Google Maps, Mail vs Gmail) — choosing the right app is part of the task. |
| Wait 1.5 s | |
| FINISH / INFEASIBLE | Ends the trial. |

There is **no step budget**. A step cap measures the cap, not the model; the 240 s wall-time limit and
the stuck detector only stop runaway loops, and every stop reason is reported.

## Grading

- **Pass** = the model chose FINISH, the task's check holds on the final accessibility snapshot, and
  (for info tasks) its multiple-choice answer is right. The model's claim of success is never trusted.
- **Infeasible tasks** (OSWorld-style) pass only when the model chooses INFEASIBLE; choosing
  INFEASIBLE on a feasible task is a failure (`false_infeasible`).
- Checks are pure functions of saved snapshots, so `phonebench.regrade` re-scores every past trial
  when a check is fixed. Every release ships `grader_audit.json`: a human review of every failing
  trial and at least a quarter of passes, against the final screenshot.

## Failure taxonomy

| Mode | Meaning |
|---|---|
| `false_finish` | Said FINISH, goal not on screen (includes using the wrong app). |
| `wrong_answer` | Reached the goal screen, picked the wrong multiple-choice answer. |
| `reached_no_finish` | Was at the goal at some step, kept going, never finished there. |
| `stuck_loop` | Same action on an unchanged screen 6 times. |
| `timeout` | 240 s of task time elapsed. |
| `false_infeasible` / `missed_infeasible` | Gave up on a feasible task / claimed to finish an impossible one. |

## Metrics

- **Score**: task-macro pass rate — the mean over tasks of each task's pass rate, so a task with more
  repeats does not weigh more. Pass/trials and a 95% Wilson interval are reported next to it.
- **Time to pass**: wall time from the Home screen to FINISH, for passing trials. Provider rate-limit
  waits are subtracted and reported separately; reset time is excluded.
- **Decision latency**: per-call round trip, p50/p90/p99. **Tokens**: provider-reported input/output.
- **Time split**: share of task time spent in the model vs in device actions and observation.

## Resets on a physical phone

phonedriver can't force-quit apps on a physical iPhone, so each task's apps are navigated back to a
**verified root view** (e.g. the Home tab selected, no player open) using navigation only. A reset that
can't be verified marks the trial `reset_failed`; it is excluded and never counted against the model.
Trials are run in a seeded random order within each repeat so time-of-day effects spread evenly.

## Safety

Two independent layers. The candidate filter never offers send / buy / install / follow / like / post /
delete / trial / sign-up / subscribe / confirm controls or any switch. phonedriver itself refuses taps that
spend money or can't be undone without human approval. One task writes (a Notes note with fixed text).

## Privacy

Raw runs (screenshots, accessibility text) stay on the device owner's machine. Published results contain
task ids, outcomes, counts and timings only. Tasks over personal data read their names and expected values
from `config/private.json` (git-ignored), and the repo's audit fails if any string on a private deny-list
appears in a tracked file.

## Known limitations

- One phone, one account, one network: absolute times are specific to this setup.
- App content changes (feeds, ads, store sheets). That is realistic; it is also why each cell is repeated.
- TikTok's accessibility tree hangs the XCUITest runner, so TikTok is excluded.
- Free-tier quotas shaped what could be run: Gemini Decision is rate-limited (waits are excluded from
  timings), and Cloudflare's daily free allocation limits how many Clef trials fit in a day.

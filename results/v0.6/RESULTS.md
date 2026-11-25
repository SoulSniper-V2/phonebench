# PhoneBench results — v0.6

51 scored trials on a physical iPhone, 19 tasks, 3 decision models. 7 phone attempts were excluded for harness reasons (listed at the end) and never counted as model failures. Simulator trials and screenshot-free trials are reported in their own sections, never pooled with the phone score.

| Rank | Model | Score (task-macro) | Pass / trials | 95% CI | Median time to pass | Median actions to pass | Decision p50 / p90 | Input tokens / task | Model share of time | False finish rate |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Gemini Decision 1 | **93%** | 14/15 | 70%–99% | 20.96 s | 4.0 | 925 / 1299 ms | 14,221 | 26% | 0% |
| 2 | Jev 1.14 | **78%** | 14/18 | 55%–91% | 13.465 s | 3.5 | 219 / 440 ms | 17,847 | 7% | 17% |
| 3 | Jev 1.13 | **67%** | 12/18 | 44%–84% | 17.14 s | 4.0 | 211 / 436 ms | 20,279 | 6% | 17% |

## By difficulty

| Model | easy | medium | hard |
|---|---|---|---|
| Gemini Decision 1 | 3/3 | 7/7 | 4/5 |
| Jev 1.14 | 2/3 | 8/10 | 4/5 |
| Jev 1.13 | 2/3 | 6/10 | 4/5 |

## By category

| Model | compute | info | navigate | write |
|---|---|---|---|---|
| Gemini Decision 1 | 1/1 | 6/6 | 6/7 | 1/1 |
| Jev 1.14 | 1/1 | 7/7 | 5/9 | 1/1 |
| Jev 1.13 | 1/1 | 5/7 | 5/9 | 1/1 |

## Failure modes

| Model | false_finish | wrong_answer | reached_no_finish | stuck_loop | timeout | false_infeasible | missed_infeasible | wandered_infeasible | invalid_choice |
|---|---|---|---|---|---|---|---|---|---|
| Gemini Decision 1 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |
| Jev 1.14 | 3 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |
| Jev 1.13 | 3 | 0 | 0 | 3 | 0 | 0 | 0 | 0 | 0 |

## Every task

✅ pass · ❌ fail, with seconds and actions per trial.

| Task | Category | Difficulty | Gemini Decision 1 | Jev 1.14 | Jev 1.13 |
|---|---|---|---|---|---|
| `amazon_product` | navigate | hard | ❌24s/7 | ❌59s/15 | ❌69s/17 |
| `appstore_ratings` | navigate | medium | ✅22s/5 | ✅23s/5 | ✅27s/6 |
| `calc_expression` | compute | easy | ✅53s/16 | ✅27s/9 | ✅24s/10 |
| `gmail_open_email` | navigate | medium | – | ❌22s/5 | ❌6s/1 |
| `gmaps_place` | navigate | medium | ✅27s/4 | ❌45s/7 | ✅46s/9 |
| `maps_route` | navigate | hard | ✅31s/5 | ✅26s/5 | ✅27s/5 |
| `notes_create` | write | medium | ✅21s/4 | ✅12s/3 | ✅14s/3 |
| `portal_assignment_score` | navigate | hard | ✅17s/4 | ✅10s/3 | ✅17s/4 |
| `portal_attendance` | navigate | easy | ✅9s/2 | ❌8s/2 | ❌10s/2 |
| `portal_grade_lookup` | info | medium | ✅21s/5 | ✅14s/4 | ❌21s/5 |
| `reddit_community` | navigate | medium | ✅28s/6 | ✅17s/5 | ✅17s/5 |
| `safari_fact` | info | hard | ✅19s/3 | ✅13s/3 | ✅14s/3 |
| `settings_battery_health` | info | hard | ✅18s/4 | ✅6s/1 | ✅23s/4 |
| `settings_os_version` | info | medium | ✅13s/3 | ✅11s/3 | ✅8s/2 |
| `settings_storage` | info | medium | ✅35s/7 | ✅12s/3 | ❌45s/12 |
| `stocks_detail` | info | easy | ✅19s/4 | ✅9s/2 | ✅6s/1 |
| `weather_city` | info | medium | – | ✅31s/6 | ✅16s/2 |
| `x_profile` | navigate | medium | – | – | ❌103s/13 |
| `yt_creator_video` | navigate | medium | – | ✅24s/7 | – |

## Provenance

Trials from 2026-11-25 on record the device, the OS and hashes of the task suite and the harness (`phonebench/version.py`). Results are comparable only within one suite hash.

- 58 earlier trials predate stamping

## Excluded trials

- 2 × gemini: HTTP 429: {"error":{"message":"Rate limit exceeded f
- 2 × phonedriver timed out; inspect the phone before retrying
- 2 × RESET_FAILED: root view of com.google.ios.youtube not verifi
- 1 × running

# PhoneBench results — v0.7

154 scored trials on a physical iPhone, 31 tasks, 4 decision models. 38 phone attempts were excluded for harness reasons (listed at the end) and never counted as model failures. Simulator trials and screenshot-free trials are reported in their own sections, never pooled with the phone score.

| Rank | Model | Score (task-macro) | Pass / trials | 95% CI | Median time to pass | Median actions to pass | Decision p50 / p90 | Input tokens / task | Model share of time | False finish rate |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Gemini Decision 1 | **82%** | 31/40 | 62%–88% | 18.53 s | 4.0 | 880 / 1274 ms | 13,836 | 27% | 6% |
| 2 | Jev 1.14 | **71%** | 33/47 | 56%–81% | 14.14 s | 4.0 | 222 / 430 ms | 20,724 | 9% | 18% |
| 3 | Jev 1.13 | **70%** | 30/41 | 58%–84% | 15.035 s | 4.0 | 216 / 375 ms | 18,037 | 7% | 16% |
| 4 | Clef Omni | **46%** | 12/26 | 29%–65% | 17.51 s | 3.0 | 471 / 953 ms | 15,992 | 13% | 17% |

## By difficulty

| Model | easy | medium | hard |
|---|---|---|---|
| Gemini Decision 1 | 3/4 | 13/13 | 15/23 |
| Jev 1.14 | 3/4 | 13/19 | 17/24 |
| Jev 1.13 | 2/3 | 12/17 | 16/21 |
| Clef Omni | 2/3 | 5/12 | 5/11 |

## By category

| Model | compute | infeasible | info | multi-app | navigate | reasoning | write |
|---|---|---|---|---|---|---|---|
| Gemini Decision 1 | 1/1 | 4/4 | 12/16 | 2/2 | 10/13 | 0/2 | 2/2 |
| Jev 1.14 | 2/2 | 3/3 | 14/16 | 2/4 | 11/20 | 0/1 | 1/1 |
| Jev 1.13 | 1/1 | 4/4 | 12/15 | 2/2 | 10/17 | 0/1 | 1/1 |
| Clef Omni | 0/1 | 2/2 | 6/11 | 1/1 | 2/9 | 0/1 | 1/1 |

## Failure modes

| Model | false_finish | wrong_answer | reached_no_finish | stuck_loop | timeout | false_infeasible | missed_infeasible | wandered_infeasible | invalid_choice |
|---|---|---|---|---|---|---|---|---|---|
| Gemini Decision 1 | 2 | 0 | 2 | 1 | 0 | 4 | 0 | 0 | 0 |
| Jev 1.14 | 8 | 0 | 0 | 5 | 0 | 1 | 0 | 0 | 0 |
| Jev 1.13 | 6 | 0 | 0 | 5 | 0 | 0 | 0 | 0 | 0 |
| Clef Omni | 4 | 1 | 2 | 7 | 0 | 0 | 0 | 0 | 0 |

## Every task

✅ pass · ❌ fail, with seconds and actions per trial.

| Task | Category | Difficulty | Gemini Decision 1 | Jev 1.14 | Jev 1.13 | Clef Omni |
|---|---|---|---|---|---|---|
| `amazon_product` | navigate | hard | ❌24s/7 ❌2s/0 | ❌59s/15 ❌33s/9 | ❌69s/17 | – |
| `appstore_developer` | info | hard | ❌8s/2 | ❌7s/2 ❌41s/13 | ❌7s/2 | ❌47s/8 |
| `appstore_ratings` | navigate | medium | ✅22s/5 | ❌23s/5 ❌31s/10 | ✅27s/6 | – |
| `calc_expression` | compute | easy | ✅53s/16 | ✅27s/9 ✅33s/12 | ✅24s/10 | ❌44s/16 |
| `cross_appstore_to_web` | multi-app | hard | ✅24s/6 | ✅26s/8 ❌38s/12 | ✅18s/5 | – |
| `cross_weather_to_note` | multi-app | hard | ✅31s/8 | ❌1s/0 ✅26s/9 | ✅16s/5 | ✅49s/8 |
| `gmail_open_email` | navigate | medium | – | ❌22s/5 ❌11s/3 | ❌6s/1 | ❌58s/11 |
| `gmaps_place` | navigate | medium | ✅27s/4 | ❌45s/7 ❌64s/17 | ✅46s/9 ❌6s/1 | ❌19s/2 |
| `infeasible_missing_app` | infeasible | medium | ✅1s/0 ✅3s/0 | ✅5s/1 ✅1s/0 | ✅1s/0 ✅1s/0 | ✅5s/1 |
| `infeasible_missing_feature` | infeasible | hard | ✅2s/0 ✅2s/0 | ✅8s/2 | ✅4s/1 ✅6s/2 | ✅18s/4 |
| `maps_route` | navigate | hard | ✅31s/5 | ✅26s/5 | ✅27s/5 | – |
| `maps_walking_coffee` | navigate | hard | ✅29s/6 | ✅29s/7 ✅24s/6 | ✅27s/6 ✅30s/8 | – |
| `notes_create` | write | medium | ✅21s/4 ✅14s/4 | ✅12s/3 | ✅14s/3 | ✅13s/3 |
| `portal_assignment_score` | navigate | hard | ✅17s/4 | ✅10s/3 ✅13s/4 | ✅17s/4 | ❌31s/8 |
| `portal_attendance` | navigate | easy | ✅9s/2 | ❌8s/2 | ❌10s/2 | ✅17s/3 |
| `portal_grade_lookup` | info | medium | ✅21s/5 | ✅14s/4 ✅14s/4 | ❌21s/5 | ❌32s/8 |
| `portal_lowest_class` | reasoning | hard | ❌49s/16 ❌65s/20 | ❌24s/10 | ❌23s/9 | ❌30s/9 |
| `reddit_community` | navigate | medium | ✅28s/6 | ✅17s/5 | ✅17s/5 ✅22s/7 | ❌14s/4 |
| `reddit_sort_top` | navigate | hard | ✅27s/8 ❌28s/7 | ✅26s/9 | ❌14s/5 ❌23s/7 | ❌25s/7 |
| `safari_compare` | info | hard | ✅15s/3 ✅14s/3 | ✅10s/3 ✅12s/3 | ✅11s/3 ✅13s/3 | ✅18s/3 |
| `safari_fact` | info | hard | ✅19s/3 ✅17s/4 | ✅13s/3 | ✅14s/3 | ✅17s/3 |
| `settings_battery_health` | info | hard | ✅18s/4 ✅8s/2 | ✅6s/1 ✅13s/4 ✅17s/4 | ✅23s/4 ✅9s/3 ✅12s/4 | ✅14s/4 |
| `settings_os_version` | info | medium | ✅13s/3 ✅11s/3 | ✅11s/3 ✅16s/5 | ✅8s/2 | ❌83s/24 |
| `settings_storage` | info | medium | ✅35s/7 | ✅12s/3 ✅12s/4 | ❌45s/12 ✅10s/3 | ❌36s/11 |
| `sim_safari_capital` | info | medium | – | – | – | ✅20s/3 |
| `stocks_detail` | info | easy | ✅19s/4 ❌6s/1 | ✅9s/2 | ✅6s/1 | ✅11s/2 |
| `stocks_market_cap` | info | hard | ❌6s/1 ❌6s/1 | – | ✅11s/3 | ❌12s/2 |
| `weather_city` | info | medium | ✅14s/3 | ✅31s/6 | ✅16s/2 ✅16s/5 | ✅25s/5 |
| `x_profile` | navigate | medium | – | – | ❌103s/13 | ❌167s/25 |
| `yt_channel_videos_tab` | navigate | hard | ✅22s/6 | ✅16s/6 ✅16s/6 | ✅18s/6 | ❌78s/5 |
| `yt_creator_video` | navigate | medium | ✅20s/5 | ✅24s/7 ✅17s/6 | ✅13s/4 | ✅78s/5 |

## Judged track

Open-ended goals (best coffee nearby, a useful Reddit post, a short tutorial). Claude Opus 5.5 grades each trajectory against the task rubric; verdicts and reasons are in `judgments.json`. Not part of the headline score.

| Model | Pass / trials |
|---|---|
| Clef Omni | 2/5 |

## Simulator track

iOS Simulator, the tasks that run there (built-in apps and Safari). Reported separately from the phone.

| Model | Pass / trials | 95% CI | Tasks | Median time to pass | Decision p50 |
|---|---|---|---|---|---|
| Jev 1.14 | 27/27 | 88%–100% | 9 | 13.18 s | 209 ms |
| Jev 1.13 | 23/27 | 68%–94% | 9 | 11.49 s | 185 ms |
| Strands Decider 2B (local) | 4/18 | 9%–45% | 9 | 5.185 s | 696 ms |

## Observation ablation

Same model, same device, with and without the screenshot (all trials, not only the scored phone set).

| Model | Device | Tree + screenshot | Tree only |
|---|---|---|---|
| Jev 1.14 | sim | 27/27 (100%) | 15/18 (83%) |
| Strands Decider 2B (local) | sim | 4/18 (22%) | 5/18 (28%) |

## Provenance

Trials from 2026-11-25 on record the device, the OS and hashes of the task suite and the harness (`phonebench/version.py`). Results are comparable only within one suite hash.

- 8 × iPhone18,3 · iOS 27.0
- 17 × suite 7c2156328bd2 · harness a93e95f0c490 · phonedriver 0.1.7
- 2 × suite 6e837d5fb40e · harness f0ea2138e6c6 · phonedriver 0.1.7
- 296 earlier trials predate stamping

## Excluded trials

- 7 × error: The device is locked. Unlock it by hand; phonedriver 
- 4 × error: no device "ios:<device>"; connected: sim:<device> (iP
- 4 × opened into navigation left running by an earlier trial
- 2 × gemini: HTTP 429: {"error":{"message":"Rate limit exceeded f
- 2 × phonedriver timed out; inspect the phone before retrying
- 2 × RESET_FAILED: root view of com.google.ios.youtube not verifi
- 2 × answer question not asked (trial predates the question)
- 2 × RESET_FAILED: root view of com.infinitecampus.student.campus
- 2 × RESET_FAILED: root view of com.apple.AppStore not verified
- 2 × clef-omni: HTTP 429: {"errors":[{"message":"AiError: AiError
- 1 × running
- 1 × error: device ios:<device> disconnected
- 1 × error: connection error: runner tree: Failed to get matching
- 1 × RESET_FAILED: root view of com.apple.Maps not verified
- 1 × clef-omni: <urlopen error [Errno 60] Operation timed out>
- 1 × clef-flash: HTTP 429: {"errors":[{"message":"AiError: AiErro
- 1 × clef: HTTP 429: {"errors":[{"message":"AiError: AiError: you
- 1 × phone locked during the trial
- 1 × resetting

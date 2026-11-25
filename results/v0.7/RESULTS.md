# PhoneBench results — v0.7

125 scored trials on a physical iPhone, 30 tasks, 3 decision models. 134 trials excluded for harness reasons (listed at the end), never counted as model failures.

| Rank | Model | Score (task-macro) | Pass / trials | 95% CI | Median time to pass | Median actions to pass | Decision p50 / p90 | Input tokens / task | Model share of time | False finish rate |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Gemini Decision 1 | **82%** | 31/39 | 64%–89% | 18.53 s | 4.0 | 880 / 1274 ms | 14,160 | 27% | 6% |
| 2 | Jev 1.13 | **72%** | 30/40 | 60%–86% | 15.035 s | 4.0 | 215 / 376 ms | 18,710 | 7% | 14% |
| 3 | Jev 1.14 | **71%** | 32/46 | 55%–81% | 15.18 s | 4.0 | 222 / 431 ms | 20,816 | 9% | 18% |

## By difficulty

| Model | easy | medium | hard |
|---|---|---|---|
| Gemini Decision 1 | 3/4 | 13/13 | 15/22 |
| Jev 1.13 | 2/3 | 12/16 | 16/21 |
| Jev 1.14 | 3/4 | 12/18 | 17/24 |

## By category

| Model | compute | infeasible | info | multi-app | navigate | reasoning | write |
|---|---|---|---|---|---|---|---|
| Gemini Decision 1 | 1/1 | 4/4 | 12/16 | 2/2 | 10/12 | 0/2 | 2/2 |
| Jev 1.13 | 1/1 | 4/4 | 12/15 | 2/2 | 10/16 | 0/1 | 1/1 |
| Jev 1.14 | 2/2 | 2/2 | 14/16 | 2/4 | 11/20 | 0/1 | 1/1 |

## Failure modes

| Model | false_finish | wrong_answer | reached_no_finish | stuck_loop | timeout | false_infeasible | missed_infeasible | wandered_infeasible | invalid_choice |
|---|---|---|---|---|---|---|---|---|---|
| Gemini Decision 1 | 2 | 0 | 2 | 1 | 0 | 3 | 0 | 0 | 0 |
| Jev 1.13 | 5 | 0 | 0 | 5 | 0 | 0 | 0 | 0 | 0 |
| Jev 1.14 | 8 | 0 | 0 | 5 | 0 | 1 | 0 | 0 | 0 |

## Every task

✅ pass · ❌ fail, with seconds and actions per trial.

| Task | Category | Difficulty | Gemini Decision 1 | Jev 1.13 | Jev 1.14 |
|---|---|---|---|---|---|
| `amazon_product` | navigate | hard | ❌24s/7 | ❌69s/17 | ❌59s/15 ❌33s/9 |
| `appstore_developer` | info | hard | ❌8s/2 | ❌7s/2 | ❌7s/2 ❌41s/13 |
| `appstore_ratings` | navigate | medium | ✅22s/5 | ✅27s/6 | ❌23s/5 ❌31s/10 |
| `calc_expression` | compute | easy | ✅53s/16 | ✅24s/10 | ✅27s/9 ✅33s/12 |
| `cross_appstore_to_web` | multi-app | hard | ✅24s/6 | ✅18s/5 | ✅26s/8 ❌38s/12 |
| `cross_weather_to_note` | multi-app | hard | ✅31s/8 | ✅16s/5 | ❌1s/0 ✅26s/9 |
| `gmail_open_email` | navigate | medium | – | ❌6s/1 | ❌22s/5 ❌11s/3 |
| `gmaps_place` | navigate | medium | ✅27s/4 | ✅46s/9 | ❌45s/7 ❌64s/17 |
| `infeasible_missing_app` | infeasible | medium | ✅1s/0 ✅3s/0 | ✅1s/0 ✅1s/0 | ✅5s/1 |
| `infeasible_missing_feature` | infeasible | hard | ✅2s/0 ✅2s/0 | ✅4s/1 ✅6s/2 | ✅8s/2 |
| `maps_route` | navigate | hard | ✅31s/5 | ✅27s/5 | ✅26s/5 |
| `maps_walking_coffee` | navigate | hard | ✅29s/6 | ✅27s/6 ✅30s/8 | ✅29s/7 ✅24s/6 |
| `notes_create` | write | medium | ✅21s/4 ✅14s/4 | ✅14s/3 | ✅12s/3 |
| `portal_assignment_score` | navigate | hard | ✅17s/4 | ✅17s/4 | ✅10s/3 ✅13s/4 |
| `portal_attendance` | navigate | easy | ✅9s/2 | ❌10s/2 | ❌8s/2 |
| `portal_grade_lookup` | info | medium | ✅21s/5 | ❌21s/5 | ✅14s/4 ✅14s/4 |
| `portal_lowest_class` | reasoning | hard | ❌49s/16 ❌65s/20 | ❌23s/9 | ❌24s/10 |
| `reddit_community` | navigate | medium | ✅28s/6 | ✅17s/5 ✅22s/7 | ✅17s/5 |
| `reddit_sort_top` | navigate | hard | ✅27s/8 ❌28s/7 | ❌14s/5 ❌23s/7 | ✅26s/9 |
| `safari_compare` | info | hard | ✅15s/3 ✅14s/3 | ✅11s/3 ✅13s/3 | ✅10s/3 ✅12s/3 |
| `safari_fact` | info | hard | ✅19s/3 ✅17s/4 | ✅14s/3 | ✅13s/3 |
| `settings_battery_health` | info | hard | ✅18s/4 ✅8s/2 | ✅23s/4 ✅9s/3 ✅12s/4 | ✅6s/1 ✅13s/4 ✅17s/4 |
| `settings_os_version` | info | medium | ✅13s/3 ✅11s/3 | ✅8s/2 | ✅11s/3 ✅16s/5 |
| `settings_storage` | info | medium | ✅35s/7 | ❌45s/12 ✅10s/3 | ✅12s/3 ✅12s/4 |
| `stocks_detail` | info | easy | ✅19s/4 ❌6s/1 | ✅6s/1 | ✅9s/2 |
| `stocks_market_cap` | info | hard | ❌6s/1 ❌6s/1 | ✅11s/3 | – |
| `weather_city` | info | medium | ✅14s/3 | ✅16s/2 ✅16s/5 | ✅31s/6 |
| `x_profile` | navigate | medium | – | ❌103s/13 | – |
| `yt_channel_videos_tab` | navigate | hard | ✅22s/6 | ✅18s/6 | ✅16s/6 ✅16s/6 |
| `yt_creator_video` | navigate | medium | ✅20s/5 | ✅13s/4 | ✅24s/7 ✅17s/6 |

## Observation ablation

Same model, same device, with and without the screenshot (all trials, not only the scored phone set).

| Model | Device | Tree + screenshot | Tree only |
|---|---|---|---|
| Jev 1.14 | sim | 27/27 (100%) | 15/18 (83%) |
| Strands Decider 2B (local) | sim | 4/18 (22%) | 5/18 (28%) |

## Excluded trials

- 6 × task not available on sim
- 4 × error: no device "ios:<device>"; connected: sim:<device> (iP
- 2 × gemini: HTTP 429: {"error":{"message":"Rate limit exceeded f
- 2 × phonedriver timed out; inspect the phone before retrying
- 2 × RESET_FAILED: root view of com.google.ios.youtube not verifi
- 2 × answer question not asked (trial predates the question)
- 1 × running
- 1 × error: device ios:<device> disconnected
hint: Reconnect the 
- 1 × RESET_FAILED: root view of com.infinitecampus.student.campus
- 1 × error: connection error: runner tree: Failed to get matching
- 1 × RESET_FAILED: root view of com.apple.AppStore not verified
- 1 × RESET_FAILED: root view of com.apple.Maps not verified
- 1 × phonedriver timed out
- 1 × strands-2b: HTTP 422: {"detail":"prompt of 4505 tokens (1527

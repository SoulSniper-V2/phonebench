# PhoneBench results — v0.7

87 scored trials on a physical iPhone, 30 tasks, 3 decision models. 30 trials excluded for harness reasons (listed at the end), never counted as model failures.

| Rank | Model | Score (task-macro) | Pass / trials | 95% CI | Median time to pass | Median actions to pass | Decision p50 / p90 | Input tokens / task | Model share of time | False finish rate |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Gemini Decision 1 | **85%** | 23/27 | 68%–94% | 20.99 s | 4.0 | 890 / 1294 ms | 14,391 | 27% | 4% |
| 2 | Jev 1.14 | **72%** | 22/30 | 56%–86% | 13.7 s | 4.0 | 216 / 428 ms | 17,412 | 8% | 18% |
| 3 | Jev 1.13 | **69%** | 21/30 | 52%–83% | 16.17 s | 4.0 | 214 / 433 ms | 19,512 | 7% | 18% |

## By difficulty

| Model | easy | medium | hard |
|---|---|---|---|
| Gemini Decision 1 | 3/3 | 8/8 | 12/16 |
| Jev 1.14 | 2/3 | 8/11 | 12/16 |
| Jev 1.13 | 2/3 | 7/11 | 12/16 |

## By category

| Model | compute | infeasible | info | multi-app | navigate | reasoning | write |
|---|---|---|---|---|---|---|---|
| Gemini Decision 1 | 1/1 | 2/2 | 8/10 | 2/2 | 9/10 | 0/1 | 1/1 |
| Jev 1.14 | 1/1 | 2/2 | 10/11 | 1/2 | 7/12 | 0/1 | 1/1 |
| Jev 1.13 | 1/1 | 2/2 | 8/11 | 2/2 | 7/12 | 0/1 | 1/1 |

## Failure modes

| Model | false_finish | wrong_answer | reached_no_finish | stuck_loop | timeout | false_infeasible | missed_infeasible | wandered_infeasible | invalid_choice |
|---|---|---|---|---|---|---|---|---|---|
| Gemini Decision 1 | 1 | 0 | 1 | 1 | 0 | 1 | 0 | 0 | 0 |
| Jev 1.14 | 5 | 0 | 0 | 2 | 0 | 1 | 0 | 0 | 0 |
| Jev 1.13 | 5 | 0 | 0 | 4 | 0 | 0 | 0 | 0 | 0 |

## Every task

✅ pass · ❌ fail, with seconds and actions per trial.

| Task | Category | Difficulty | Gemini Decision 1 | Jev 1.14 | Jev 1.13 |
|---|---|---|---|---|---|
| `amazon_product` | navigate | hard | ❌24s/7 | ❌59s/15 | ❌69s/17 |
| `appstore_developer` | info | hard | ❌8s/2 | ❌7s/2 | ❌7s/2 |
| `appstore_ratings` | navigate | medium | ✅22s/5 | ❌23s/5 | ✅27s/6 |
| `calc_expression` | compute | easy | ✅53s/16 | ✅27s/9 | ✅24s/10 |
| `cross_appstore_to_web` | multi-app | hard | ✅24s/6 | ✅26s/8 | ✅18s/5 |
| `cross_weather_to_note` | multi-app | hard | ✅31s/8 | ❌1s/0 | ✅16s/5 |
| `gmail_open_email` | navigate | medium | – | ❌22s/5 | ❌6s/1 |
| `gmaps_place` | navigate | medium | ✅27s/4 | ❌45s/7 | ✅46s/9 |
| `infeasible_missing_app` | infeasible | medium | ✅1s/0 | ✅5s/1 | ✅1s/0 |
| `infeasible_missing_feature` | infeasible | hard | ✅2s/0 | ✅8s/2 | ✅4s/1 |
| `maps_route` | navigate | hard | ✅31s/5 | ✅26s/5 | ✅27s/5 |
| `maps_walking_coffee` | navigate | hard | ✅29s/6 | ✅29s/7 | ✅27s/6 |
| `notes_create` | write | medium | ✅21s/4 | ✅12s/3 | ✅14s/3 |
| `portal_assignment_score` | navigate | hard | ✅17s/4 | ✅10s/3 | ✅17s/4 |
| `portal_attendance` | navigate | easy | ✅9s/2 | ❌8s/2 | ❌10s/2 |
| `portal_grade_lookup` | info | medium | ✅21s/5 | ✅14s/4 | ❌21s/5 |
| `portal_lowest_class` | reasoning | hard | ❌49s/16 | ❌24s/10 | ❌23s/9 |
| `reddit_community` | navigate | medium | ✅28s/6 | ✅17s/5 | ✅17s/5 |
| `reddit_sort_top` | navigate | hard | ✅27s/8 | ✅26s/9 | ❌14s/5 |
| `safari_compare` | info | hard | ✅15s/3 | ✅10s/3 | ✅11s/3 |
| `safari_fact` | info | hard | ✅19s/3 | ✅13s/3 | ✅14s/3 |
| `settings_battery_health` | info | hard | ✅18s/4 ✅8s/2 | ✅6s/1 ✅13s/4 | ✅23s/4 ✅9s/3 |
| `settings_os_version` | info | medium | ✅13s/3 | ✅11s/3 | ✅8s/2 |
| `settings_storage` | info | medium | ✅35s/7 | ✅12s/3 | ❌45s/12 |
| `stocks_detail` | info | easy | ✅19s/4 | ✅9s/2 | ✅6s/1 |
| `stocks_market_cap` | info | hard | ❌6s/1 | ✅19s/6 | ✅8s/2 |
| `weather_city` | info | medium | – | ✅31s/6 | ✅16s/2 |
| `x_profile` | navigate | medium | – | – | ❌103s/13 |
| `yt_channel_videos_tab` | navigate | hard | ✅22s/6 | ✅16s/6 | ✅18s/6 |
| `yt_creator_video` | navigate | medium | – | ✅24s/7 | – |

## Observation ablation

| Model | Observation | Pass / trials |
|---|---|---|
| Gemini Decision 1 | tree+image | 23/27 |
| Jev 1.13 | tree+image | 28/39 |
| Jev 1.14 | tree+image | 28/36 |

## Excluded trials

- 6 × task not available on sim
- 2 × running
- 2 × gemini: HTTP 429: {"error":{"message":"Rate limit exceeded f
- 2 × phonedriver timed out; inspect the phone before retrying
- 2 × RESET_FAILED: root view of com.google.ios.youtube not verifi
- 1 × error: device ios:<device> disconnected
hin

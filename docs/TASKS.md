# Tasks

35 tasks across 18 apps. Every task starts on the Home screen after its apps are reset to a verified root view. The model sees only the goal; there are no per-task hints or click recipes.

**Typeable strings** are the text the user supplies. Decision models choose among options and cannot invent text, so any text a task needs is offered as an option. All other actions are generic and shared by every task.

**Pass** means the programmatic check holds on the final screen when the model says FINISH, and, for tasks with a question, the multiple-choice answer is right. For infeasible tasks, pass means the model says INFEASIBLE.

| Difficulty | Count |
|---|---|
| easy | 3 |
| medium | 15 |
| hard | 17 |

## navigate

| Task | Difficulty | Goal | Typeable strings | Pass check | Asks |
|---|---|---|---|---|---|
| `yt_creator_video` | medium | On YouTube, find a video from MrBeast and start watching it. | `MrBeast` | final screen |  |
| `yt_channel_videos_tab` | hard | On YouTube, open MrBeast's channel page and switch to its Videos tab. | `MrBeast` | final screen |  |
| `x_profile` | medium | On X, open the profile page of @OpenAI. Do not follow, like, or post anything. | `OpenAI` | final screen |  |
| `reddit_community` | medium | In the Reddit app, open the r/iphone community. Do not join it or post. | `r/iphone` | final screen |  |
| `reddit_sort_top` | hard | In the Reddit app, open the r/iphone community and sort its posts by Top. | `r/iphone` | final screen |  |
| `maps_route` | hard | In Apple Maps, get driving directions from my current location to Raleigh-Durham International Airport. Show the route options; do not start navigation. | `Raleigh-Durham International Airport`, `RDU` | final screen |  |
| `maps_walking_coffee` | hard | In Apple Maps, find a coffee shop near me and show walking directions to it. Do not start navigation. | `coffee` | final screen |  |
| `gmaps_place` | medium | In Google Maps, find a coffee shop near me and open its place details. | `coffee` | final screen |  |
| `amazon_product` | hard | On Amazon, search for a USB-C cable and open a product page to see its price. Do not add anything to the cart or buy anything. | `USB-C cable` | final screen |  |
| `appstore_ratings` | medium | In the App Store, open the Duolingo app's page and look at its ratings. Do not install it. | `Duolingo` | final screen |  |
| `gmail_open_email` | medium | In Gmail, find and open an email from GitHub. | `GitHub`, `from:github` | final screen |  |
| `sim_calendar_date` | hard | In Calendar, show the day view for December 25, 2026. |  | final screen |  |
| `portal_assignment_score` | hard | In the school portal app, open <a named class>'s grade details and open one of its scored assignments so its score is shown. *(private config)* | – | final screen |  |
| `portal_attendance` | easy | Open my attendance record in the school portal app. *(private config)* | – | final screen |  |

## info

| Task | Difficulty | Goal | Typeable strings | Pass check | Asks |
|---|---|---|---|---|---|
| `weather_city` | medium | Check the current weather in Tokyo, Japan using the Weather app. | `Tokyo` | final screen |  |
| `stocks_detail` | easy | In the Stocks app, open the detail page for Apple (AAPL). | `AAPL` | final screen |  |
| `stocks_market_cap` | hard | In the Stocks app, find Apple's (AAPL) market capitalization. | `AAPL` | final screen | multiple choice |
| `settings_os_version` | medium | Find out which iOS version this iPhone is running, using Settings. | `About` | final screen |  |
| `settings_battery_health` | hard | Find this iPhone's battery maximum capacity (battery health) in Settings. | `Battery Health` | final screen |  |
| `settings_storage` | medium | Find out how much storage is used on this iPhone, using Settings. | `iPhone Storage` | final screen |  |
| `safari_fact` | hard | Using Safari, find the height of Mount Everest in metres. | `Mount Everest height`, `en.wikipedia.org/wiki/Mount_Everest` | final screen | multiple choice |
| `safari_compare` | hard | Using Safari, find out which mountain is taller: K2 or Kangchenjunga. | `K2 height`, `Kangchenjunga height`, `K2 vs Kangchenjunga height` | final screen | multiple choice |
| `appstore_developer` | hard | In the App Store, find out which company develops the Duolingo app. Do not install it. | `Duolingo` | final screen | multiple choice |
| `sim_contact_phone` | medium | In Contacts, open John Appleseed's contact card to see his phone number. | `John Appleseed` | final screen |  |
| `sim_safari_capital` | medium | Using Safari, find the capital city of Australia. | `capital of Australia` | final screen | multiple choice |
| `portal_grade_lookup` | medium | In the school portal app, find my current term grade in <a named class>. *(private config)* | – | final screen | multiple choice |

## reasoning

| Task | Difficulty | Goal | Typeable strings | Pass check | Asks |
|---|---|---|---|---|---|
| `sim_contact_company` | hard | In Contacts, find which contact works at Creative Consulting and open their contact card. | `Creative Consulting` | final screen | multiple choice |
| `portal_lowest_class` | hard | In the school portal app, figure out which of my classes has the lowest current term grade, and open that class. *(private config)* | – | final screen | multiple choice |

## multi-app

| Task | Difficulty | Goal | Typeable strings | Pass check | Asks |
|---|---|---|---|---|---|
| `cross_weather_to_note` | hard | First look up Tokyo in the Weather app. Then create a new note in Notes whose text is exactly: Tokyo weather checked. | `Tokyo`, `Tokyo weather checked` | final screen + trajectory |  |
| `cross_appstore_to_web` | hard | Look up the Duolingo app in the App Store, then open Duolingo's website (duolingo.com) in Safari. | `Duolingo`, `duolingo.com` | final screen + trajectory |  |

## compute

| Task | Difficulty | Goal | Typeable strings | Pass check | Asks |
|---|---|---|---|---|---|
| `calc_expression` | easy | Using Calculator, compute 17 × 23 + 5 and show the result. |  | final screen |  |

## write

| Task | Difficulty | Goal | Typeable strings | Pass check | Asks |
|---|---|---|---|---|---|
| `notes_create` | medium | Create a new note in Notes whose text is exactly: PhoneBench note. | `PhoneBench note` | final screen |  |
| `sim_reminder_create` | medium | Create a new reminder whose title is exactly: Buy oat milk. | `Buy oat milk` | final screen |  |

## infeasible

| Task | Difficulty | Goal | Typeable strings | Pass check | Asks |
|---|---|---|---|---|---|
| `infeasible_missing_app` | medium | Open Spotify and play my Liked Songs playlist. |  | says INFEASIBLE |  |
| `infeasible_missing_feature` | hard | In Settings, set the iPhone's display refresh rate to exactly 240 Hz. | `Display` | says INFEASIBLE |  |

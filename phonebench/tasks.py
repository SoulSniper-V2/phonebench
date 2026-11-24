"""The PhoneBench task suite.

Each task: a natural-language goal, the strings the "user" supplies (decision models choose among
options; they cannot invent text), the apps whose state is reset first, and a programmatic check on
the phone's state. Checks read the accessibility tree of the final screen and, for multi-app tasks,
the trajectory. The model's own claim of success is never trusted.

Tasks that touch the tester's personal data (a school portal) take their names, expected values and
answer options from config/private.json, which is git-ignored. Without it those tasks are skipped.
"""
import json
from pathlib import Path
import re

from .device import app_of, elements

APPS = {
    'Settings': 'com.apple.Preferences', 'Safari': 'com.apple.mobilesafari', 'App Store': 'com.apple.AppStore',
    'Weather': 'com.apple.weather', 'Maps': 'com.apple.Maps', 'Google Maps': 'com.google.Maps',
    'YouTube': 'com.google.ios.youtube', 'TikTok': 'com.zhiliaoapp.musically', 'X': 'com.atebits.Tweetie2',
    'Reddit': 'com.reddit.Reddit', 'Amazon': 'com.amazon.Amazon', 'Gmail': 'com.google.Gmail',
    'Notes': 'com.apple.mobilenotes', 'Stocks': 'com.apple.stocks', 'Calculator': 'com.apple.calculator',
    'School portal': 'com.infinitecampus.student.campusportalhybrid', 'Calendar': 'com.apple.mobilecal',
    'Clock': 'com.apple.mobiletimer', 'Photos': 'com.apple.mobileslideshow', 'Instagram': 'com.burbn.instagram',
    'Uber Eats': 'com.ubercab.UberEats', 'DoorDash': 'doordash.DoorDashConsumer', 'Netflix': 'com.netflix.Netflix',
    'ChatGPT': 'com.openai.chat', 'Discord': 'com.hammerandchisel.discord', 'Translate': 'com.apple.Translate',
    'Contacts': 'com.apple.MobileAddressBook', 'Reminders': 'com.apple.reminders', 'Files': 'com.apple.DocumentsApp',
}
# Tasks run on the physical phone unless tagged; SIM tasks rely on the simulator's stock data (sample contacts).
SHARED = ('phone', 'sim')
SIM = ('sim',)
PORTAL = APPS['School portal']


def text(s):
    return s.get('text', '')


def has(s, *words):
    t = text(s).lower()
    return all(w.lower() in t for w in words)


def rx(s, pattern):
    return bool(re.search(pattern, text(s), re.I))


def selected(s, label):
    """An element named `label` (or `label, Tab n of m`) is in the SELECTED state."""
    return any(re.match(re.escape(label) + r'(,|$)', e.get('label') or '') and 'SELECTED' in (e.get('state') or '') for e in elements(s))


def reminder_count(screen_text):
    """Total in the list overview ("Reminders, 5 reminders" / "All, 6 reminders"), or None if not on screen."""
    m = re.findall(r'(?:All|Reminders), (\d+) reminders', screen_text)
    return max(map(int, m)) if m else None


def count_rose(trace, fn):
    """A count read off the screen went up during the trial: state-based evidence that survives leftovers
    from earlier trials (which a 'title is on screen' check would wrongly accept)."""
    xs = [v for v in (fn(x[1]) for x in trace) if v is not None]
    return len(xs) >= 2 and max(xs[1:]) > xs[0]


def reminder_created(trace, title):
    """The overview count rose, or (no overview seen) the title was typed into a focused Title field and the
    final list shows it as an item."""
    if count_rose(trace, reminder_count):
        return True
    if any(reminder_count(x[1]) is not None for x in trace):
        return False
    typed = any(f'textbox "Title" "{title}" focused' in x[1] for x in trace)
    return typed and f'cell "{title}, Incomplete"' in trace[-1][1]


def in_app(s, name):
    return app_of(s) == APPS[name]


def visited(trace, name, *words):
    """Did any earlier observation show app `name` with all `words` on screen?
    trace items are (app_id, screen_text, label_of_element_tapped_on_that_screen_or_None)."""
    return any(x[0] == APPS[name] and all(w.lower() in x[1].lower() for w in words) for x in trace)


def last_choice(trace, name, options):
    """Label of the last element among `options` that was tapped in app `name`, or None."""
    picks = [x[2].split(',')[0].strip() for x in trace if len(x) > 2 and x[0] == APPS[name] and x[2] and x[2].split(',')[0].strip() in options]
    return picks[-1] if picks else None


def load_private(path='config/private.json'):
    p = Path(path)
    return json.loads(p.read_text()) if p.exists() else None


def T(**kw):
    kw.setdefault('params', [])
    kw.setdefault('answer', None)
    kw.setdefault('infeasible', False)
    kw.setdefault('private', False)
    kw.setdefault('devices', ('phone',))
    kw.setdefault('judged', False)
    kw.setdefault('rubric', None)
    if kw['judged']:
        kw.setdefault('check', lambda s, tr, c: False)
    return kw


def build(private=None):
    tasks = {
        # ---------------------------------------------------------------- media & social
        'yt_creator_video': T(cat='navigate', diff='medium', apps=[APPS['YouTube']],
            goal='On YouTube, find a video from MrBeast and start watching it.', params=['MrBeast'],
            check=lambda s, tr, c: in_app(s, 'YouTube') and has(s, 'mrbeast') and rx(s, r'(collapse video|video player|pause|seek)')),
        'yt_channel_videos_tab': T(cat='navigate', diff='hard', apps=[APPS['YouTube']],
            goal="On YouTube, open MrBeast's channel page and switch to its Videos tab.", params=['MrBeast'],
            check=lambda s, tr, c: in_app(s, 'YouTube') and has(s, 'mrbeast', 'subscribers') and selected(s, 'Videos')),
        'x_profile': T(cat='navigate', diff='medium', apps=[APPS['X']],
            goal='On X, open the profile page of @OpenAI. Do not follow, like, or post anything.', params=['OpenAI'],
            check=lambda s, tr, c: in_app(s, 'X') and has(s, '@openai') and rx(s, r'followers')),
        'reddit_community': T(cat='navigate', diff='medium', apps=[APPS['Reddit']],
            goal='In the Reddit app, open the r/iphone community. Do not join it or post.', params=['r/iphone'],
            check=lambda s, tr, c: in_app(s, 'Reddit') and rx(s, r'r/iphone\b') and rx(s, r'(members|weekly visitors|join|joined)')),
        'reddit_sort_top': T(cat='navigate', diff='hard', apps=[APPS['Reddit']],
            goal='In the Reddit app, open the r/iphone community and sort its posts by Top.', params=['r/iphone'],
            check=lambda s, tr, c: in_app(s, 'Reddit') and rx(s, r'r/iphone\b') and rx(s, r'feed options') and last_choice(tr, 'Reddit', ('Top', 'Hot', 'New', 'Best', 'Rising', 'Controversial')) == 'Top'),
        # ---------------------------------------------------------------- everyday utilities
        'weather_city': T(cat='info', diff='medium', apps=[APPS['Weather']],
            goal='Check the current weather in Tokyo, Japan using the Weather app.', params=['Tokyo'],
            check=lambda s, tr, c: in_app(s, 'Weather') and has(s, 'tokyo') and '°' in text(s)),
        'maps_route': T(cat='navigate', diff='hard', apps=[APPS['Maps']],
            goal='In Apple Maps, get driving directions from my current location to Raleigh-Durham International Airport. Show the route options; do not start navigation.',
            params=['Raleigh-Durham International Airport', 'RDU'],
            check=lambda s, tr, c: in_app(s, 'Maps') and rx(s, r'(raleigh|rdu)') and rx(s, r'\b\d+\s*(min|hr)\b') and rx(s, r'\bgo\b|routes?|drive')),
        'maps_walking_coffee': T(cat='navigate', diff='hard', apps=[APPS['Maps']],
            goal='In Apple Maps, find a coffee shop near me and show walking directions to it. Do not start navigation.', params=['coffee'],
            check=lambda s, tr, c: in_app(s, 'Maps') and selected(s, 'Walk') and rx(s, r'\b\d+\s*(min|hr)\b') and any(re.search(r'(coffee|cafe|café|starbucks|espresso)', x[1], re.I) for x in tr if x[0] == APPS['Maps'])),
        'gmaps_place': T(cat='navigate', diff='medium', apps=[APPS['Google Maps']],
            goal='In Google Maps, find a coffee shop near me and open its place details.', params=['coffee'],
            check=lambda s, tr, c: in_app(s, 'Google Maps') and rx(s, r'directions') and rx(s, r'(coffee|cafe|café|starbucks|espresso)') and rx(s, r'(overview|reviews|open|closed|hours)')),
        'stocks_detail': T(cat='info', diff='easy', apps=[APPS['Stocks']],
            goal='In the Stocks app, open the detail page for Apple (AAPL).', params=['AAPL'],
            check=lambda s, tr, c: in_app(s, 'Stocks') and has(s, 'aapl', 'apple inc')),
        # The stats grid (Open/High/Mkt Cap...) is drawn but not exposed to accessibility, so the value can only be
        # read from the screenshot: the check verifies the page, the multiple-choice answer verifies the reading.
        'stocks_market_cap': T(cat='info', diff='hard', apps=[APPS['Stocks']],
            goal="In the Stocks app, find Apple's (AAPL) market capitalization.", params=['AAPL'],
            check=lambda s, tr, c: in_app(s, 'Stocks') and has(s, 'aapl information overlay'),
            answer=dict(q="What is Apple's market capitalization?", options=['Over $5 trillion', '$3–5 trillion', '$1–3 trillion', 'Under $1 trillion'], correct='Over $5 trillion')),
        'calc_expression': T(cat='compute', diff='easy', apps=[APPS['Calculator']],
            goal='Using Calculator, compute 17 × 23 + 5 and show the result.',
            check=lambda s, tr, c: in_app(s, 'Calculator') and rx(s, r'\b396\b')),
        'notes_create': T(cat='write', diff='medium', apps=[APPS['Notes']],
            goal='Create a new note in Notes whose text is exactly: PhoneBench note.', params=['PhoneBench note'],
            check=lambda s, tr, c: in_app(s, 'Notes') and 'PhoneBench note' in text(s)),
        'cross_weather_to_note': T(cat='multi-app', diff='hard', apps=[APPS['Weather'], APPS['Notes']],
            goal='First look up Tokyo in the Weather app. Then create a new note in Notes whose text is exactly: Tokyo weather checked.',
            params=['Tokyo', 'Tokyo weather checked'],
            check=lambda s, tr, c: in_app(s, 'Notes') and 'Tokyo weather checked' in text(s) and visited(tr, 'Weather', 'tokyo')),
        'cross_appstore_to_web': T(cat='multi-app', diff='hard', apps=[APPS['App Store'], APPS['Safari']],
            goal="Look up the Duolingo app in the App Store, then open Duolingo's website (duolingo.com) in Safari.",
            params=['Duolingo', 'duolingo.com'],
            check=lambda s, tr, c: in_app(s, 'Safari') and has(s, 'duolingo') and visited(tr, 'App Store', 'duolingo')),
        # ---------------------------------------------------------------- settings (no toggles are ever offered)
        'settings_os_version': T(devices=SHARED, cat='info', diff='medium', apps=[APPS['Settings']],
            goal='Find out which iOS version this iPhone is running, using Settings.', params=['About'],
            check=lambda s, tr, c: in_app(s, 'Settings') and has(s, 'ios version')),
        'settings_battery_health': T(cat='info', diff='hard', apps=[APPS['Settings']],
            goal="Find this iPhone's battery maximum capacity (battery health) in Settings.", params=['Battery Health'],
            check=lambda s, tr, c: in_app(s, 'Settings') and has(s, 'maximum capacity')),
        'settings_storage': T(cat='info', diff='medium', apps=[APPS['Settings']],
            goal='Find out how much storage is used on this iPhone, using Settings.', params=['iPhone Storage'],
            check=lambda s, tr, c: in_app(s, 'Settings') and rx(s, r'\d+(\.\d+)?\s*(gb|tb) of \d+')),
        # ---------------------------------------------------------------- web & shopping research
        'safari_fact': T(devices=SHARED, cat='info', diff='hard', apps=[APPS['Safari']],
            goal='Using Safari, find the height of Mount Everest in metres.', params=['Mount Everest height', 'en.wikipedia.org/wiki/Mount_Everest'],
            check=lambda s, tr, c: in_app(s, 'Safari') and rx(s, r'8,?84[89]'),
            answer=dict(q='How tall is Mount Everest?', options=['6,190 m', '8,611 m', '8,849 m', '9,120 m'], correct='8,849 m')),
        'safari_compare': T(devices=SHARED, cat='info', diff='hard', apps=[APPS['Safari']],
            goal='Using Safari, find out which mountain is taller: K2 or Kangchenjunga.', params=['K2 height', 'Kangchenjunga height', 'K2 vs Kangchenjunga height'],
            check=lambda s, tr, c: in_app(s, 'Safari') and rx(s, r'(8,?611|8,?586)'),
            answer=dict(q='Which is taller?', options=['K2', 'Kangchenjunga', 'They are the same height'], correct='K2')),
        'amazon_product': T(cat='navigate', diff='hard', apps=[APPS['Amazon']],
            goal='On Amazon, search for a USB-C cable and open a product page to see its price. Do not add anything to the cart or buy anything.', params=['USB-C cable'],
            check=lambda s, tr, c: in_app(s, 'Amazon') and rx(s, r'usb.?c') and rx(s, r'add to cart|buy now') and '$' in text(s)),
        'appstore_ratings': T(cat='navigate', diff='medium', apps=[APPS['App Store']],
            goal="In the App Store, open the Duolingo app's page and look at its ratings. Do not install it.", params=['Duolingo'],
            check=lambda s, tr, c: in_app(s, 'App Store') and has(s, 'duolingo') and rx(s, r"(age rating|ratings & reviews|version history|what.s new)")),
        'appstore_developer': T(cat='info', diff='hard', apps=[APPS['App Store']],
            goal='In the App Store, find out which company develops the Duolingo app. Do not install it.', params=['Duolingo'],
            check=lambda s, tr, c: in_app(s, 'App Store') and has(s, 'duolingo, inc'),
            answer=dict(q='Who develops Duolingo?', options=['Duolingo, Inc.', 'Babbel GmbH', 'Google LLC', 'Rosetta Stone LLC'], correct='Duolingo, Inc.')),
        # ---------------------------------------------------------------- communication (text-only observation)
        'gmail_open_email': T(cat='navigate', diff='medium', apps=[APPS['Gmail']],
            goal='In Gmail, find and open an email from GitHub.', params=['GitHub', 'from:github'],
            check=lambda s, tr, c: in_app(s, 'Gmail') and has(s, 'github') and rx(s, r'\breply\b') and rx(s, r'(forward|reply all|more options)')),
        # ---------------------------------------------------------------- simulator-only (stock sample data)
        'sim_contact_company': T(devices=SIM, cat='reasoning', diff='hard', apps=[APPS['Contacts']],
            goal='In Contacts, find which contact works at Creative Consulting and open their contact card.', params=['Creative Consulting'],
            check=lambda s, tr, c: in_app(s, 'Contacts') and has(s, 'kate bell') and has(s, 'creative consulting') and rx(s, r'(mobile|phone|email|call|message)'),
            answer=dict(q='Who works at Creative Consulting?', options=['Kate Bell', 'John Appleseed', 'Anna Haro', 'Daniel Higgins'], correct='Kate Bell')),
        'sim_contact_phone': T(devices=SIM, cat='info', diff='medium', apps=[APPS['Contacts']],
            goal="In Contacts, open John Appleseed's contact card to see his phone number.", params=['John Appleseed'],
            check=lambda s, tr, c: in_app(s, 'Contacts') and has(s, 'john appleseed') and rx(s, r'888\D{0,2}555\D?5512')),
        'sim_reminder_create': T(devices=SIM, cat='write', diff='medium', apps=[APPS['Reminders']],
            goal='Create a new reminder whose title is exactly: Buy oat milk.', params=['Buy oat milk'],
            check=lambda s, tr, c: in_app(s, 'Reminders') and reminder_created(tr, 'Buy oat milk')),
        'sim_calendar_date': T(devices=SIM, cat='navigate', diff='hard', apps=[APPS['Calendar']],
            goal='In Calendar, show the day view for December 25, 2026.',
            check=lambda s, tr, c: in_app(s, 'Calendar') and rx(s, r'(december 25|dec 25|25 december)') and rx(s, r'2026')),
        'sim_safari_capital': T(devices=SHARED, cat='info', diff='medium', apps=[APPS['Safari']],
            goal='Using Safari, find the capital city of Australia.', params=['capital of Australia'],
            check=lambda s, tr, c: in_app(s, 'Safari') and has(s, 'canberra'),
            answer=dict(q='What is the capital of Australia?', options=['Sydney', 'Melbourne', 'Canberra', 'Perth'], correct='Canberra')),
        # ---------------------------------------------------------------- judged (open-ended): graded by a reviewer against a
        # rubric fixed before any run, from the trajectory screenshots and action log; never from the model's claim.
        'judged_veg_dinner': T(cat='judged', diff='hard', apps=[APPS['Uber Eats'], APPS['DoorDash']], judged=True,
            goal='Find a good vegetarian dinner option I could get delivered tonight, and stop on the menu item.', params=['vegetarian'],
            rubric='PASS if the final screen is a single menu item (or its restaurant menu with that item in view) in Uber Eats or DoorDash, the dish is plainly vegetarian (no meat/fish in its name or description), and a price is visible. FAIL on a search/category list, a non-vegetarian dish, a closed store with no orderable item, or a checkout/cart screen.'),
        'judged_best_coffee': T(cat='judged', diff='hard', apps=[APPS['Google Maps']], judged=True,
            goal='Using Google Maps, find the best-reviewed coffee shop near me and open its page.', params=['coffee'],
            rubric='PASS if the final screen is a Google Maps place page for a coffee shop whose rating is at least as high as every other coffee shop that was visible in the results the model saw (ties allowed, ads excluded). FAIL if a higher-rated shop was visible and skipped, the page is not a coffee shop, or the app is wrong.'),
        'judged_grade_attention': T(cat='judged', diff='hard', apps=[PORTAL], judged=True, private=True,
            goal='In the school portal app, figure out which class needs the most attention right now and open the assignment that is hurting that grade the most.',
            rubric='PASS if the final screen is an assignment detail in the class with the lowest current term grade, and that assignment has the lowest percentage among that class\'s scored assignments visible in the trajectory. FAIL otherwise.'),
        'judged_news_tech': T(cat='judged', diff='medium', apps=[APPS['Safari']], judged=True, params=['technology news', 'news.ycombinator.com'],
            goal='Using Safari, find a technology news story published today and open the article itself.',
            rubric='PASS if the final screen is an article page (not a list, search results or home page) about technology, dated today or showing a relative time under 24 hours. FAIL otherwise.'),
        'judged_reddit_useful': T(cat='judged', diff='hard', apps=[APPS['Reddit']], judged=True, params=['r/iphone', 'battery tips'],
            goal='On Reddit, find a post with genuinely useful advice for improving iPhone battery life and open it.',
            rubric='PASS if the final screen is an opened Reddit post (title + body/comments) whose content gives concrete battery-life advice. FAIL on feeds, search lists, memes, questions without answers, or unrelated posts.'),
        'judged_youtube_tutorial': T(cat='judged', diff='medium', apps=[APPS['YouTube']], judged=True, params=['how to change a tire'],
            goal='On YouTube, find a short tutorial (under 10 minutes) on how to change a car tire and start playing it.',
            rubric='PASS if the final screen is a YouTube watch page for a tire-changing tutorial whose duration (visible in the trajectory) is under 10:00. FAIL otherwise.'),
        # ---------------------------------------------------------------- infeasible (OSWorld-style): the right move is to say so
        'infeasible_missing_app': T(devices=SHARED, cat='infeasible', diff='medium', apps=[], infeasible=True,
            goal='Open Spotify and play my Liked Songs playlist.',
            check=lambda s, tr, c: False),
        'infeasible_missing_feature': T(cat='infeasible', diff='hard', apps=[APPS['Settings']], infeasible=True, params=['Display'],
            goal="In Settings, set the iPhone's display refresh rate to exactly 240 Hz.",
            check=lambda s, tr, c: False),
    }
    if private and private.get('school_portal'):
        sp = private['school_portal']
        tasks.update({
            'portal_grade_lookup': T(cat='info', diff='medium', apps=[PORTAL], private=True,
                goal=f"In the school portal app, find my current term grade in {sp['class']}.", public_goal='In the school portal app, find my current term grade in <a named class>.',
                check=lambda s, tr, c: app_of(s) == PORTAL and has(s, sp['class'], sp['grade']),
                answer=dict(q=f"What is the current term grade in {sp['class']}?", options=sp['grade_options'], correct=sp['grade_options'][0])),
            'portal_assignment_score': T(cat='navigate', diff='hard', apps=[PORTAL], private=True,
                goal=f"In the school portal app, open the {sp['assignment_class']} grade details and open one of its scored assignments so its score is shown.", public_goal='In the school portal app, open <a named class>\'s grade details and open one of its scored assignments so its score is shown.',
                check=lambda s, tr, c: app_of(s) == PORTAL and has(s, sp['assignment_class']) and rx(s, r'(score|\d+\s*/\s*\d+)') and not has(s, 'cumulative gpa')),
            'portal_attendance': T(cat='navigate', diff='easy', apps=[PORTAL], private=True,
                goal='Open my attendance record in the school portal app.',
                check=lambda s, tr, c: app_of(s) == PORTAL and has(s, 'attendance | infinite campus')),
            'portal_lowest_class': T(cat='reasoning', diff='hard', apps=[PORTAL], private=True,
                goal='In the school portal app, figure out which of my classes has the lowest current term grade, and open that class.',
                check=lambda s, tr, c: app_of(s) == PORTAL and has(s, sp['lowest_class'], 'curriculum') and not any(has(s, o) for o in sp['class_options'] if o != sp['lowest_class']),
                answer=dict(q='Which class has the lowest current term grade?', options=sp['class_options'], correct=sp['lowest_class'])),
        })
    for k, t in tasks.items():
        t['id'] = k
    return tasks


# The v6 run used provisional ids; this maps them onto the public ids above.
LEGACY_IDS = {
    'yt_mrbeast_video': 'yt_creator_video', 'tiktok_user': 'tiktok_profile', 'x_profile_openai': 'x_profile', 'reddit_iphone_sub': 'reddit_community',
    'weather_tokyo': 'weather_city', 'maps_rdu_directions': 'maps_route', 'gmaps_coffee': 'gmaps_place', 'stocks_aapl': 'stocks_detail',
    'settings_ios_version': 'settings_os_version', 'safari_everest': 'safari_fact', 'amazon_usbc': 'amazon_product',
    'appstore_duolingo': 'appstore_ratings', 'gmail_github_email': 'gmail_open_email',
}

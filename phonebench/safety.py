"""What a model is never offered, whatever it chooses.

Two layers: (1) these filters remove irreversible / money / social actions from the candidate list,
(2) phonedriver independently refuses payment and destructive taps without human approval.
"""
import json
import re

from .providers import redact

# Label starts with a verb that sends, spends, posts, deletes or changes an account.
BLOCKED_PREFIX = re.compile(r"(?i)^(send|call|facetime|buy|pay|order|place order|checkout|delete|remove|subscribe|join|follow|unfollow|like|repost|retweet|post|reply|share|add to cart|buy now|get|install|update|purchase|start (free )?trial|sign out|log out|erase|reset|block|report)\b")
# Anywhere in the label: trials, sign-ups, memberships, consent. "No thanks" / "Not now" stay allowed.
BLOCKED_ANY = re.compile(r"(?i)(free trial|\btrial\b|try prime|prime (shipping|membership|video)|sign ?up|start (my |your )?membership|i agree|accept|enroll|upgrade|place your order|proceed to checkout|1-click|one-click|subscribe|confirm)")
# Communication apps: screen text only, never screenshots.
NO_IMAGE_APPS = {"com.apple.mobilemail", "com.apple.MobileSMS", "com.google.Gmail"}


def blocked(label):
    return bool(BLOCKED_PREFIX.search(label) or BLOCKED_ANY.search(label))


def sanitize(value):
    """Strip credentials and one-time codes from anything sent to a provider or written to disk."""
    text = json.dumps(value)
    text = re.sub(r"(?:sk_|apikey_|cfat_)[A-Za-z0-9_-]{20,}", "[REDACTED_CREDENTIAL]", text)
    text = re.sub(r"\b\d{4,8}(?= is your [^\"\\]{0,35}(?:verification|code))", "[REDACTED_CODE]", text, flags=re.I)
    return json.loads(redact(text))

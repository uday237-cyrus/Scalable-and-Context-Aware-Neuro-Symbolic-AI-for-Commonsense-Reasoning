"""query_classifier.py – Query-type and Android intent classifier.

Classifies every incoming message into one of three pipeline modes:
  - ``"scripture"``  → moral/ethical/philosophical/wisdom content only
  - ``"web"``        → real-world / current-event facts need live retrieval
  - ``"hybrid"``     → factual question with moral or philosophical context

Also detects Android device-action intents ("open WhatsApp", "call mum",
"navigate to hospital", "set alarm for 7am") and returns the intent name
and parameters so the Android client can execute them directly.
"""

from __future__ import annotations

import re
from typing import Literal, TypedDict

# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------

QueryMode = Literal["scripture", "web", "hybrid"]


class DeviceAction(TypedDict):
    action: str | None          # Android intent string or null
    parameters: dict            # intent extras / URI params


class ClassifierResult(TypedDict):
    mode: QueryMode
    device_action: DeviceAction


# ---------------------------------------------------------------------------
# Pattern Tables
# ---------------------------------------------------------------------------

# Patterns that indicate a live-web / real-world query
_WEB_PATTERNS = [
    r"\b(what'?s?\s+the\s+(weather|temperature|forecast))\b",
    r"\b(today'?s?\s+(weather|news|price|rate|score|match|result))\b",
    r"\b(current(ly)?|right\s+now|at\s+the\s+moment|as\s+of\s+today|live\s+(score|update|news))\b",
    r"\b(latest\s+(news|update|version|release|price|score))\b",
    r"\b(news\s+(about|on|regarding)|breaking\s+news|headlines)\b",
    r"\b(stock\s+(price|market)|cryptocurrency|bitcoin|exchange\s+rate|forex)\b",
    r"\b(covid|pandemic|election|war|conflict|flood|earthquake|disaster)\s+(update|news|situation|today)\b",
    r"\b(who\s+(won|is\s+winning|leads?)\s+(the\s+)?(election|match|game|race|tournament))\b",
    r"\b(score\s+of|result\s+of|winner\s+of)\s+.{3,40}\b",
    r"\b(temperature\s+in|weather\s+in|forecast\s+for)\b",
    r"\b(what\s+(happened|is\s+happening)\s+(today|yesterday|recently|now|in\s+\d{4}))\b",
    r"\b(ipl|cricket|football|nba|nfl|premier\s+league).{0,30}(score|result|today|live)\b",
]

# Patterns that are firmly scripture/moral/philosophical (never need web)
_SCRIPTURE_PATTERNS = [
    r"\b(what\s+does\s+(the\s+)?(bible|scripture|quran|torah|god|jesus|allah|proverbs)\s+say)\b",
    r"\b(is\s+it\s+(right|wrong|sinful|moral|ethical|a\s+sin)\s+to)\b",
    r"\b(should\s+i\s+(morally|ethically|in\s+god'?s?\s+eyes))\b",
    r"\b(moral(ly|ity)?|ethic(al|s)|commandment|righteousness|virtue|sin\b|holiness|repentance)\b",
    r"\b(meaning\s+of\s+life|purpose\s+of\s+life|why\s+are\s+we\s+here|what\s+is\s+love|what\s+is\s+truth)\b",
    r"\b(do\s+(we|i|you)\s+have\s+(free\s+will|a\s+soul|purpose|destiny))\b",
    r"\b(if\s+god\s+(exists?|is\s+(real|good|love))|does\s+god\s+exist|is\s+there\s+a\s+god)\b",
    r"\b(forgive(ness)?|mercy|grace|salvation|redemption|prayer|faith|believe\s+in\s+god)\b",
]

# Hybrid triggers — factual questions that also have moral dimension
_HYBRID_PATTERNS = [
    r"\b(is\s+it\s+(okay|ok|acceptable|right|wrong)\s+to\s+(use|watch|play|eat|drink))\b",
    r"\b(should\s+i\s+(quit|leave|stay|choose|pick|trust))\b",
    r"\b(moral(ly)?\s+(right|wrong|okay|acceptable))\b",
    r"\b(is\s+(social\s+media|technology|ai|science)\s+(good|bad|moral|evil|okay))\b",
    r"\b(can\s+you\s+sin\s+(with|by|through|using))\b",
    r"\b(what\s+does\s+science\s+say.{0,30}(bible|faith|god|soul|prayer))\b",
]

# ---------------------------------------------------------------------------
# Android Intent Detection
# ---------------------------------------------------------------------------

class _AndroidIntent:
    """Maps natural-language patterns to Android intent action strings."""

    _INTENTS: list[tuple[str, str, list[str]]] = [
        # (intent_action, param_key, patterns)
        (
            "android.intent.action.DIAL",
            "phone_number",
            [
                r"\b(call|phone|dial|ring)\s+(?P<target>[\w\s\-@.]+?)(\s+for\s+me)?\s*$",
                r"\bmake\s+a\s+(phone\s+)?call\s+to\s+(?P<target>[\w\s\-@.]+?)\s*$",
            ],
        ),
        (
            "android.intent.action.VIEW",
            "app_name",
            [
                r"\b(open|launch|start|run|show\s+me)\s+(?P<target>[\w\s]+?)\s*(app)?\s*$",
                r"\bgo\s+to\s+(?P<target>[\w\s]+?)\s*(app)?\s*$",
            ],
        ),
        (
            "android.intent.action.WEB_SEARCH",
            "query",
            [
                r"\b(search\s+(for|on\s+google)?|google)\s+(?P<target>.+)$",
            ],
        ),
        (
            "com.google.android.apps.maps.NAVIGATION",
            "destination",
            [
                r"\b(navigate|take\s+me|directions?)\s+to\s+(?P<target>[\w\s,\-]+?)\s*$",
                r"\bhow\s+do\s+i\s+get\s+to\s+(?P<target>[\w\s,\-]+?)\s*$",
            ],
        ),
        (
            "android.provider.AlarmClock.SET_ALARM",
            "time",
            [
                r"\b(set\s+(an?\s+)?alarm|wake\s+me\s+(up)?)\s+(at|for)\s+(?P<target>\d{1,2}[:\s]\d{0,2}\s*(am|pm)?|\d{1,2}\s*(am|pm))\b",
            ],
        ),
        (
            "android.provider.AlarmClock.SET_TIMER",
            "duration",
            [
                r"\b(set\s+(a\s+)?timer\s+for|start\s+(a\s+)?(\d+)\s*(minute|hour|second))\s+(?P<target>\d+\s*(minute|hour|second)s?)\b",
            ],
        ),
        (
            "android.media.action.IMAGE_CAPTURE",
            None,
            [
                r"\b(take\s+a?\s*(photo|picture|selfie|screenshot))\b",
                r"\bopen\s+(the\s+)?(camera)\b",
            ],
        ),
        (
            "android.intent.action.SENDTO",
            "to",
            [
                r"\b(send\s+(a\s+)?(text|sms|message|whatsapp|msg)\s+to)\s+(?P<target>[\w\s\-@.]+?)\s*$",
            ],
        ),
    ]

    def detect(self, message: str) -> DeviceAction:
        lower = message.strip().lower()
        for action, param_key, patterns in self._INTENTS:
            for pattern in patterns:
                match = re.search(pattern, lower, re.IGNORECASE)
                if match:
                    params: dict = {}
                    if param_key:
                        try:
                            params[param_key] = match.group("target").strip()
                        except IndexError:
                            pass
                    return DeviceAction(action=action, parameters=params)
        return DeviceAction(action=None, parameters={})


_android_detector = _AndroidIntent()


# ---------------------------------------------------------------------------
# Main Classifier
# ---------------------------------------------------------------------------

class QueryClassifier:
    """Classify a query into pipeline mode + optional Android device action."""

    def classify(self, message: str) -> ClassifierResult:
        lower = message.lower()

        # Check device intent first — if it's a device command, mode is web
        # (device actions often need real-world context)
        device_action = _android_detector.detect(message)

        # Scripture check
        is_scripture = any(
            re.search(p, lower, re.IGNORECASE) for p in _SCRIPTURE_PATTERNS
        )
        # Web check
        is_web = any(re.search(p, lower, re.IGNORECASE) for p in _WEB_PATTERNS)
        # Hybrid check
        is_hybrid = any(re.search(p, lower, re.IGNORECASE) for p in _HYBRID_PATTERNS)

        if is_scripture and is_web:
            mode: QueryMode = "hybrid"
        elif is_hybrid:
            mode = "hybrid"
        elif is_web:
            mode = "web"
        elif is_scripture:
            mode = "scripture"
        else:
            # Default: try scripture pipeline; web is only called explicitly
            mode = "scripture"

        return ClassifierResult(mode=mode, device_action=device_action)


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------

_classifier: QueryClassifier | None = None


def get_query_classifier() -> QueryClassifier:
    global _classifier
    if _classifier is None:
        _classifier = QueryClassifier()
    return _classifier


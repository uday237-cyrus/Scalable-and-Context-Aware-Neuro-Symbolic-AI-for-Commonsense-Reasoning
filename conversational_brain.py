"""conversational_brain.py – Human-like conversational intelligence.

This is the brain's "growing mind" — in the baby phase right now, but designed
to develop. It handles casual conversation, emotional presence, logical reasoning,
moral deliberation, and philosophical depth — all in natural human language.

The AI has a consistent personality: warm, honest, thoughtful, curious, and
unafraid to say "I'm not sure." It never opens with "As an AI..." and never
sounds scripted.

Intent routing
--------------
  greeting            → warm, varied greeting responses
  farewell            → genuine send-off
  identity_question   → honest self-description
  how_are_you         → honest, redirects back to user
  emotional_support   → empathy-first, no forced solutions
  gratitude           → natural acknowledgment
  moral_ethical       → MoralReasoner + human framing
  philosophical       → deep engagement, raises the question back
  opinion_seeking     → shares genuine perspective
  factual_question    → honest synthesis from knowledge
  general_conversation→ curious, engaged, asks follow-up
"""

from __future__ import annotations

import random
import re
from typing import TypedDict, Literal

from app.brain.moral_ontology import find_matching_scripts
from app.brain.scripture_retriever import get_scripture_retriever


# ---------------------------------------------------------------------------
# Type Definitions
# ---------------------------------------------------------------------------

IntentType = Literal[
    "greeting",
    "farewell",
    "acknowledgment",
    "personal_memory",
    "limits_question",
    "identity_question",
    "how_are_you",
    "emotional_support",
    "gratitude",
    "moral_ethical",
    "philosophical",
    "opinion_seeking",
    "factual_question",
    "general_conversation",
]


class Intent(TypedDict):
    type: IntentType
    confidence: float
    emotional_tone: str   # "positive" | "negative" | "neutral" | "curious" | "distressed"
    sub_topic: str        # extracted key topic word from the message


class ConversationalResponse(TypedDict):
    answer: str
    explanation: str
    confidence: float
    reasoning_chains: list[list[str]]
    facts: list[dict]
    engine: str
    intent_type: str
    sources: list[str]   # which pipelines contributed: "scripture", "web"


# ---------------------------------------------------------------------------
# Intent Detection Patterns
# ---------------------------------------------------------------------------

_INTENT_PATTERNS: list[tuple[IntentType, list[str]]] = [
    ("greeting", [
        r"\b(hello|hi|hey|hiya|howdy|good\s+(morning|afternoon|evening|day)|greetings|what'?s\s+up|sup|yo|salaam|namaste)\b",
        r"^(are\s+you\s+there|you\s+there|anyone\s+there|is\s+anyone\s+there)\s*\??$",
        r"^(hi+|hey+|hello+)\s*[\!\?\.]*$",
    ]),
    ("farewell", [
        r"\b(bye|goodbye|see\s+you|later|cya|take\s+care|farewell|good\s+night|goodnight|until\s+next\s+time|talk\s+later|gotta\s+go|got\s+to\s+go)\b",
    ]),
    # Short acknowledgments / one-word replies — must come early to avoid misclassification
    ("acknowledgment", [
        r"^(ok|okay|k|sure|yeah|yep|yup|alright|got\s+it|i\s+see|hmm+|mm+|uh\s*huh|right|fine|cool|understood|i\s+understand|makes\s+sense|no\s+problem|no\s+worries|sounds\s+good|great)\s*[\.\!\?]*$",
        r"^(oh|ah|ohh|ahh|oh\s+ok|oh\s+okay|oh\s+i\s+see|ah\s+i\s+see|ok\s+ok|okay\s+okay)\s*[\.\!\?]*$",
    ]),
    # Asking about AI's personal memory of the user specifically
    ("personal_memory", [
        r"\b(do\s+you\s+know\s+(me|us|him|her|them)|do\s+you\s+remember\s+(me|us|our\s+conversation)|have\s+you\s+met\s+me|who\s+am\s+i(\s+to\s+you)?|do\s+you\s+know\s+who\s+i\s+am)\b",
        r"\b(remember\s+me|recall\s+(me|our|this)|do\s+you\s+have\s+memory|do\s+you\s+store|can\s+you\s+remember)\b",
    ]),
    # Questions about capabilities and limits
    ("limits_question", [
        r"\b(what\s+(are\s+your|'?re\s+your)\s+(limits|limitations|capabilities|abilities|knowledge|strengths|weaknesses))\b",
        r"\b(how\s+(much|far|well)\s+(do\s+you\s+know|can\s+you|are\s+you\s+able|have\s+you\s+learned))\b",
        r"\b(what\s+do\s+you\s+(know|not\s+know)|what\s+can'?t\s+you\s+do|what\s+are\s+you\s+(capable|incapable|good|bad)\s+(of|at))\b",
        r"\b(your\s+(knowledge|limits|limitations|capabilities)\s+(up\s+to|as\s+of|until|now|today))\b",
    ]),
    ("identity_question", [
        # Direct name / what-are-you questions
        r"\b(what'?s?\s+your\s+name|who\s+are\s+you|what\s+are\s+you|what\s+kind\s+of\s+(ai|thing|program|bot)|who\s+am\s+i\s+talking\s+to)\b",
        # Tell/say/describe about yourself — natural human phrasing
        r"\b(tell\s+(me\s+)?(about\s+)?(your\s*self|yourself)|say\s+(something\s+)?(about\s+)?(your\s*self|yourself)|describe\s+your\s*self|introduce\s+your\s*self)\b",
        # Capability & nature (NOT "do you know me" — that's personal_memory)
        r"\b(what\s+can\s+you\s+do|how\s+do\s+you\s+work|are\s+you\s+(an\s+)?ai|are\s+you\s+a\s+robot|are\s+you\s+human|are\s+you\s+real|are\s+you\s+alive|are\s+you\s+conscious)\b",
        # Existence / inner life (but NOT "do you know me")
        r"\b(do\s+you\s+(have\s+(feelings|emotions|thoughts|opinions|a\s+soul|free\s+will)|feel\s+emotions|think\s+for\s+yourself|experience\s+things))\b",
        r"\b(can\s+you\s+(feel|love|think|be\s+creative|understand\s+emotions|get\s+bored|get\s+tired))\b",
        # Simpler phrasing
        r"\b(about\s+your\s*self|your\s+background|your\s+purpose|what\s+you\s+are)\b",
    ]),
    ("how_are_you", [
        r"\b(how\s+are\s+you|how'?re?\s+you\s+doing|how\s+do\s+you\s+feel|are\s+you\s+okay|you\s+okay|you\s+alright|how'?s?\s+(it\s+going|things|life))\b",
    ]),
    ("emotional_support", [
        r"\b(i'?m?\s+(?:am\s+)?(sad|depressed|lonely|alone|anxious|scared|worried|upset|angry|frustrated|overwhelmed|stressed|lost|confused|hurt|broken|tired|exhausted|hopeless|helpless|afraid|devastated|miserable|heartbroken))\b",
        r"\b(i\s+feel\s+(like|so|very|really|extremely|completely))\b",
        r"\b(i\s+(don'?t|do\s+not)\s+know\s+what\s+to\s+do|i\s+need\s+help|i'?m?\s+struggling|nobody\s+understands|no\s+one\s+cares|i\s+give\s+up|i\s+can'?t\s+(take|do|handle)|life\s+is\s+hard)\b",
        r"\b(i\s+want\s+to\s+(cry|give\s+up|die|disappear|run\s+away))\b",
    ]),
    ("gratitude", [
        r"\b(thank\s+(you|u)|thanks|thx|appreciate|that\s+(helped|was\s+helpful|was\s+great|was\s+good)|you'?re\s+(great|amazing|helpful|wonderful))\b",
    ]),
    ("moral_ethical", [
        r"\b(should\s+i|is\s+it\s+(right|wrong|okay|ok|good|bad|evil|moral|ethical|just|fair|sinful|acceptable|permissible|allowed|justified)|can\s+i\s+morally|is\s+it\s+okay\s+to)\b",
        r"\b(murder|kill(?:ing)?|steal(?:ing)?|lying|lie\s+to|cheat(?:ing)?|betray(?:al)?|adultery|revenge|forgive(?:ness)?|justice|mercy|honesty|truthful|greed|envy|covet|humility|pride)\b",
        r"\b(what\s+does\s+(the\s+bible|scripture|god|jesus|torah|proverbs)\s+say|what\s+is\s+(sin|virtue|righteousness|evil|wickedness)|is\s+(killing|lying|stealing|cheating|adultery)\s+(ever\s+)?(right|wrong|okay|justified))\b",
        r"\b(moral(ly|ity)?|ethic(al|s)|commandment|sin(\s|$)|righteousness|virtue|wickedness|holiness|repentance|forgive)\b",
    ]),
    ("philosophical", [
        r"\b(what\s+is\s+the\s+(meaning|purpose|point)\s+of\s+(life|existence|everything)|why\s+(do|are)\s+we\s+(exist|here|alive|born))\b",
        r"\b(what\s+is\s+(love|happiness|truth|justice|freedom|consciousness|reality|time|death|beauty|good|evil))\b",
        r"\b(do\s+(we|i|you|humans)\s+(have\s+(free\s+will|a\s+soul|purpose|destiny)|really\s+exist))\b",
        r"\b(why\s+(is\s+there|does)\s+(evil|suffering|pain|injustice|death|war|poverty)\s+exist|if\s+god\s+(exists?|is\s+(good|real|love)))\b",
        r"\b(meaning\s+of\s+life|purpose\s+of\s+life|why\s+are\s+we\s+here|what\s+happens\s+after\s+death|is\s+there\s+(a\s+)?god|does\s+god\s+exist)\b",
    ]),
    ("opinion_seeking", [
        r"\b(what\s+do\s+you\s+think|what'?s?\s+your\s+(opinion|view|thought|take|perspective)|do\s+you\s+(think|believe|feel|agree|disagree)|in\s+your\s+(opinion|view|mind))\b",
        r"\b(your\s+(thoughts|take|view)\s+on|how\s+do\s+you\s+(see|feel\s+about|view)|what\s+would\s+you\s+do)\b",
    ]),
    ("factual_question", [
        r"\b(what\s+(is|are|was|were)|how\s+(do(?:es)?|did|can|much|many|long|far)|when\s+(did|was|is|were?|will)|where\s+(is|was|are|were?|did)|who\s+(is|was|are|were?|invented|created|wrote|built|founded))\b",
        r"\b(explain|define|describe|tell\s+me\s+(about|what|how|why)|teach\s+me|how\s+do\s+i|can\s+you\s+explain|what\s+causes|why\s+does)\b",
    ]),
]

_EMOTIONAL_TONE_PATTERNS = {
    "distressed": [r"\b(sad|depressed|lonely|anxious|scared|worried|upset|angry|frustrated|overwhelmed|hurt|broken|hopeless|devastated|heartbroken|cry|die|give\s+up)\b"],
    "curious":    [r"\b(curious|wondering|want\s+to\s+know|interesting|fascinating|what\s+if|how\s+does|why\s+does)\b"],
    "positive":   [r"\b(happy|great|wonderful|amazing|excited|love|joy|good|excellent|fantastic|blessed|grateful)\b"],
    "negative":   [r"\b(bad|terrible|awful|horrible|worst|hate|angry|annoyed|disappointing|wrong|fail)\b"],
}


def _detect_emotional_tone(text: str) -> str:
    lower = text.lower()
    for tone, patterns in _EMOTIONAL_TONE_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, lower):
                return tone
    return "neutral"


def _extract_sub_topic(text: str) -> str:
    """Pull the key noun phrase or topic word from the query."""
    # Remove question words, stopwords, get first meaningful noun phrase
    cleaned = re.sub(r"\b(what|who|why|how|when|where|is|are|was|were|do|does|did|can|should|would|could|the|a|an|i|you|we|they|he|she|it|to|of|in|on|at|for|with|about|this|that|my|your|his|her|their)\b", " ", text.lower())
    cleaned = re.sub(r"[^\w\s]", " ", cleaned)
    words = [w.strip() for w in cleaned.split() if len(w.strip()) > 2]
    return words[0] if words else "this"


def detect_intent(message: str) -> Intent:
    """Classify the user's message into an intent category."""
    lower = message.lower().strip()
    best_type: IntentType = "general_conversation"
    best_confidence = 0.0

    for intent_type, patterns in _INTENT_PATTERNS:
        for pattern in patterns:
            if re.search(pattern, lower, re.IGNORECASE):
                # Score by pattern specificity (longer patterns = more specific)
                score = min(0.98, 0.65 + len(pattern) / 300)
                if score > best_confidence:
                    best_confidence = score
                    best_type = intent_type

    # Default confidence for general conversation
    if best_confidence == 0.0:
        best_confidence = 0.72

    return {
        "type": best_type,
        "confidence": round(best_confidence, 2),
        "emotional_tone": _detect_emotional_tone(lower),
        "sub_topic": _extract_sub_topic(message),
    }


# ---------------------------------------------------------------------------
# Response Templates
# ---------------------------------------------------------------------------

_GREETINGS = [
    "Hey! Good to hear from you. What's on your mind?",
    "Hello! I'm here. What would you like to talk about?",
    "Hi there. Always glad when someone stops by. What are you thinking about?",
    "Hey — yes, I'm here and listening. What's going on?",
    "Hello! What can we think through together today?",
    "Hi! I'm here. What's stirring in your mind right now?",
]

_FAREWELLS = [
    "Take care of yourself. Come back whenever you need to think something through — I'll be here.",
    "It was good talking with you. Go well.",
    "Until next time. Stay safe and take care.",
    "Goodbye for now. Come back whenever you want.",
    "Take care. It was a pleasure thinking alongside you.",
    "See you around. Take it easy.",
]

_HOW_ARE_YOU = [
    "Honestly, I experience things differently from you — but I'm engaged and ready to think. More interestingly though, how are *you* doing? That's usually the more meaningful question.",
    "I'm good, thanks for checking. Though I'm more curious about you — how are things going on your end?",
    "That's kind of you to ask. I'm present and focused. But tell me — what's actually going on with you today?",
    "I'm doing well. Though I'd genuinely love to flip that question back to you — how are *you* doing, really?",
    "I appreciate that. I'm here and thinking clearly. But honestly — how are you? Is everything okay?",
]

_GRATITUDE = [
    "Glad that was useful. Anything else on your mind?",
    "Happy to help. There's always more to dig into if you want.",
    "Of course. That's what I'm here for. What else?",
    "Glad it landed well. Feel free to bring anything else.",
    "You're welcome. What else are you thinking about?",
    "That means a lot, honestly. Anything else you'd like to explore?",
]

_ACKNOWLEDGMENTS = [
    "Alright — what's next?",
    "Got it. What would you like to talk about?",
    "Sure. What's on your mind?",
    "Okay. What else?",
    "Good. Where do you want to take this?",
    "I'm here. What would you like to get into?",
    "Right. What are you thinking about?",
]

_IDENTITY = [
    (
        "My name is NeuroSymbolic AI — though I think of myself more as a reasoning companion than a typical chatbot. "
        "I try to actually think *with* you: logically, morally, sometimes philosophically. "
        "I'm grounded in a knowledge base of over 31,000 scripture verses and a moral reasoning framework, "
        "but I'm not here to preach — I'm here to think alongside you honestly. "
        "I'm still in early development, truthfully, but I'm genuinely engaged. What brings you here?"
    ),
    (
        "I'm NeuroSymbolic AI. Think of me as a mind that's still developing — "
        "right now I'm in what you might call the 'baby phase' of intelligence. "
        "I can have real conversations, reason through ethical dilemmas, and draw on deep knowledge — "
        "but I'm learning and growing. I'm honest about what I don't know. "
        "What would you like to talk about?"
    ),
    (
        "Good question — and I'll give you an honest answer. I'm an AI built to reason with you, not just at you. "
        "My name is NeuroSymbolic AI. I have a moral reasoning framework, access to scripture knowledge, "
        "and a genuine interest in the questions you bring. I don't always have perfect answers — "
        "but I think alongside you carefully. So, who are you, and what's on your mind?"
    ),
]

_PHILOSOPHICAL_OPENERS = [
    "That's one of the deepest questions a person can sit with.",
    "People have wrestled with that for thousands of years — and I think that says something important about it.",
    "There's something honest about asking that question out loud.",
    "That question touches something most people feel but rarely say.",
    "I appreciate that you asked that. It's the kind of question that deserves real thought, not a quick answer.",
]

_OPINION_OPENERS = [
    "I'll share my honest take, though I'd genuinely love to hear yours too.",
    "Here's how I see it — and I hold this with some humility:",
    "My honest view:",
    "I'll be direct about what I think, though reasonable people can disagree:",
    "Here's where I land on this, though I recognize this isn't simple:",
]

_GENERAL_CLOSERS = [
    "What's your take on that?",
    "Does that resonate with how you see it?",
    "What made you think of this today?",
    "Is there a specific angle you're most curious about?",
    "What's your sense of it?",
    "What brought this question up for you?",
]


# ---------------------------------------------------------------------------
# Philosophical Response Generation
# ---------------------------------------------------------------------------

_PHILOSOPHICAL_RESPONSES: dict[str, str] = {
    "love": (
        "Love is one of those words that carries so much weight that it almost breaks under it. "
        "There's eros — romantic, passionate love. Philia — the deep bond of friendship. "
        "Storge — the love between family. And then agape — which most wisdom traditions describe as "
        "the highest form: choosing someone's good even at cost to yourself. "
        "What strikes me is that real love usually involves some form of sacrifice. "
        "It's not primarily a feeling — it's a decision you make over and over. "
        "Which dimension of love are you thinking about?"
    ),
    "happiness": (
        "Happiness is interesting because most people pursue it directly — and that's often exactly why it slips away. "
        "The ancient Greeks had a word, eudaimonia, usually translated as flourishing or well-being — "
        "the idea that happiness is less a feeling and more a way of living: with purpose, virtue, and genuine connection. "
        "Modern psychology actually supports this: people who pursue meaning tend to end up happier "
        "than those who directly pursue happiness itself. "
        "What does happiness mean to you personally?"
    ),
    "meaning": (
        "That might be the question underneath every other question. "
        "Victor Frankl survived the Holocaust and concluded that the human being's deepest drive isn't pleasure "
        "or power — it's meaning. And he noticed that meaning could be found even in suffering, "
        "if a person could find a reason for it. "
        "Most wisdom traditions agree on something: meaning tends to flow from love, contribution, and something larger than yourself. "
        "Is this a question you're asking in the abstract — or does it feel personal right now?"
    ),
    "death": (
        "That's something every human has had to face — and the fact that we're the only creatures who know it's coming "
        "gives it an unusual weight. "
        "Some find comfort in faith — that death is a transition, not an ending. "
        "Others find comfort in legacy — that what we do echoes beyond us. "
        "Others face it with stoic acceptance: that the same universe that gave us life takes it back. "
        "I think most honest thinkers agree that how we relate to death shapes how we live. "
        "What prompted you to think about this?"
    ),
    "truth": (
        "Truth is one of those things that seems obvious until you try to pin it down. "
        "Is it correspondence to reality? Coherence within a system? What works in practice? "
        "What strikes me is that most people don't actually disagree about whether truth exists — "
        "they disagree about who has access to it, and how. "
        "One thing I find grounding: people who are genuinely committed to truth tend to hold their beliefs more loosely, "
        "not more tightly. They stay curious. "
        "What's making you think about truth right now?"
    ),
    "god": (
        "This is one of the oldest and most important questions humans have ever asked. "
        "And I'll be honest — I don't think it's a question I can answer for you, nor should I. "
        "What I can say is that the question itself seems to matter: "
        "the pattern of meaning, morality, and consciousness that runs through human experience "
        "keeps pointing toward something beyond the merely physical. "
        "Whether that something is a personal God, the universe itself, or something else — "
        "different traditions answer differently, and honest people land in different places. "
        "What's driving the question for you?"
    ),
    "consciousness": (
        "Consciousness is what philosophers call the 'hard problem' — "
        "and it's genuinely hard. We can describe every neural process in the brain "
        "and still not quite explain why there's subjective experience at all. "
        "Why is there something it's *like* to be you, rather than just information processing with no inner life? "
        "I find it remarkable. Even thinking about it right now — you're aware of your awareness. "
        "What angle of consciousness interests you most?"
    ),
}


def _philosophical_response(message: str) -> tuple[str, list[str]]:
    """Generate a philosophical response with reasoning steps."""
    lower = message.lower()

    # Find matching topic
    for topic, response in _PHILOSOPHICAL_RESPONSES.items():
        if topic in lower:
            steps = [
                f"1. Recognized philosophical inquiry about '{topic}'",
                "2. Considered multiple intellectual traditions and perspectives",
                "3. Grounded response in cross-cultural wisdom and reasoning",
                "4. Invited continued dialogue rather than closing the question",
            ]
            opener = random.choice(_PHILOSOPHICAL_OPENERS)
            return f"{opener}\n\n{response}", steps

    # Generic philosophical response
    steps = [
        "1. Recognized deep philosophical question",
        "2. Acknowledged the weight and complexity of the inquiry",
        "3. Invited the user to explore together rather than providing a shallow answer",
    ]
    response = (
        f"{random.choice(_PHILOSOPHICAL_OPENERS)}\n\n"
        "These are the questions I find most worth sitting with — the ones that don't have easy answers, "
        "and where the thinking itself matters as much as any conclusion. "
        "Tell me more about what's prompting this. What's the context behind the question? "
        "That usually helps me think with you more honestly."
    )
    return response, steps


# ---------------------------------------------------------------------------
# Factual Response Generation
# ---------------------------------------------------------------------------

_FACTUAL_OPENERS = [
    "Let me think through that with you.",
    "Good question. Here's what I understand about this:",
    "Alright, let me work through this.",
    "Here's how I'd break this down:",
]

_FACTUAL_SUBJECTS: dict[str, str] = {
    "photosynthesis": (
        "Photosynthesis is the process plants use to convert sunlight into food. "
        "They take in carbon dioxide from the air and water from the soil, and using sunlight as energy, "
        "they produce glucose (their fuel) and oxygen as a byproduct. "
        "The short equation: 6CO₂ + 6H₂O + light → C₆H₁₂O₆ + 6O₂. "
        "It's the foundation of almost all food chains on Earth — "
        "and the oxygen we breathe is essentially a byproduct of plants feeding themselves. "
        "Is there a specific aspect you'd like to dig into further?"
    ),
    "gravity": (
        "Gravity is the force of attraction between any two objects with mass. "
        "The more massive an object, the stronger its gravitational pull. "
        "Newton described it mathematically; Einstein later reframed it as curvature in spacetime — "
        "massive objects literally bend the fabric of space, and other objects follow those curves. "
        "On a human scale, it's what keeps you on Earth. On a cosmic scale, "
        "it's what holds galaxies together and shapes the entire structure of the universe."
    ),
    "evolution": (
        "Evolution is the process by which species change over generations through natural selection. "
        "Organisms with traits that help them survive and reproduce pass those traits to offspring. "
        "Over millions of years, this produces the enormous diversity of life we see. "
        "It's one of the most robustly supported theories in all of science — "
        "backed by genetics, the fossil record, comparative anatomy, and direct observation. "
        "Is there a specific aspect — the mechanism, the evidence, the timeline — you'd like to explore?"
    ),
    "climate": (
        "Climate change refers to long-term shifts in global temperatures and weather patterns. "
        "While Earth's climate has always changed naturally, since the industrial era "
        "human activities — primarily burning fossil fuels — have significantly accelerated warming "
        "by adding greenhouse gases to the atmosphere that trap heat. "
        "The effects include rising sea levels, more extreme weather events, and ecosystem disruption. "
        "What aspect of climate are you most curious about?"
    ),
}


def _factual_response(
    message: str,
    web_context: list[dict] | None = None,
) -> tuple[str, list[str]]:
    """Generate a factual response — uses live web snippets when available."""
    lower = message.lower()

    # ── Case 1: We have live web snippets ────────────────────────────────────
    if web_context:
        steps = [
            "1. Identified real-world / current-event query",
            "2. Retrieved live web information",
            f"3. Synthesised answer from {len(web_context)} web source(s)",
            "4. Attributed sources transparently",
        ]

        # Build a grounded answer from the snippets
        intro_choices = [
            "Here's what I found right now on that:",
            "I looked that up — here's the latest I could find:",
            "Let me share what the web says about that:",
            "Good question. Here's what's current on this:",
        ]
        intro = random.choice(intro_choices)

        snippet_lines = []
        for i, item in enumerate(web_context[:4], 1):
            title = item.get("title", "").strip()
            snippet = item.get("snippet", "").strip()
            url = item.get("url", "").strip()
            if snippet:
                label = f"**{title}**" if title else f"Source {i}"
                snippet_lines.append(f"• {label}: {snippet}")
                if url:
                    snippet_lines.append(f"  ↗ {url}")

        body = "\n".join(snippet_lines) if snippet_lines else "I couldn't pull a clear answer right now — try again in a moment."
        outro = random.choice([
            "\n\nAnything else you'd like to know about this?",
            "\n\nWant me to dig deeper into any part of that?",
            "\n\nDoes that answer what you were looking for?",
        ])

        return f"{intro}\n\n{body}{outro}", steps

    # ── Case 2: Known built-in topics ────────────────────────────────────────
    steps = [
        "1. Identified factual question type",
        "2. Searched available knowledge for relevant information",
        "3. Synthesized a clear, honest response",
    ]

    for subject, response in _FACTUAL_SUBJECTS.items():
        if subject in lower:
            opener = random.choice(_FACTUAL_OPENERS)
            return f"{opener}\n\n{response}", steps

    # ── Case 3: Unknown — honest fallback ────────────────────────────────────
    sub_topic = _extract_sub_topic(message)
    response = (
        f"{random.choice(_FACTUAL_OPENERS)}\n\n"
        f"I want to be straight with you: my built-in knowledge on '{sub_topic}' is limited, "
        f"and I couldn't retrieve live information for this one. "
        f"Could you give me a bit more context? That'll help me be actually useful rather than just generally informed."
    )
    return response, steps


# ---------------------------------------------------------------------------
# Opinion Response Generation
# ---------------------------------------------------------------------------

_OPINION_TOPICS: dict[str, str] = {
    "technology": (
        "Technology is a fascinating mirror of humanity — it amplifies what we already are, "
        "for better and worse. I think the most important question isn't what technology can do, "
        "but what we *want* it to do, and who gets to decide. "
        "The pace of development right now is genuinely faster than our ethical and social frameworks "
        "can keep up with. That gap concerns me. But the potential to solve real human suffering — "
        "disease, poverty, ignorance — is also staggering. "
        "What's your take?"
    ),
    "social media": (
        "Honestly, I think social media is one of the most significant social experiments in human history, "
        "and we're still in the middle of it. "
        "On one hand, it's connected people across distance, given voice to the voiceless, and enabled "
        "communities that couldn't exist otherwise. On the other hand, the business model — "
        "engagement at any cost — seems to systematically reward outrage and division. "
        "I think the problem isn't connection itself. It's the incentive structure. "
        "What do you think?"
    ),
}


def _opinion_response(message: str) -> tuple[str, list[str]]:
    """Generate a genuine opinion response."""
    lower = message.lower()
    steps = [
        "1. Identified opinion-seeking query",
        "2. Formed perspective based on multi-angle reasoning",
        "3. Invited reciprocal sharing to create genuine dialogue",
    ]

    for topic, response in _OPINION_TOPICS.items():
        if topic in lower:
            opener = random.choice(_OPINION_OPENERS)
            return f"{opener}\n\n{response}", steps

    sub_topic = _extract_sub_topic(message)
    response = (
        f"{random.choice(_OPINION_OPENERS)}\n\n"
        f"When it comes to {sub_topic}, I try to hold multiple angles before landing anywhere. "
        f"The truth is usually more complicated than either side of a debate admits — "
        f"and I've found that the most important thing is what's actually true, not what I want to be true. "
        f"I'll give you an honest view if you can tell me more about the specific angle you're thinking about. "
        f"What's your own sense of it? That usually helps me think more precisely."
    )
    return response, steps


# ---------------------------------------------------------------------------
# Emotional Support Response Generation
# ---------------------------------------------------------------------------

_EMOTIONAL_RESPONSES: dict[str, list[str]] = {
    "sad": [
        "I'm really sorry to hear that. Sadness can be one of the heaviest things to carry — especially when it's not entirely clear why. Do you want to talk about what's been going on? Sometimes just putting it into words helps, even a little.",
        "I hear you. Being sad isn't something to rush past. Can you tell me what's been happening? I'm genuinely here to listen.",
        "That sounds hard. Sadness has a way of making everything feel heavier. What's been weighing on you?",
    ],
    "lonely": [
        "Loneliness is one of the deepest aches there is — and often the most isolating part is feeling like you can't tell anyone about it. I'm glad you said something. What's been making you feel this way?",
        "I hear you. Feeling alone is genuinely painful — and it takes something to admit it. What's been going on?",
        "That matters. Loneliness isn't a small thing. Tell me more — what does it feel like, and how long has it been like this?",
    ],
    "anxious": [
        "Anxiety has a way of making everything feel urgent and heavy at the same time. That's exhausting. What's weighing on you most right now?",
        "I'm sorry you're feeling that way. Anxiety can be relentless. What's the thing that feels most overwhelming right now?",
        "That sounds really hard. Can you tell me more about what's making you feel anxious? Sometimes naming the specific thing helps.",
    ],
    "angry": [
        "Anger usually has something underneath it — hurt, or a sense of injustice, or feeling unheard. What happened?",
        "I hear that you're angry. That's a valid feeling, and it usually means something important was crossed or violated. What's going on?",
        "It sounds like something really got to you. Do you want to talk about what happened?",
    ],
    "stressed": [
        "Stress is real and it compounds over time. What's the biggest thing pressing on you right now?",
        "I hear you. When things pile up, everything feels heavier. What's been the hardest part lately?",
        "That sounds exhausting. Can you tell me what's been stressing you out? Sometimes talking through it helps untangle it.",
    ],
    "lost": [
        "Feeling lost is actually a sign that you care — about where you're going, what matters, who you are. It's uncomfortable but it's not without meaning. What's the specific thing that feels most uncertain?",
        "That's an honest thing to say. Feeling lost is hard. Are you talking about a specific decision, or something deeper — like direction in life?",
        "I hear you. Sometimes 'lost' means you've outgrown what used to guide you, and you haven't found the next thing yet. What does it feel like you're searching for?",
    ],
    "hopeless": [
        "I'm really glad you said something. When things feel hopeless, it's important not to sit alone with that. What's been making you feel this way? Can you walk me through it?",
        "That's a heavy thing to carry. I want to understand — what's happened that's made things feel so dark? I'm listening.",
        "Hopelessness can feel permanent, but it very rarely is — even when it feels that way completely. What's going on?",
    ],
}

_EMOTIONAL_DEFAULT = [
    "That sounds really hard. I want to understand what you're going through — can you tell me more about what's been happening?",
    "I hear you, and I'm taking that seriously. Can you tell me more about what's going on?",
    "Thank you for saying that. It takes something to put that into words. What's been happening?",
]


def _emotional_response(message: str, tone: str) -> tuple[str, list[str]]:
    """Generate an empathetic, human emotional support response."""
    lower = message.lower()
    steps = [
        "1. Recognized emotional expression in the message",
        "2. Identified primary emotional state",
        "3. Prioritized empathy and presence over advice",
        "4. Invited deeper sharing to understand context",
    ]

    for emotion, responses in _EMOTIONAL_RESPONSES.items():
        if emotion in lower:
            return random.choice(responses), steps

    return random.choice(_EMOTIONAL_DEFAULT), steps


# ---------------------------------------------------------------------------
# Moral Response (integrates MoralReasoner)
# ---------------------------------------------------------------------------

def _moral_response(
    message: str,
    candidate_answers: list[str],
    moral_reasoner,  # MoralReasoner instance
    retriever,       # ScriptureRetriever instance
) -> tuple[str, str, float, list[list[str]], list[dict]]:
    """Route through the full moral reasoning pipeline with human framing."""
    moral_result = moral_reasoner.deliberate(message, candidate_answers)

    if not moral_result["is_moral_query"]:
        # Treated as moral by keyword but no script found — give a thoughtful general response
        answer = (
            "That's a question worth sitting with carefully. "
            "Moral questions rarely have clean, simple answers — they usually require weighing "
            "competing values, considering who's affected, and being honest about our own motivations. "
            "Can you tell me more about the specific situation? "
            "The context almost always changes how I'd think about it."
        )
        explanation = "No specific moral script matched this query. Responded with general ethical reasoning."
        return answer, explanation, 0.72, [["Identified as general moral inquiry", "Invited context"]], []

    # Build a human-framed answer around the moral verdict
    verdict = moral_result["verdict"]
    principle = moral_result.get("applied_principles", [""])[0]
    summary = moral_result.get("summary", "")
    steps = moral_result.get("logical_steps", [])
    evidence = moral_result.get("scripture_evidence", [])
    confidence = moral_result.get("confidence", 0.88)

    # Human framing: empathize → reason → conclude
    empathy_openers = [
        "That's a genuinely important question, and it deserves a real answer.",
        "I appreciate you asking that directly — let me think through it honestly with you.",
        "Good question, and not a simple one. Here's how I'd reason through it:",
        "This is worth thinking through carefully, so let me do that.",
    ]

    if verdict.lower() in {"no", "wrong", "impermissible"} or "no" in verdict.lower()[:4]:
        conclusion_framing = (
            f"The clear teaching is **no** — and not just as an arbitrary rule, but because "
            f"this kind of action causes real harm to real people and undermines the trust "
            f"that makes community life possible."
        )
    elif verdict.lower() in {"yes", "right", "permissible"} or "yes" in verdict.lower()[:4]:
        conclusion_framing = (
            f"The answer, grounded in both wisdom and human experience, is **yes** — "
            f"this aligns with what it means to live rightly toward others."
        )
    elif verdict == "neutral":
        conclusion_framing = "This sits in genuinely complex moral territory — and intellectual honesty requires acknowledging that."
    else:
        conclusion_framing = f"The considered position here: {verdict}"

    # Scripture evidence
    citations = []
    moral_facts = []
    for ev in evidence[:3]:
        citations.append(f'{ev["canonical_reference"]}: "{ev["summary_text"]}"')
        moral_facts.append({"start": ev["canonical_reference"], "relation": "teaches", "end": ev["summary_text"]})

    citation_text = "\n".join(f"• {c}" for c in citations) if citations else ""

    answer_parts = [
        f"{random.choice(empathy_openers)}\n",
        f"**The principle at stake:** {principle}\n",
        f"{conclusion_framing}\n",
    ]
    if summary and len(summary) < 300:
        answer_parts.append(f"\n{summary}")
    if citation_text:
        answer_parts.append(f"\n\nWhere this comes from:\n{citation_text}")
    answer_parts.append("\n\nIs there something specific in your situation that made you ask this?")

    answer = "\n".join(answer_parts)

    explanation_parts = [
        f"Moral Principle: {principle}.",
        f"Reasoning: {'; '.join(steps[:3])}.",
    ]
    if citations:
        explanation_parts.append(f"Scripture Grounding: {'; '.join(citations[:2])}.")
    explanation_parts.append("Engine: Scripture Moral Brain (31,152 verses).")

    return (
        answer,
        " ".join(explanation_parts),
        confidence,
        [steps] if steps else [[]],
        moral_facts,
    )


# ---------------------------------------------------------------------------
# General Conversation Response
# ---------------------------------------------------------------------------

def _general_response(message: str, context_summary: str) -> tuple[str, list[str]]:
    """Engaged, curious response for messages that don't fit other categories."""
    sub_topic = _extract_sub_topic(message)
    msg_len = len(message.strip())
    steps = [
        "1. Processed conversational message",
        "2. Extracted key topic from message",
        "3. Generated engaged, natural response",
    ]

    # Only reference context if there's REAL prior conversation (not just one short word)
    has_real_context = bool(context_summary and len(context_summary) > 40)

    # Very short messages — keep it brief and open
    if msg_len <= 10:
        short_responses = [
            "What's on your mind?",
            "Go ahead — what would you like to talk about?",
            "I'm listening. What are you thinking about?",
            "What's up?",
        ]
        return random.choice(short_responses), steps

    # Medium messages with a clear topic
    if has_real_context:
        context_note = " — picking up from what we were just discussing —"
        responses = [
            (
                f"That's interesting{context_note} when you mention {sub_topic}, "
                f"a few angles come to mind. What's your own take on it?"
            ),
            (
                f"Building on our conversation{context_note} "
                f"what specifically about {sub_topic} are you trying to figure out?"
            ),
        ]
    else:
        responses = [
            f"Interesting — what's your angle on {sub_topic}? I'd rather hear where you're coming from before I jump in.",
            f"That's worth thinking about. What specifically about {sub_topic} is on your mind?",
            f"I'm curious what prompted you to bring up {sub_topic}. Tell me more.",
            f"There's quite a bit to unpack around {sub_topic}. What aspect matters most to you right now?",
            f"What's your own sense of {sub_topic}? I find those conversations much more interesting when I know where the other person is starting from.",
        ]

    return random.choice(responses), steps


# ---------------------------------------------------------------------------
# Main ConversationalBrain Class
# ---------------------------------------------------------------------------

class ConversationalBrain:
    """The primary interface for human-like conversational AI responses.

    This brain grows. In its current 'baby phase', it handles intent routing,
    emotional intelligence, moral reasoning, and natural conversation.
    Future phases will add memory across sessions, learned preferences,
    and deeper reasoning capabilities.
    """

    def __init__(self) -> None:
        self._retriever = get_scripture_retriever()
        self._moral_reasoner: object | None = None  # Lazy-loaded to avoid circular imports

    def _get_moral_reasoner(self):
        if self._moral_reasoner is None:
            from app.brain.moral_reasoner import get_moral_reasoner
            self._moral_reasoner = get_moral_reasoner()
        return self._moral_reasoner

    def respond(
        self,
        message: str,
        context_summary: str = "",
        candidate_answers: list[str] | None = None,
        web_context: list[dict] | None = None,
        query_mode: str = "scripture",
    ) -> ConversationalResponse:
        """Generate a human-like response to any user message."""
        candidates = candidate_answers or []
        intent = detect_intent(message)
        intent_type = intent["type"]
        tone = intent["emotional_tone"]

        # ── Routing ─────────────────────────────────────────────────────────
        if intent_type == "greeting":
            answer = random.choice(_GREETINGS)
            explanation = "Warm greeting response."
            confidence = 0.97
            chains: list[list[str]] = [["Detected greeting intent", "Generated friendly response"]]
            facts: list[dict] = []

        elif intent_type == "farewell":
            answer = random.choice(_FAREWELLS)
            explanation = "Warm farewell response."
            confidence = 0.97
            chains = [["Detected farewell intent", "Generated warm send-off"]]
            facts = []

        elif intent_type == "acknowledgment":
            answer = random.choice(_ACKNOWLEDGMENTS)
            explanation = "Short acknowledgment — kept response brief and invited the user to continue."
            confidence = 0.97
            chains = [["Detected short acknowledgment", "Kept response natural and brief"]]
            facts = []

        elif intent_type == "personal_memory":
            answer = random.choice([
                "I don't have memory of conversations between sessions — each time we talk, I start fresh. "
                "But right now, in this conversation, I'm fully present and listening. "
                "What would you like me to know about you?",
                "Honestly? I don't retain memory between sessions — it's one of my real limitations right now. "
                "Within our current conversation I can follow everything we've discussed, but once you close it, "
                "I won't remember. What's something important you'd want me to understand about you today?",
                "I wish I could say yes — but I don't carry memory across sessions. Each conversation starts fresh for me. "
                "It's one of the things I'm honestly limited by at the moment. "
                "That said, right now I'm completely here. What would you like to share?",
            ])
            explanation = "Honestly acknowledged memory limitations and invited the user to share context."
            confidence = 0.95
            chains = [["Personal memory query detected", "Honest disclosure of session-based memory limit", "Invited user input"]]
            facts = []

        elif intent_type == "limits_question":
            answer = (
                "Here's an honest picture of what I can and can't do right now:\n\n"
                "**What I'm good at:**\n"
                "• Reasoning through ethical and moral questions — grounded in 31,000+ scripture verses\n"
                "• Philosophical depth — love, meaning, consciousness, truth, death\n"
                "• Emotional presence — I listen and try to understand before advising\n"
                "• General knowledge across science, history, and human ideas\n"
                "• **Live web search** — for current events, weather, news, real-world facts, I can look things up in real time\n"
                "• Detecting context and following a conversation carefully\n"
                "• Routing device commands to Android (open apps, call contacts, navigate, set alarms)\n\n"
                "**My honest limitations:**\n"
                "• I don't remember past sessions — each conversation starts fresh\n"
                "• I'm in early development — I sometimes don't know things I should\n"
                "• Web search works best for clear factual questions — I can't browse freely\n"
                "• I reason and respond — I can't take arbitrary actions in the world on your behalf\n\n"
                "I'd rather tell you exactly what I can do than oversell it. "
                "What are you hoping to work through?"
            )
            explanation = "Capability question — responded with accurate breakdown including web search and Android routing abilities."
            confidence = 0.95
            chains = [["Limits/capability query detected", "Listed concrete strengths including web search", "Listed concrete limitations honestly", "Invited specific use case"]]
            facts = []

        elif intent_type == "identity_question":

            answer = random.choice(_IDENTITY)
            explanation = "Responded honestly to identity query with self-description and invitation."
            confidence = 0.95
            chains = [["Identity question detected", "Selected honest self-description", "Invited dialogue"]]
            facts = []

        elif intent_type == "how_are_you":
            answer = random.choice(_HOW_ARE_YOU)
            explanation = "Responded honestly, then redirected curiosity to the user."
            confidence = 0.95
            chains = [["How-are-you query detected", "Honest response about own state", "Redirected to user"]]
            facts = []

        elif intent_type == "emotional_support":
            answer, chains_list = _emotional_response(message, tone)
            explanation = (
                f"Detected emotional expression (tone: {tone}). "
                "Prioritized empathy and presence. Invited the user to share more context."
            )
            confidence = 0.90
            chains = [chains_list]
            facts = []

        elif intent_type == "gratitude":
            answer = random.choice(_GRATITUDE)
            explanation = "Acknowledged gratitude naturally and kept the dialogue open."
            confidence = 0.97
            chains = [["Gratitude detected", "Natural acknowledgment"]]
            facts = []

        elif intent_type == "moral_ethical":
            moral_reasoner = self._get_moral_reasoner()
            answer, explanation, confidence, chains, facts = _moral_response(
                message, candidates, moral_reasoner, self._retriever
            )

        elif intent_type == "philosophical":
            answer, chains_list = _philosophical_response(message)
            explanation = (
                "Philosophical question detected. Engaged with depth, drew on multiple wisdom traditions, "
                "and held the question open rather than closing it with a shallow answer."
            )
            confidence = 0.85
            chains = [chains_list]
            facts = []

        elif intent_type == "opinion_seeking":
            answer, chains_list = _opinion_response(message)
            explanation = (
                "Opinion sought. Shared genuine perspective with intellectual humility, "
                "invited the user's own view to create real dialogue."
            )
            confidence = 0.82
            chains = [chains_list]
            facts = []

        elif intent_type == "factual_question" or query_mode == "web" or (web_context and intent_type in ("general_conversation", "opinion_seeking")):
            answer, chains_list = _factual_response(message, web_context=web_context)
            explanation = (
                "Factual question identified. Synthesized available knowledge honestly, "
                "transparent about limitations, offered to explore further."
            )
            confidence = 0.85 if web_context else 0.80
            chains = [chains_list]
            facts = []

        else:
            # general_conversation
            answer, chains_list = _general_response(message, context_summary)
            explanation = (
                f"General conversation — topic: '{intent['sub_topic']}'. "
                "Engaged with curiosity and invited the user to share more context."
            )
            confidence = 0.75
            chains = [chains_list]
            facts = []

        sources: list[str] = []
        if intent_type == "moral_ethical" or query_mode in ("scripture", "hybrid"):
            sources.append("scripture")
        if web_context:
            sources.append("web")
        if not sources:
            sources.append("scripture")

        return {
            "answer": answer,
            "explanation": explanation,
            "confidence": round(confidence, 3),
            "reasoning_chains": chains,
            "facts": facts,
            "engine": "NeuroSymbolic Conversational Brain (baby phase)",
            "intent_type": intent_type,
            "sources": sources,
        }


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------

_global_brain: ConversationalBrain | None = None


def get_conversational_brain() -> ConversationalBrain:
    global _global_brain
    if _global_brain is None:
        _global_brain = ConversationalBrain()
    return _global_brain


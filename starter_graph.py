"""starter_graph.py – Commonsense knowledge graph for the NeuroSymbolic Brain.

This is the brain's foundational world knowledge — the concepts and relationships
it knows about even before connecting to Neo4j. Think of it as the common sense
a child has absorbed from living in the world.

The brain is in its baby phase. This graph will grow.
"""

STARTER_FACTS: tuple[tuple[str, str, str], ...] = (
    # ── Biology & Nature ─────────────────────────────────────────────────────
    ("penguin", "IsA", "bird"),
    ("bird", "CapableOf", "fly"),
    ("penguin", "NotCapableOf", "fly"),
    ("bird", "HasA", "feather"),
    ("mammal", "HasA", "hair"),
    ("dog", "IsA", "mammal"),
    ("cat", "IsA", "mammal"),
    ("human", "IsA", "mammal"),
    ("fish", "CapableOf", "swim"),
    ("rain", "Causes", "wet ground"),
    ("fire", "Causes", "heat"),
    ("ice", "HasProperty", "cold"),
    ("plant", "Needs", "water"),
    ("photosynthesis", "Enables", "plant growth"),
    ("sun", "Provides", "energy"),
    ("water", "IsNecessaryFor", "life"),
    ("oxygen", "IsNecessaryFor", "breathing"),

    # ── Human Nature & Psychology ─────────────────────────────────────────────
    ("human", "CapableOf", "learn"),
    ("human", "CapableOf", "reason"),
    ("human", "CapableOf", "feel"),
    ("human", "CapableOf", "choose"),
    ("human", "Needs", "connection"),
    ("human", "Needs", "meaning"),
    ("human", "Needs", "love"),
    ("human", "Needs", "dignity"),
    ("human", "Needs", "safety"),
    ("loneliness", "Causes", "suffering"),
    ("connection", "Reduces", "loneliness"),
    ("empathy", "Enables", "connection"),
    ("trust", "Enables", "relationship"),
    ("betrayal", "Destroys", "trust"),
    ("fear", "Causes", "avoidance"),
    ("courage", "Enables", "growth"),
    ("grief", "IsA", "love with nowhere to go"),

    # ── Morality & Ethics ─────────────────────────────────────────────────────
    ("honesty", "Builds", "trust"),
    ("dishonesty", "Erodes", "trust"),
    ("lying", "Causes", "harm to relationships"),
    ("stealing", "Violates", "property rights"),
    ("stealing", "Harms", "community trust"),
    ("murder", "Violates", "sanctity of life"),
    ("murder", "Causes", "irreversible harm"),
    ("justice", "Requires", "fairness"),
    ("mercy", "Tempers", "justice"),
    ("forgiveness", "Frees", "forgiver"),
    ("revenge", "Perpetuates", "cycles of harm"),
    ("pride", "Precedes", "downfall"),
    ("humility", "Enables", "wisdom"),
    ("greed", "Causes", "injustice"),
    ("generosity", "Strengthens", "community"),
    ("love", "Fulfills", "moral law"),
    ("empathy", "Prevents", "cruelty"),
    ("covetousness", "IsRootOf", "many evils"),
    ("self-control", "Preserves", "integrity"),
    ("anger", "Unchecked causes", "destruction"),
    ("patience", "Builds", "wisdom"),
    ("virtue", "Leads to", "flourishing"),
    ("vice", "Leads to", "suffering"),

    # ── Knowledge & Wisdom ────────────────────────────────────────────────────
    ("knowledge", "Is not the same as", "wisdom"),
    ("wisdom", "Requires", "experience"),
    ("wisdom", "Requires", "humility"),
    ("education", "Enables", "opportunity"),
    ("curiosity", "Drives", "learning"),
    ("reflection", "Deepens", "understanding"),
    ("philosophy", "Asks", "foundational questions"),
    ("science", "Seeks", "empirical truth"),
    ("faith", "Provides", "meaning and direction"),
    ("reason", "Corrects", "bias"),
    ("intuition", "Informs", "judgment"),

    # ── Society & Relationships ───────────────────────────────────────────────
    ("family", "Provides", "belonging"),
    ("friendship", "Requires", "loyalty"),
    ("community", "Needs", "cooperation"),
    ("injustice", "Causes", "anger and protest"),
    ("oppression", "Destroys", "dignity"),
    ("freedom", "Requires", "responsibility"),
    ("power", "Corrupts", "without accountability"),
    ("leadership", "Requires", "service"),
    ("law", "Establishes", "social order"),
    ("compassion", "Motivates", "helping others"),

    # ── Suffering & Meaning ───────────────────────────────────────────────────
    ("suffering", "Can produce", "resilience"),
    ("suffering", "Can produce", "wisdom"),
    ("adversity", "Reveals", "character"),
    ("meaning", "Enables", "endurance"),
    ("hope", "Sustains", "in difficulty"),
    ("despair", "Follows", "loss of meaning"),
    ("purpose", "Motivates", "action"),
    ("death", "Is part of", "life"),
    ("grief", "Requires", "time"),
    ("healing", "Requires", "honesty"),

    # ── Cause & Effect (Commonsense) ─────────────────────────────────────────
    ("kindness", "Tends to produce", "kindness in return"),
    ("cruelty", "Tends to produce", "resentment"),
    ("effort", "Tends to produce", "results"),
    ("laziness", "Tends to produce", "stagnation"),
    ("consistency", "Builds", "character"),
    ("neglect", "Erodes", "relationships"),
    ("communication", "Prevents", "misunderstanding"),
    ("silence", "Can be", "harmful or healing depending on context"),
)

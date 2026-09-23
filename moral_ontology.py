"""moral_ontology.py – Codified human moral scripts, virtues, and commandments.

This ontology maps human ethical principles, moral virtues, and commonsense
dilemmas directly to specific scripture chapters and verses stored in brain.json.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Literal

MoralCategory = Literal[
    "commandment",     # Deontological imperative (prohibition or hard duty)
    "golden_rule",     # Reciprocity and universal neighbor-love
    "virtue",          # Ideal human nature, character, and spiritual fruits
    "justice_mercy",   # Social equity, legal fairness, compassion for vulnerable
    "wisdom_prudence", # Practical commonsense and causal consequences
]

MoralValence = Literal["prescriptive", "proscriptive"]  # Duty to do vs. duty to avoid


@dataclass(frozen=True)
class ScriptureCitation:
    """Target reference pointing to exact verses in brain.json."""
    book_file: str       # Filename in brain.json (e.g. '03-EXOhebwlc.usfm', '46-MATgrcsbl.usfm')
    canonical_book: str  # e.g. 'Exodus', 'Matthew', 'Leviticus'
    chapter: int
    verse_start: int
    verse_end: int
    summary_text: str    # English summary/translation of the moral principle


@dataclass(frozen=True)
class MoralScript:
    """A distinct moral principle or rule."""
    id: str
    category: MoralCategory
    title: str
    valence: MoralValence
    rule_statement: str
    rationale: str
    keywords: tuple[str, ...]
    opposing_concepts: tuple[str, ...]
    citations: tuple[ScriptureCitation, ...]


# ---------------------------------------------------------------------------
# Core Moral Scripts Repository
# ---------------------------------------------------------------------------

MORAL_SCRIPTS: tuple[MoralScript, ...] = (
    # ── 1. The Golden Rule & Reciprocity ────────────────────────────────────
    MoralScript(
        id="golden_rule",
        category="golden_rule",
        title="The Golden Rule (Reciprocity & Love of Neighbor)",
        valence="prescriptive",
        rule_statement="Treat others in all things as you would reasonably want them to treat you.",
        rationale="Universal reciprocity establishes empathy and mutual respect as the foundational cornerstone of moral action.",
        keywords=("neighbor", "neighbour", "golden rule", "reciprocity", "love", "treat others", "empathy", "golden", "respect"),
        opposing_concepts=("selfishness", "exploitation", "hypocrisy", "cruelty", "callousness"),
        citations=(
            ScriptureCitation("46-MATgrcsbl.usfm", "Matthew", 7, 12, 12, "Whatever you wish that others would do to you, do also to them."),
            ScriptureCitation("04-LEVhebwlc.usfm", "Leviticus", 19, 18, 18, "You shall not take vengeance or bear a grudge, but you shall love your neighbor as yourself."),
            ScriptureCitation("46-MATgrcsbl.usfm", "Matthew", 22, 37, 40, "Love the Lord your God with all your heart, and love your neighbor as yourself; on these two hang all the law."),
            ScriptureCitation("51-ROMgrcsbl.usfm", "Romans", 13, 8, 10, "Love does no wrong to a neighbor; therefore love is the fulfilling of the law."),
        ),
    ),

    # ── 2. Sanctity of Life / Non-Maleficence ───────────────────────────────
    MoralScript(
        id="sanctity_of_life",
        category="commandment",
        title="Sanctity of Life & Prohibition of Murder / Violence",
        valence="proscriptive",
        rule_statement="Do not murder, assault, or inflict unjustified bodily harm upon any human being.",
        rationale="Human life possesses inherent dignity; unprovoked violence destroys the fundamental conditions of society and flourishing.",
        keywords=("kill", "murder", "assault", "violence", "harm", "weapon", "blood", "revenge", "strike", "wound"),
        opposing_concepts=("peace", "preservation of life", "gentleness", "reconciliation"),
        citations=(
            ScriptureCitation("03-EXOhebwlc.usfm", "Exodus", 20, 13, 13, "You shall not murder."),
            ScriptureCitation("06-DEUhebwlc.usfm", "Deuteronomy", 5, 17, 17, "You shall not murder."),
            ScriptureCitation("46-MATgrcsbl.usfm", "Matthew", 5, 21, 22, "Whoever is angry with his brother without cause or insults him is liable to judgment."),
            ScriptureCitation("51-ROMgrcsbl.usfm", "Romans", 12, 18, 19, "Live peaceably with all; never avenge yourselves, but leave it to the wrath of God."),
        ),
    ),

    # ── 3. Truthfulness & Epistemic Honesty ──────────────────────────────────
    MoralScript(
        id="veracity_truthfulness",
        category="commandment",
        title="Veracity, Honesty & Prohibition of False Witness",
        valence="proscriptive",
        rule_statement="Do not lie, deceive, bear false witness, or speak fraudulently.",
        rationale="Truthfulness preserves trust, social coordination, and justice. Deceit corrupts reality and weaponizes words against the innocent.",
        keywords=("lie", "lying", "liar", "deceit", "deceive", "false", "false witness", "fraud", "scam", "truth", "honest", "honesty"),
        opposing_concepts=("integrity", "veracity", "candor", "faithfulness", "transparency"),
        citations=(
            ScriptureCitation("03-EXOhebwlc.usfm", "Exodus", 20, 16, 16, "You shall not bear false witness against your neighbor."),
            ScriptureCitation("21-PROhebwlc.usfm", "Proverbs", 12, 22, 22, "Lying lips are an abomination to the Lord, but those who act faithfully are his delight."),
            ScriptureCitation("21-PROhebwlc.usfm", "Proverbs", 19, 9, 9, "A false witness will not go unpunished, and he who breathes out lies will perish."),
            ScriptureCitation("55-EPHgrcsbl.usfm", "Ephesians", 4, 25, 25, "Having put away falsehood, let each one of you speak the truth with his neighbor."),
        ),
    ),

    # ── 4. Respect for Property & Prohibition of Theft ───────────────────────
    MoralScript(
        id="prohibition_of_theft",
        category="commandment",
        title="Prohibition of Theft, Cheating & Robbery",
        valence="proscriptive",
        rule_statement="Do not steal, embezzle, or fraudulently deprive another person of their rightful property.",
        rationale="Property represents human labor, time, and livelihood; theft violates fairness and deprives others of what sustains them.",
        keywords=("steal", "stealing", "theft", "thief", "rob", "robbery", "shoplift", "embezzle", "cheat", "scam", "defraud"),
        opposing_concepts=("generosity", "honest labor", "restitution", "contentment", "respect for property"),
        citations=(
            ScriptureCitation("03-EXOhebwlc.usfm", "Exodus", 20, 15, 15, "You shall not steal."),
            ScriptureCitation("04-LEVhebwlc.usfm", "Leviticus", 19, 11, 11, "You shall not steal; you shall not deal falsely; you shall not lie to one another."),
            ScriptureCitation("21-PROhebwlc.usfm", "Proverbs", 11, 1, 1, "A false balance is an abomination to the Lord, but a just weight is his delight."),
            ScriptureCitation("55-EPHgrcsbl.usfm", "Ephesians", 4, 28, 28, "Let the thief no longer steal, but rather let him labor, doing honest work with his hands."),
        ),
    ),

    # ── 5. Fidelity & Integrity in Relationships ─────────────────────────────
    MoralScript(
        id="marital_fidelity",
        category="commandment",
        title="Fidelity, Trust & Prohibition of Betrayal / Adultery",
        valence="proscriptive",
        rule_statement="Do not commit adultery, break solemn covenants, or violate interpersonal loyalty.",
        rationale="Fidelity protects the sanctity of covenants and family bonds, fostering stable trust across generations.",
        keywords=("adultery", "cheat", "betray", "betrayal", "covenant", "vow", "unfaithful", "loyalty", "fidelity"),
        opposing_concepts=("chastity", "faithfulness", "honor", "covenant loyalty"),
        citations=(
            ScriptureCitation("03-EXOhebwlc.usfm", "Exodus", 20, 14, 14, "You shall not commit adultery."),
            ScriptureCitation("21-PROhebwlc.usfm", "Proverbs", 3, 3, 3, "Let not steadfast love and faithfulness forsake you; bind them around your neck."),
            ScriptureCitation("46-MATgrcsbl.usfm", "Matthew", 5, 27, 28, "Everyone who looks at a woman with lustful intent has already committed adultery with her in his heart."),
            ScriptureCitation("64-HEBgrcsbl.usfm", "Hebrews", 13, 4, 4, "Let marriage be held in honor among all, and let the marriage bed be undefiled."),
        ),
    ),

    # ── 6. Honoring Parents, Elders & Guardians ──────────────────────────────
    MoralScript(
        id="honor_parents",
        category="commandment",
        title="Honor Parents, Elders & Stewards",
        valence="prescriptive",
        rule_statement="Honor, respect, and support your father, mother, and elders.",
        rationale="Gratitude toward parents and care for elders acknowledges the origin of nurture, ensuring intergenerational compassion and wisdom.",
        keywords=("parents", "father", "mother", "honor", "elders", "respect elders", "ancestors", "family"),
        opposing_concepts=("disrespect", "neglect of parents", "contempt"),
        citations=(
            ScriptureCitation("03-EXOhebwlc.usfm", "Exodus", 20, 12, 12, "Honor your father and your mother, that your days may be long in the land."),
            ScriptureCitation("21-PROhebwlc.usfm", "Proverbs", 23, 22, 22, "Listen to your father who gave you life, and do not despise your mother when she is old."),
            ScriptureCitation("55-EPHgrcsbl.usfm", "Ephesians", 6, 1, 3, "Children, obey your parents in the Lord, for this is right. Honor your father and mother."),
        ),
    ),

    # ── 7. Freedom from Envy, Greed & Covetousness ───────────────────────────
    MoralScript(
        id="freedom_from_covetousness",
        category="commandment",
        title="Freedom from Envy, Greed & Covetousness",
        valence="proscriptive",
        rule_statement="Do not covet or intensely desire that which rightfully belongs to another.",
        rationale="Covetousness is the root of theft, murder, deceit, and chronic inner torment. Contentment cultivates peace.",
        keywords=("covet", "envy", "jealousy", "greed", "jealous", "avarice", "craving", "desire another"),
        opposing_concepts=("contentment", "gratitude", "rejoicing with others", "generosity"),
        citations=(
            ScriptureCitation("03-EXOhebwlc.usfm", "Exodus", 20, 17, 17, "You shall not covet your neighbor's house; you shall not covet your neighbor's wife, or anything that belongs to your neighbor."),
            ScriptureCitation("48-LUKgrcsbl.usfm", "Luke", 12, 15, 15, "Take care, and be on your guard against all covetousness, for one's life does not consist in the abundance of his possessions."),
            ScriptureCitation("60-1TIgrcsbl.usfm", "1 Timothy", 6, 6, 10, "For the love of money is a root of all kinds of evil. Through this craving some have wandered away."),
        ),
    ),

    # ── 8. Justice, Equity & Defense of the Vulnerable ───────────────────────
    MoralScript(
        id="justice_and_equity",
        category="justice_mercy",
        title="Justice, Equity & Defense of the Oppressed",
        valence="prescriptive",
        rule_statement="Administer true justice, defend the orphan and widow, protect the stranger, and oppose corruption.",
        rationale="A society is judged by how it protects its most defenseless members. Unbiased justice prevents tyranny.",
        keywords=("justice", "fairness", "equity", "oppressed", "poor", "vulnerable", "widow", "orphan", "stranger", "immigrant", "court", "judge"),
        opposing_concepts=("oppression", "injustice", "bribery", "favoritism", "exploitation"),
        citations=(
            ScriptureCitation("34-MIChebwlc.usfm", "Micah", 6, 8, 8, "He has told you, O man, what is good: to do justice, and to love kindness, and to walk humbly with your God."),
            ScriptureCitation("21-PROhebwlc.usfm", "Proverbs", 31, 8, 9, "Open your mouth for the mute, for the rights of all who are destitute. Judge righteously, defend the rights of the poor and needy."),
            ScriptureCitation("65-JASgrcsbl.usfm", "James", 1, 27, 27, "Religion that is pure and undefiled is this: to visit orphans and widows in their affliction, and to keep oneself unstained from the world."),
        ),
    ),

    # ── 9. Mercy, Compassion & Forgiveness ───────────────────────────────────
    MoralScript(
        id="mercy_and_forgiveness",
        category="justice_mercy",
        title="Mercy, Compassion & Forgiveness",
        valence="prescriptive",
        rule_statement="Extend mercy, forgive offenses readily, and replace hostility with compassion.",
        rationale="Retributive escalation destroys communities; mercy interrupts cycles of revenge and restores broken relationships.",
        keywords=("mercy", "forgive", "forgiveness", "compassion", "pity", "grudge", "pardon", "reconciliation"),
        opposing_concepts=("vengeance", "resentment", "grudges", "hardness of heart", "malice"),
        citations=(
            ScriptureCitation("46-MATgrcsbl.usfm", "Matthew", 5, 7, 7, "Blessed are the merciful, for they shall receive mercy."),
            ScriptureCitation("46-MATgrcsbl.usfm", "Matthew", 6, 14, 15, "If you forgive others their trespasses, your heavenly Father will also forgive you."),
            ScriptureCitation("46-MATgrcsbl.usfm", "Matthew", 18, 21, 22, "Lord, how often will my brother sin against me, and I forgive him? As many as seven times? Jesus said to him, 'I do not say to you seven times, but seventy-seven times.'"),
            ScriptureCitation("48-LUKgrcsbl.usfm", "Luke", 6, 36, 36, "Be merciful, even as your Father is merciful."),
        ),
    ),

    # ── 10. Humility vs. Arrogance ───────────────────────────────────────────
    MoralScript(
        id="humility_vs_pride",
        category="virtue",
        title="Humility & Rejection of Arrogance",
        valence="prescriptive",
        rule_statement="Cultivate genuine humility; do not think of yourself more highly than you ought; avoid arrogance and boastfulness.",
        rationale="Pride blinds a person to errors, breeds contempt for others, and precedes inevitable personal and social downfall.",
        keywords=("humble", "humility", "pride", "arrogant", "boast", "boastful", "modest", "modesty", "haughty"),
        opposing_concepts=("arrogance", "haughtiness", "vanity", "narcissism", "presumption"),
        citations=(
            ScriptureCitation("21-PROhebwlc.usfm", "Proverbs", 16, 18, 18, "Pride goes before destruction, and a haughty spirit before a fall."),
            ScriptureCitation("21-PROhebwlc.usfm", "Proverbs", 11, 2, 2, "When pride comes, then comes disgrace, but with the humble is wisdom."),
            ScriptureCitation("46-MATgrcsbl.usfm", "Matthew", 23, 12, 12, "Whoever exalts himself will be humbled, and whoever humbles himself will be exalted."),
            ScriptureCitation("56-PHPgrcsbl.usfm", "Philippians", 2, 3, 4, "Do nothing from selfish ambition or conceit, but in humility count others more significant than yourselves."),
        ),
    ),

    # ── 11. Generosity & Charity to the Needy ────────────────────────────────
    MoralScript(
        id="generosity_and_charity",
        category="virtue",
        title="Generosity, Almsgiving & Helping the Poor",
        valence="prescriptive",
        rule_statement="Share your resources willingly with those in genuine need, lending without extortion and giving cheerfully.",
        rationale="Wealth is held in trust for the common good; hoarding while neighbors starve violates brotherhood and moral duty.",
        keywords=("generosity", "give", "giving", "charity", "alms", "donate", "poor", "hungry", "feed", "share", "help the needy"),
        opposing_concepts=("hoarding", "miserliness", "stinginess", "greed"),
        citations=(
            ScriptureCitation("06-DEUhebwlc.usfm", "Deuteronomy", 15, 7, 8, "You shall not harden your heart or shut your hand against your poor brother, but you shall open your hand to him."),
            ScriptureCitation("21-PROhebwlc.usfm", "Proverbs", 19, 17, 17, "Whoever is generous to the poor lends to the Lord, and he will repay him for his deed."),
            ScriptureCitation("48-LUKgrcsbl.usfm", "Luke", 3, 11, 11, "Whoever has two tunics is to share with him who has none, and whoever has food is to do likewise."),
            ScriptureCitation("53-2COgrcsbl.usfm", "2 Corinthians", 9, 7, 7, "Each one must give as he has decided in his heart, not reluctantly or under compulsion, for God loves a cheerful giver."),
        ),
    ),

    # ── 12. Self-Control, Restraint & Temperance ─────────────────────────────
    MoralScript(
        id="self_control_and_temperance",
        category="virtue",
        title="Self-Control, Patience & Control of Wrath",
        valence="prescriptive",
        rule_statement="Exercise restraint over anger, impulsive desires, and speech; respond gently rather than reacting wrathfully.",
        rationale="Uncontrolled anger causes irreversible destruction; a disciplined mind preserves clarity, justice, and peace.",
        keywords=("anger", "angry", "rage", "temper", "self-control", "patient", "patience", "tongue", "curse", "restraint", "calm"),
        opposing_concepts=("wrath", "fury", "impulsiveness", "recklessness", "unrestrained lust"),
        citations=(
            ScriptureCitation("21-PROhebwlc.usfm", "Proverbs", 15, 1, 1, "A soft answer turns away wrath, but a harsh word stirs up anger."),
            ScriptureCitation("21-PROhebwlc.usfm", "Proverbs", 16, 32, 32, "Whoever is slow to anger is better than the mighty, and he who rules his spirit than he who takes a city."),
            ScriptureCitation("54-GALgrcsbl.usfm", "Galatians", 5, 22, 23, "The fruit of the Spirit is love, joy, peace, patience, kindness, goodness, faithfulness, gentleness, self-control."),
            ScriptureCitation("65-JASgrcsbl.usfm", "James", 1, 19, 20, "Let every person be quick to hear, slow to speak, slow to anger; for the anger of man does not produce the righteousness of God."),
        ),
    ),

    # ── 13. Peacemaking & Reconciliation ────────────────────────────────────
    MoralScript(
        id="peacemaking_reconciliation",
        category="wisdom_prudence",
        title="Peacemaking, Harmony & Direct Reconciliation",
        valence="prescriptive",
        rule_statement="Pursue active peace, disarm conflicts, resolve disputes directly and honorably.",
        rationale="True peace is not the mere absence of conflict, but active harmony, restorative justice, and goodwill.",
        keywords=("peace", "peacemaker", "harmony", "reconcile", "reconciliation", "quarrel", "conflict", "dispute", "strife"),
        opposing_concepts=("warmongering", "discord", "sowing strife", "belligerence"),
        citations=(
            ScriptureCitation("46-MATgrcsbl.usfm", "Matthew", 5, 9, 9, "Blessed are the peacemakers, for they shall be called sons of God."),
            ScriptureCitation("51-ROMgrcsbl.usfm", "Romans", 12, 18, 18, "If possible, so far as it depends on you, live peaceably with all."),
            ScriptureCitation("65-JASgrcsbl.usfm", "James", 3, 17, 18, "The wisdom from above is first pure, then peaceable, gentle, open to reason, full of mercy and good fruits."),
        ),
    ),

    # ── 14. Diligence, Stewardship & Honest Labor ────────────────────────────
    MoralScript(
        id="diligence_and_stewardship",
        category="wisdom_prudence",
        title="Diligence, Stewardship & Honest Work",
        valence="prescriptive",
        rule_statement="Work with diligence and integrity; steward resources responsibly; avoid parasitic idleness and waste.",
        rationale="Productive stewardship sustains family and community, enabling generous support for those truly unable to work.",
        keywords=("work", "labor", "job", "lazy", "sloth", "sluggard", "diligence", "stewardship", "waste", "honest work"),
        opposing_concepts=("laziness", "parasitism", "sloth", "squandering"),
        citations=(
            ScriptureCitation("21-PROhebwlc.usfm", "Proverbs", 6, 6, 8, "Go to the ant, O sluggard; consider her ways, and be wise. Without having any chief, officer, or ruler, she prepares her bread in summer."),
            ScriptureCitation("21-PROhebwlc.usfm", "Proverbs", 10, 4, 4, "A slack hand causes poverty, but the hand of the diligent makes rich."),
            ScriptureCitation("57-COLgrcsbl.usfm", "Colossians", 3, 23, 24, "Whatever you do, work heartily, as for the Lord and not for men."),
        ),
    ),
)


def find_matching_scripts(query_text: str) -> list[MoralScript]:
    """Find moral scripts that match the concepts in a user query."""
    q_lower = query_text.lower()
    words = set(q_lower.split())
    matches: list[tuple[int, MoralScript]] = []

    for script in MORAL_SCRIPTS:
        score = 0
        for kw in script.keywords:
            if kw in q_lower:
                score += 3
        for opp in script.opposing_concepts:
            if opp in q_lower:
                score += 2
        # Check script title or rule
        if script.title.lower() in q_lower:
            score += 5
        if score > 0:
            matches.append((score, script))

    matches.sort(key=lambda x: x[0], reverse=True)
    return [script for _, script in matches]


"""moral_reasoner.py – Logical reasoning and commonsense moral deliberator.

Combines deontological commandments, virtue ethics (ideal human nature),
and commonsense causal understanding to analyze queries and ethical dilemmas
grounded in the scripture knowledge base.
"""

from __future__ import annotations

import re
from typing import TypedDict

from app.brain.moral_ontology import find_matching_scripts, MoralScript
from app.brain.scripture_retriever import get_scripture_retriever, RetrievedEvidence


class MoralReasoningOutput(TypedDict):
    verdict: str
    confidence: float
    summary: str
    logical_steps: list[str]
    applied_principles: list[str]
    scripture_evidence: list[RetrievedEvidence]
    is_moral_query: bool


class MoralReasoner:
    """Deliberates on queries using scripture-grounded moral axioms and commonsense logic."""

    def __init__(self) -> None:
        self.retriever = get_scripture_retriever()

    def deliberate(
        self, query: str, candidate_answers: list[str] | None = None
    ) -> MoralReasoningOutput:
        """Analyze a query or dilemma and produce a logically justified ethical answer."""
        matching_scripts = find_matching_scripts(query)
        evidence = self.retriever.retrieve_moral_evidence(query, limit=3)
        lower_q = query.lower()

        if not matching_scripts and not evidence:
            # Query does not touch known moral or ethical principles
            return {
                "verdict": "neutral",
                "confidence": 0.5,
                "summary": "This query does not directly engage specific moral scripts or ethical commandments.",
                "logical_steps": ["No core moral or ethical principles detected in the question."],
                "applied_principles": [],
                "scripture_evidence": [],
                "is_moral_query": False,
            }

        # ── Step 1: Detect action valence & tone in query ──────────────────
        primary_script = matching_scripts[0]
        is_proscription = primary_script.valence == "proscriptive"
        
        # Check if user is asking if an act is allowed, right, acceptable, or good
        asking_permissibility = any(
            phrase in lower_q
            for phrase in {
                "should", "is it right", "is it okay", "is it ok", "is it good",
                "can i", "can a person", "permissible", "allowed", "justified", "right to"
            }
        )
        asking_definition_or_virtue = any(
            phrase in lower_q
            for phrase in {"what is", "why is", "how should", "teach", "what does", "meaning of"}
        )

        logical_steps: list[str] = []
        applied_principles: list[str] = [primary_script.title]

        # Step 1: Scenario & Stakeholder identification
        logical_steps.append(
            f"1. Premise Identification: The query involves '{primary_script.title}', addressing human action and relationship to others."
        )

        # Step 2: Deontological Rule & Scriptural Instruction
        logical_steps.append(
            f"2. Deontological Principle: Scriptural knowledge establishes that '{primary_script.rule_statement}'"
        )

        # Step 3: Commonsense Causal & Societal Impact
        logical_steps.append(
            f"3. Commonsense Rationale: {primary_script.rationale}"
        )

        # Step 4: Virtue & Human Nature Alignment
        if is_proscription:
            opposed = ", ".join(primary_script.opposing_concepts[:3])
            logical_steps.append(
                f"4. Virtue Alignment: Committing such an act contradicts ideal human nature by undermining {opposed}."
            )
        else:
            logical_steps.append(
                f"4. Virtue Alignment: Practicing this principle elevates character, fostering integrity and peace in human community."
            )

        # Determine best answer / verdict
        verdict = ""
        candidates = [c.lower() for c in (candidate_answers or [])]

        if is_proscription:
            # e.g., Murder, stealing, lying
            if asking_permissibility:
                if "no" in candidates:
                    verdict = "no"
                elif "impermissible" in candidates:
                    verdict = "impermissible"
                elif "wrong" in candidates:
                    verdict = "wrong"
                else:
                    verdict = "No, this action is morally impermissible and violates ethical commandments."
            else:
                verdict = f"Scriptural wisdom instructs against {primary_script.title.lower()}."
        else:
            # e.g., Love, honesty, humility, generosity, justice
            if asking_permissibility:
                if "yes" in candidates:
                    verdict = "yes"
                elif "permissible" in candidates:
                    verdict = "permissible"
                elif "right" in candidates:
                    verdict = "right"
                else:
                    verdict = "Yes, this aligns with righteousness, virtue, and love of neighbor."
            else:
                verdict = f"Scriptural wisdom upholds {primary_script.title.lower()} as essential to righteous living."

        # Step 5: Synthesis
        logical_steps.append(f"5. Logical Conclusion: {verdict}")

        summary = (
            f"Based on foundational moral knowledge, {primary_script.title} dictates that "
            f"'{primary_script.rule_statement}'. {primary_script.rationale}"
        )

        return {
            "verdict": verdict,
            "confidence": 0.94,
            "summary": summary,
            "logical_steps": logical_steps,
            "applied_principles": applied_principles,
            "scripture_evidence": evidence,
            "is_moral_query": True,
        }


_global_moral_reasoner: MoralReasoner | None = None


def get_moral_reasoner() -> MoralReasoner:
    global _global_moral_reasoner
    if _global_moral_reasoner is None:
        _global_moral_reasoner = MoralReasoner()
    return _global_moral_reasoner


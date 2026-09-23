from __future__ import annotations

import re
from typing import Any

from app.config import get_settings
from app.knowledge.starter_graph import STARTER_FACTS

_SAFE_RELATION = re.compile(r"^[A-Z][A-Z0-9_]{0,63}$")


class Neo4jClient:
    """Neo4j gateway with an in-process graph fallback for first-run demos."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.driver: Any | None = None
        if self.settings.neo4j_enabled:
            try:
                from neo4j import GraphDatabase

                self.driver = GraphDatabase.driver(
                    self.settings.neo4j_uri,
                    auth=(self.settings.neo4j_user, self.settings.neo4j_password),
                )
                self.driver.verify_connectivity()
            except Exception:
                self.driver = None

    @property
    def source_name(self) -> str:
        return "Neo4j" if self.driver else "bundled starter graph"

    def close(self) -> None:
        if self.driver:
            self.driver.close()

    def get_related_concepts(self, concept: str, limit: int = 10) -> list[dict[str, str]]:
        normalized = concept.lower().strip()
        if not normalized:
            return []
        if self.driver:
            query = """
            MATCH (c:Concept {name: $concept})-[r]-(related:Concept)
            RETURN type(r) AS relation, related.name AS related_concept
            LIMIT $limit
            """
            with self.driver.session() as session:
                return [dict(record) for record in session.run(query, concept=normalized, limit=limit)]

        related: list[dict[str, str]] = []
        for start, relation, end in STARTER_FACTS:
            if start == normalized:
                related.append({"relation": relation, "related_concept": end})
            elif end == normalized:
                related.append({"relation": relation, "related_concept": start})
        return related[:limit]

    def add_concept_relation(self, concept_a: str, relation: str, concept_b: str) -> None:
        if not self.driver:
            raise RuntimeError("Neo4j is not connected. Configure NEO4J_URI and credentials first.")
        safe_relation = relation.upper().replace(" ", "_")
        if not _SAFE_RELATION.fullmatch(safe_relation):
            raise ValueError("Relation may contain only letters, digits, underscores, and must start with a letter.")
        query = f"""
        MERGE (a:Concept {{name: $a}})
        MERGE (b:Concept {{name: $b}})
        MERGE (a)-[:{safe_relation}]->(b)
        """
        with self.driver.session() as session:
            session.run(query, a=concept_a.lower().strip(), b=concept_b.lower().strip())


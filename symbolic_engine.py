from __future__ import annotations

from collections import deque

from app.knowledge.neo4j_client import Neo4jClient


class SymbolicReasoner:
    """Build a small query-local graph and expose auditable relationship paths."""

    def __init__(self, knowledge_client: Neo4jClient) -> None:
        self.knowledge_client = knowledge_client

    def build_local_graph(self, concepts: list[str]) -> tuple[dict[str, list[str]], list[dict[str, str]]]:
        adjacency: dict[str, list[str]] = {}
        facts: list[dict[str, str]] = []
        for concept in concepts:
            source = concept.lower()
            for related in self.knowledge_client.get_related_concepts(source):
                target = related["related_concept"].lower()
                adjacency.setdefault(source, []).append(target)
                adjacency.setdefault(target, []).append(source)
                facts.append({"start": source, "relation": related["relation"], "end": target})
        return adjacency, facts

    @staticmethod
    def _shortest_path(adjacency: dict[str, list[str]], source: str, target: str) -> list[str] | None:
        queue: deque[list[str]] = deque([[source]])
        visited = {source}
        while queue:
            path = queue.popleft()
            node = path[-1]
            if node == target:
                return path
            for neighbour in adjacency.get(node, []):
                if neighbour not in visited:
                    visited.add(neighbour)
                    queue.append([*path, neighbour])
        return None

    def infer(self, concepts: list[str]) -> dict:
        adjacency, facts = self.build_local_graph(concepts)
        nodes = sorted(adjacency)
        chains: list[list[str]] = []
        for source in concepts:
            source = source.lower()
            for target in nodes:
                if target != source:
                    path = self._shortest_path(adjacency, source, target)
                    if path and path not in chains:
                        chains.append(path)
        return {
            "graph_nodes": nodes,
            "facts": facts,
            "reasoning_chains": chains[:5],
            "knowledge_source": self.knowledge_client.source_name,
        }


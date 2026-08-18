from retrieval.hybrid_rag import (
    search_delivery_knowledge as hybrid_search_delivery_knowledge,
)


def build_engineering_tools(
    mark_source,
):
    """
    Build local tools for the
    MAQEngineeringEvidenceAgent.

    Azure DevOps MCP itself will be passed
    separately by the orchestration layer.

    This file provides Hybrid RAG only.
    """

    def search_delivery_knowledge(
        query: str,
        top_k: int = 3,
    ) -> dict:
        """
        Searches curated MAQ delivery knowledge
        using Hybrid RAG.

        Use for:
        - management guidance
        - delivery-risk interpretation
        - Power BI guidance
        - Azure guidance
        - D365 guidance
        - sprint-health guidance
        """

        mark_source(
            "MAQ Delivery Knowledge"
        )

        return (
            hybrid_search_delivery_knowledge(
                query=query,
                top_k=top_k,
            )
        )


    return [
        search_delivery_knowledge,
    ]
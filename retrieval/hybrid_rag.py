from pathlib import Path
from threading import Lock

import chromadb
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.retrievers.bm25 import BM25Retriever
from llama_index.vector_stores.chroma import ChromaVectorStore


# ---------------------------------------------------------
# Paths / configuration
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

KNOWLEDGE_PATH = (
    PROJECT_ROOT
    / "data"
    / "knowledge"
)

CHROMA_PATH = (
    PROJECT_ROOT
    / "data"
    / "chroma"
)

COLLECTION_NAME = "maq_delivery_knowledge"

EMBEDDING_MODEL = (
    "sentence-transformers/all-MiniLM-L6-v2"
)

CHUNK_SIZE = 350
CHUNK_OVERLAP = 50

SEMANTIC_TOP_K = 5
BM25_TOP_K = 5


# ---------------------------------------------------------
# Cached runtime objects
# ---------------------------------------------------------

_vector_retriever = None
_bm25_retriever = None

_initialization_lock = Lock()


# ---------------------------------------------------------
# Load Markdown knowledge
# ---------------------------------------------------------

def load_knowledge_documents():
    """
    Loads all Markdown knowledge files from:

        data/knowledge/
    """

    if not KNOWLEDGE_PATH.exists():
        raise FileNotFoundError(
            f"Knowledge directory not found: "
            f"{KNOWLEDGE_PATH}"
        )

    markdown_files = sorted(
        KNOWLEDGE_PATH.glob("*.md")
    )

    if not markdown_files:
        raise RuntimeError(
            "No Markdown knowledge files were found."
        )

    print(
        f"[HybridRAG] Found "
        f"{len(markdown_files)} knowledge files."
    )

    reader = SimpleDirectoryReader(
        input_files=[
            str(path)
            for path in markdown_files
        ],
        filename_as_id=True,
    )

    documents = reader.load_data()

    for document in documents:

        file_path = Path(
            document.metadata.get(
                "file_path",
                "unknown",
            )
        )

        document.metadata[
            "source"
        ] = "MAQ Delivery Knowledge"

        document.metadata[
            "file_name"
        ] = file_path.name

        document.metadata[
            "knowledge_type"
        ] = file_path.stem

    print(
        f"[HybridRAG] Loaded "
        f"{len(documents)} documents."
    )

    return documents


# ---------------------------------------------------------
# Chunk documents
# ---------------------------------------------------------

def build_nodes(documents):
    """
    Splits Markdown documents into retrievable
    knowledge chunks.
    """

    splitter = SentenceSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )

    nodes = splitter.get_nodes_from_documents(
        documents
    )

    print(
        f"[HybridRAG] Created "
        f"{len(nodes)} chunks."
    )

    return nodes


# ---------------------------------------------------------
# Initialize Hybrid RAG once
# ---------------------------------------------------------

def initialize_hybrid_rag(
    force_rebuild: bool = False,
):
    """
    Initializes the Hybrid RAG retrieval layer.

    The embedding model and indexes are cached so
    MAF tool calls do not rebuild them for every query.

    force_rebuild=True can be used during development
    after changing knowledge files.
    """

    global _vector_retriever
    global _bm25_retriever

    if (
        not force_rebuild
        and _vector_retriever is not None
        and _bm25_retriever is not None
    ):
        return (
            _vector_retriever,
            _bm25_retriever,
        )

    with _initialization_lock:

        if (
            not force_rebuild
            and _vector_retriever is not None
            and _bm25_retriever is not None
        ):
            return (
                _vector_retriever,
                _bm25_retriever,
            )

        print(
            "[HybridRAG] Initializing..."
        )

        documents = (
            load_knowledge_documents()
        )

        nodes = build_nodes(
            documents
        )

        CHROMA_PATH.mkdir(
            parents=True,
            exist_ok=True,
        )

        print(
            "[HybridRAG] Loading "
            "HuggingFace embedding model..."
        )

        embed_model = HuggingFaceEmbedding(
            model_name=EMBEDDING_MODEL
        )

        print(
            "[HybridRAG] Opening Chroma..."
        )

        chroma_client = (
            chromadb.PersistentClient(
                path=str(CHROMA_PATH)
            )
        )

        #
        # During initialization we rebuild
        # the collection from the current
        # Markdown knowledge base.
        #
        try:
            chroma_client.delete_collection(
                COLLECTION_NAME
            )

            print(
                "[HybridRAG] Removed previous "
                "Chroma collection."
            )

        except Exception:
            pass

        chroma_collection = (
            chroma_client.create_collection(
                COLLECTION_NAME
            )
        )

        vector_store = ChromaVectorStore(
            chroma_collection=
                chroma_collection
        )

        print(
            "[HybridRAG] Building "
            "semantic vector index..."
        )

        vector_index = VectorStoreIndex(
            nodes,
            vector_store=vector_store,
            embed_model=embed_model,
        )

        _vector_retriever = (
            vector_index.as_retriever(
                similarity_top_k=
                    SEMANTIC_TOP_K
            )
        )

        print(
            "[HybridRAG] Building BM25 index..."
        )

        _bm25_retriever = (
            BM25Retriever.from_defaults(
                nodes=nodes,
                similarity_top_k=
                    BM25_TOP_K,
            )
        )

        print(
            "[HybridRAG] Ready."
        )

        return (
            _vector_retriever,
            _bm25_retriever,
        )


# ---------------------------------------------------------
# Reciprocal Rank Fusion
# ---------------------------------------------------------

def reciprocal_rank_fusion(
    vector_results,
    bm25_results,
    top_k: int = 3,
    k: int = 60,
):
    """
    Combines semantic and lexical rankings
    using Reciprocal Rank Fusion.
    """

    fused = {}

    retrieval_sources = [
        (
            "semantic",
            vector_results,
        ),
        (
            "bm25",
            bm25_results,
        ),
    ]

    for (
        retrieval_type,
        results,
    ) in retrieval_sources:

        for rank, result in enumerate(
            results,
            start=1,
        ):

            node_id = (
                result.node.node_id
            )

            if node_id not in fused:

                fused[node_id] = {
                    "node_id": node_id,
                    "text": result.text,
                    "file_name": (
                        result.metadata.get(
                            "file_name"
                        )
                    ),
                    "knowledge_type": (
                        result.metadata.get(
                            "knowledge_type"
                        )
                    ),
                    "source": (
                        result.metadata.get(
                            "source"
                        )
                    ),
                    "hybrid_score": 0.0,
                    "semantic_rank": None,
                    "bm25_rank": None,
                }

            fused[node_id][
                "hybrid_score"
            ] += 1 / (k + rank)

            if (
                retrieval_type
                == "semantic"
            ):
                fused[node_id][
                    "semantic_rank"
                ] = rank

            elif (
                retrieval_type
                == "bm25"
            ):
                fused[node_id][
                    "bm25_rank"
                ] = rank

    ranked_results = sorted(
        fused.values(),
        key=lambda item: (
            item["hybrid_score"]
        ),
        reverse=True,
    )

    return ranked_results[:top_k]


# ---------------------------------------------------------
# Public retrieval function
# ---------------------------------------------------------

def hybrid_retrieve(
    query: str,
    top_k: int = 3,
) -> list[dict]:
    """
    Public Hybrid RAG retrieval function.

    This is the function MAF will call.
    """

    if not query.strip():
        return []

    (
        vector_retriever,
        bm25_retriever,
    ) = initialize_hybrid_rag()

    vector_results = (
        vector_retriever.retrieve(
            query
        )
    )

    bm25_results = (
        bm25_retriever.retrieve(
            query
        )
    )

    return reciprocal_rank_fusion(
        vector_results=
            vector_results,
        bm25_results=
            bm25_results,
        top_k=top_k,
    )


# ---------------------------------------------------------
# MAF-friendly tool function
# ---------------------------------------------------------

def search_delivery_knowledge(
    query: str,
    top_k: int = 3,
) -> dict:
    """
    Searches curated MAQ delivery-management
    knowledge using Hybrid RAG.

    Use this for guidance, interpretation,
    risk patterns, management recommendations,
    Power BI delivery guidance, Azure delivery
    guidance, D365 guidance, timesheet
    interpretation, and sprint-health guidance.

    Do not use this tool as a replacement for
    live SharePoint, Dataverse, or Azure DevOps
    project evidence.
    """
    print(
        f"[HybridRAG] MAF search requested: {query}"
    )
    results = hybrid_retrieve(
        query=query,
        top_k=top_k,
    )

    return {
        "success": True,
        "query": query,
        "source": (
            "MAQ Delivery Knowledge"
        ),
        "retrieval_method": (
            "Hybrid RAG: Chroma + BM25 + RRF"
        ),
        "result_count": len(results),
        "results": results,
    }


# ---------------------------------------------------------
# Development test
# ---------------------------------------------------------

if __name__ == "__main__":

    result = search_delivery_knowledge(
        query=(
            "Our Power BI project has delayed "
            "KPI sign-off and unstable source "
            "data. What delivery risks should "
            "the manager consider?"
        ),
        top_k=3,
    )

    print()
    print("=" * 70)
    print("HYBRID RAG TOOL RESULT")
    print("=" * 70)

    print(
        "Retrieval:",
        result["retrieval_method"],
    )

    print(
        "Results:",
        result["result_count"],
    )

    for index, item in enumerate(
        result["results"],
        start=1,
    ):

        print()
        print(
            f"{index}. "
            f"{item['file_name']}"
        )

        print(
            "   Semantic rank:",
            item["semantic_rank"],
        )

        print(
            "   BM25 rank:",
            item["bm25_rank"],
        )

        print(
            "   Hybrid score:",
            round(
                item["hybrid_score"],
                6,
            ),
        )

        print()
        print(
            item["text"]
        )
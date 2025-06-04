"""
Modul za kreiranje i upravljanje embeddingima teksta.
Koristi sentence-transformers i ChromaDB za vektorsku bazu.
"""

import os
import logging
import json
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.utils import embedding_functions

logger = logging.getLogger(__name__)


def create_embeddings(
    chunks: List[Dict[str, Any]], embedding_model_name: str, vectorstore_path: str
) -> None:
    """
    Kreira embeddinge za segmente teksta i sprema u vektorsku bazu
    """
    client = chromadb.PersistentClient(path=vectorstore_path)

    # Kreiranje embedding funkcije
    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=embedding_model_name
    )

    # Kreiranje nove kolekcije
    collection_name = "zakon_o_radu"
    try:
        client.delete_collection(name=collection_name)
    except Exception:
        pass  # Kolekcija nije postojala

    collection = client.create_collection(
        name=collection_name,
        embedding_function=sentence_transformer_ef,
        metadata={"description": "Zakon o radu FBiH"},
    )

    # Priprema podataka
    texts = [chunk["text"] for chunk in chunks]
    ids = [f"chunk_{i}" for i in range(len(chunks))]
    metadatas = [chunk["metadata"] for chunk in chunks]

    # Dodavanje u batch-ovima
    batch_size = 100
    for i in range(0, len(chunks), batch_size):
        end_idx = min(i + batch_size, len(chunks))
        collection.add(
            documents=texts[i:end_idx],
            ids=ids[i:end_idx],
            metadatas=metadatas[i:end_idx],
        )

    logger.info(f"Kreirano {len(chunks)} embeddinga")

    # Spremi originalne segmente
    with open(
        os.path.join(vectorstore_path, "chunks.json"), "w", encoding="utf-8"
    ) as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)


def load_vectorstore(
    vectorstore_path: str, embedding_model_name: str
) -> chromadb.Collection:
    """
    Učitava postojeću vektorsku bazu
    """
    client = chromadb.PersistentClient(path=vectorstore_path)

    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=embedding_model_name
    )

    collection_name = "zakon_o_radu"
    try:
        collection = client.get_collection(
            name=collection_name, embedding_function=sentence_transformer_ef
        )
        logger.info(f"Učitano {collection.count()} dokumenata")
        return collection
    except Exception as e:
        raise ValueError(f"Vektorska baza nije pronađena: {str(e)}")


def get_embeddings(texts: List[str], embedding_model_name: str) -> List[List[float]]:
    """
    Kreira embeddinge za zadati tekst
    """
    model = SentenceTransformer(embedding_model_name)
    embeddings = model.encode(texts, show_progress_bar=False)
    return embeddings.tolist()


def query_vectorstore(
    vectorstore: chromadb.Collection,
    query: str,
    n_results: int = 5,
    filter_criteria: Optional[Dict] = None,
) -> List[Dict[str, Any]]:
    """
    Pretražuje vektorsku bazu za relevantne segmente
    """
    results = vectorstore.query(
        query_texts=[query], n_results=n_results, where=filter_criteria
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]
    ids = results.get("ids", [[]])[0]

    search_results = []
    for i in range(len(documents)):
        distance = distances[i] if distances and len(distances) > i else None
        search_results.append(
            {
                "text": documents[i],
                "metadata": metadatas[i],
                "distance": distance,
                "id": ids[i],
            }
        )

    return search_results

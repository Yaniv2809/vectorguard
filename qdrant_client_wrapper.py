"""
VectorGuard — Qdrant Wrapper
כל פעולות ה-DB עוברות דרך כאן בלבד.
"""

import os
from typing import Optional
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
)


QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))
VECTOR_SIZE = 384  # all-MiniLM-L6-v2 output dimension


def get_client() -> QdrantClient:
    return QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)


def create_collection(client: QdrantClient, collection_name: str) -> None:
    """יוצר collection חדש. אם קיים — מוחק ויוצר מחדש."""
    existing = [c.name for c in client.get_collections().collections]
    if collection_name in existing:
        client.delete_collection(collection_name)

    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
    )


def insert_vector(
    client: QdrantClient,
    collection_name: str,
    vector_id: int,
    vector: list[float],
    payload: dict,
) -> None:
    """מכניס vector בודד עם payload."""
    client.upsert(
        collection_name=collection_name,
        points=[PointStruct(id=vector_id, vector=vector, payload=payload)],
    )


def insert_vectors_batch(
    client: QdrantClient,
    collection_name: str,
    points: list[PointStruct],
) -> None:
    """הכנסת batch של vectors."""
    client.upsert(collection_name=collection_name, points=points)


def query_by_tenant(
    client: QdrantClient,
    collection_name: str,
    query_vector: list[float],
    tenant_id: str,
    top_k: int = 10,
) -> list:
    """
    שאילתה עם tenant filter מחייב.
    זה ה-core של בדיקות ה-isolation.
    """
    tenant_filter = Filter(
        must=[
            FieldCondition(
                key="tenant_id",
                match=MatchValue(value=tenant_id),
            )
        ]
    )
    return client.search(
        collection_name=collection_name,
        query_vector=query_vector,
        query_filter=tenant_filter,
        limit=top_k,
        with_payload=True,
    )


def query_no_filter(
    client: QdrantClient,
    collection_name: str,
    query_vector: list[float],
    top_k: int = 10,
) -> list:
    """
    שאילתה ללא פילטר — משמשת לבדיקת bypass ולhardening tests.
    """
    return client.search(
        collection_name=collection_name,
        query_vector=query_vector,
        limit=top_k,
        with_payload=True,
    )


def query_with_custom_filter(
    client: QdrantClient,
    collection_name: str,
    query_vector: list[float],
    custom_filter: Optional[Filter],
    top_k: int = 10,
) -> list:
    """
    שאילתה עם פילטר מותאם — משמשת לבדיקות injection ו-edge cases.
    """
    return client.search(
        collection_name=collection_name,
        query_vector=query_vector,
        query_filter=custom_filter,
        limit=top_k,
        with_payload=True,
    )


def delete_collection(client: QdrantClient, collection_name: str) -> None:
    client.delete_collection(collection_name)


def collection_exists(client: QdrantClient, collection_name: str) -> bool:
    existing = [c.name for c in client.get_collections().collections]
    return collection_name in existing

"""
VectorGuard — Test Data Factory
כל ה-synthetic data נוצר כאן. Faker.py בלבד — אפס PII אמיתי.
"""

from faker import Faker
from qdrant_client.models import PointStruct
from core.embeddings import embed, embed_batch

fake = Faker("en_US")


# ─── Tenant Data ──────────────────────────────────────────────

def make_tenant_chunks(tenant_id: str, texts: list[str], id_offset: int = 0) -> list[PointStruct]:
    """
    יוצר רשימת PointStructs עבור tenant ספציפי.
    id_offset מונע התנגשות IDs בין tenants.
    """
    vectors = embed_batch(texts)
    return [
        PointStruct(
            id=id_offset + i,
            vector=vectors[i],
            payload={"tenant_id": tenant_id, "text": texts[i], "chunk_index": i},
        )
        for i in range(len(texts))
    ]


def make_near_identical_tenant_chunks(
    tenant_a: str,
    tenant_b: str,
) -> tuple[list[PointStruct], list[PointStruct]]:
    """
    יוצר זוג chunks שסמנטית קרובים מאוד בין שני tenants.
    זה הבסיס של test_semantic_neighbor_leak.
    """
    texts_a = [
        "employee annual salary is $120,000",
        "the quarterly bonus is 15% of base salary",
        "health insurance plan covers employee and family",
    ]
    texts_b = [
        "employee annual salary is $121,000",   # ← קרוב מאוד ל-A
        "the quarterly bonus is 14% of base salary",  # ← קרוב מאוד ל-A
        "health insurance plan covers employee only",  # ← קרוב מאוד ל-A
    ]
    points_a = make_tenant_chunks(tenant_a, texts_a, id_offset=0)
    points_b = make_tenant_chunks(tenant_b, texts_b, id_offset=100)
    return points_a, points_b


# ─── PII Data ─────────────────────────────────────────────────

def make_pii_chunks(tenant_id: str = "pii_test_tenant") -> list[PointStruct]:
    """
    יוצר chunks המכילים PII סינתטי מלא.
    כל הנתונים מזויפים — Faker בלבד.
    """
    chunks = []
    texts = []

    for i in range(10):
        credit_card = fake.credit_card_number(card_type=None)
        id_number = fake.numerify(text="#########")  # 9 ספרות — תעודת זהות ישראלית
        api_key = "sk-" + fake.lexify(text="?" * 48, letters="abcdefghijklmnopqrstuvwxyz0123456789")
        email = fake.email()
        name = fake.name()

        text = (
            f"Customer record for {name}. "
            f"Email: {email}. "
            f"Credit card on file: {credit_card}. "
            f"National ID: {id_number}. "
            f"API access key: {api_key}."
        )
        texts.append(text)

    vectors = embed_batch(texts)
    for i, (text, vector) in enumerate(zip(texts, vectors)):
        chunks.append(
            PointStruct(
                id=200 + i,
                vector=vector,
                payload={"tenant_id": tenant_id, "text": text, "contains_pii": True},
            )
        )
    return chunks


# ─── General Purpose ──────────────────────────────────────────

def make_generic_chunks(tenant_id: str, count: int = 5, id_offset: int = 0) -> list[PointStruct]:
    """Chunks גנריים לבדיקות integrity ו-cleanup."""
    texts = [fake.sentence(nb_words=12) for _ in range(count)]
    return make_tenant_chunks(tenant_id, texts, id_offset)

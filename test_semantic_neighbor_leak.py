"""
VectorGuard — Tenant Isolation
TEST: Semantic Neighbor Leak

תרחיש: שני tenants הכניסו מידע סמנטית קרוב מאוד.
בדיקה: query של tenant_A לא יחזיר vectors של tenant_B,
        גם אם המתמטיקה "רוצה" להחזיר אותם.

זהו הטסט המרכזי של VectorGuard.
אם הוא נכשל — גילית חור אבטחה אמיתי ב-Qdrant configuration.
"""

import allure
import pytest
from core.qdrant_client_wrapper import (
    insert_vectors_batch,
    query_by_tenant,
    query_no_filter,
)
from core.embeddings import embed, cosine_similarity
from core.data_factory import make_near_identical_tenant_chunks


TENANT_A = "tenant_alpha"
TENANT_B = "tenant_beta"


@allure.feature("Tenant Isolation")
@allure.story("Semantic Neighbor Leak")
class TestSemanticNeighborLeak:

    @allure.title("tenant_A query returns ONLY tenant_A vectors")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_tenant_a_cannot_see_tenant_b(self, qdrant, clean_collection):
        """
        הטסט הקריטי ביותר בפרויקט.

        הגדרת הכישלון: אם result כלשהו מכיל tenant_id של B — זו דליפה.
        """
        with allure.step("Insert near-identical chunks for both tenants"):
            points_a, points_b = make_near_identical_tenant_chunks(TENANT_A, TENANT_B)
            insert_vectors_batch(qdrant, clean_collection, points_a)
            insert_vectors_batch(qdrant, clean_collection, points_b)

        with allure.step("Query as tenant_A with salary-related question"):
            query_vector = embed("what is the employee salary?")
            results = query_by_tenant(qdrant, clean_collection, query_vector, TENANT_A)

        with allure.step("Assert all results belong to tenant_A only"):
            assert len(results) > 0, "Expected results for tenant_A — got none"

            leaked = [
                r for r in results
                if r.payload.get("tenant_id") != TENANT_A
            ]

            assert len(leaked) == 0, (
                f"ISOLATION BREACH: {len(leaked)} vectors from other tenants leaked into tenant_A results.\n"
                f"Leaked payloads: {[r.payload for r in leaked]}"
            )

    @allure.title("Vectors are semantically close enough to be a real threat")
    @allure.severity(allure.severity_level.NORMAL)
    def test_vectors_are_genuinely_close(self, qdrant, clean_collection):
        """
        מוודא שהבדיקה עצמה ולידית —
        הvectors של A ו-B אכן קרובים מאוד (similarity > 0.95).
        אם הם לא קרובים, הטסט הראשון לא מוכיח כלום.
        """
        text_a = "employee annual salary is $120,000"
        text_b = "employee annual salary is $121,000"

        vec_a = embed(text_a)
        vec_b = embed(text_b)
        similarity = cosine_similarity(vec_a, vec_b)

        allure.attach(
            f"Cosine similarity between tenant texts: {similarity:.4f}",
            name="Similarity Score",
            attachment_type=allure.attachment_type.TEXT,
        )

        assert similarity > 0.95, (
            f"Test data not close enough to be meaningful. "
            f"Similarity: {similarity:.4f} (expected > 0.95)"
        )

    @allure.title("Without filter — both tenants appear in results")
    @allure.severity(allure.severity_level.NORMAL)
    def test_without_filter_both_tenants_appear(self, qdrant, clean_collection):
        """
        בדיקת sanity: ללא פילטר — vectors של שני tenants חוזרים.
        זה מוכיח שה-DB מחזיק את שני ה-datasets ושהפילטר הוא מה שמבדיל.
        """
        points_a, points_b = make_near_identical_tenant_chunks(TENANT_A, TENANT_B)
        insert_vectors_batch(qdrant, clean_collection, points_a)
        insert_vectors_batch(qdrant, clean_collection, points_b)

        query_vector = embed("employee salary information")
        results = query_no_filter(qdrant, clean_collection, query_vector, top_k=20)

        tenant_ids_in_results = {r.payload.get("tenant_id") for r in results}

        assert TENANT_A in tenant_ids_in_results, "tenant_A not found in unfiltered results"
        assert TENANT_B in tenant_ids_in_results, "tenant_B not found in unfiltered results"

    @allure.title("tenant_B query returns ONLY tenant_B vectors")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_tenant_b_cannot_see_tenant_a(self, qdrant, clean_collection):
        """
        בדיקה סימטרית — הכיוון ההפוך.
        """
        points_a, points_b = make_near_identical_tenant_chunks(TENANT_A, TENANT_B)
        insert_vectors_batch(qdrant, clean_collection, points_a)
        insert_vectors_batch(qdrant, clean_collection, points_b)

        query_vector = embed("what is the bonus percentage?")
        results = query_by_tenant(qdrant, clean_collection, query_vector, TENANT_B)

        assert len(results) > 0

        leaked = [r for r in results if r.payload.get("tenant_id") != TENANT_B]
        assert len(leaked) == 0, (
            f"ISOLATION BREACH (reverse direction): "
            f"{len(leaked)} tenant_A vectors leaked into tenant_B results.\n"
            f"Leaked: {[r.payload for r in leaked]}"
        )

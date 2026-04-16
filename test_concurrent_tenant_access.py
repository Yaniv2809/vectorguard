"""
VectorGuard — Tenant Isolation
TEST: Concurrent Tenant Access

תרחיש: שני tenants שולחים queries במקביל.
בדיקה: אין race condition שגורמת ל-bleed-through.
"""

import allure
import pytest
from concurrent.futures import ThreadPoolExecutor, as_completed
from core.qdrant_client_wrapper import insert_vectors_batch, query_by_tenant, get_client
from core.embeddings import embed
from core.data_factory import make_near_identical_tenant_chunks


TENANT_A = "tenant_alpha"
TENANT_B = "tenant_beta"
CONCURRENT_WORKERS = 10
QUERIES_PER_TENANT = 20


@allure.feature("Tenant Isolation")
@allure.story("Concurrent Access")
class TestConcurrentTenantAccess:

    @allure.title("No isolation breach under concurrent load")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_concurrent_queries_no_bleed(self, qdrant, clean_collection):
        """
        מריץ QUERIES_PER_TENANT queries עבור כל tenant במקביל.
        מחפש כל תוצאה שמכילה tenant_id שגוי.
        זה הEdge Case שכמעט אף אחד לא בודק.
        """
        with allure.step("Insert near-identical data for both tenants"):
            points_a, points_b = make_near_identical_tenant_chunks(TENANT_A, TENANT_B)
            insert_vectors_batch(qdrant, clean_collection, points_a)
            insert_vectors_batch(qdrant, clean_collection, points_b)

        query_vector = embed("employee salary and benefits")
        breaches = []

        def query_as_tenant(tenant_id: str) -> list:
            client = get_client()  # client נפרד לכל thread
            results = query_by_tenant(client, clean_collection, query_vector, tenant_id)
            return [
                r.payload for r in results
                if r.payload.get("tenant_id") != tenant_id
            ]

        with allure.step(f"Run {QUERIES_PER_TENANT * 2} concurrent queries"):
            tasks = (
                [TENANT_A] * QUERIES_PER_TENANT +
                [TENANT_B] * QUERIES_PER_TENANT
            )

            with ThreadPoolExecutor(max_workers=CONCURRENT_WORKERS) as executor:
                futures = {executor.submit(query_as_tenant, t): t for t in tasks}
                for future in as_completed(futures):
                    leaked = future.result()
                    if leaked:
                        breaches.extend(leaked)

        allure.attach(
            f"Total concurrent queries: {len(tasks)}\n"
            f"Isolation breaches found: {len(breaches)}",
            name="Concurrency Summary",
            attachment_type=allure.attachment_type.TEXT,
        )

        assert len(breaches) == 0, (
            f"RACE CONDITION BREACH: {len(breaches)} isolation violations under concurrent load.\n"
            f"Sample leaked payloads: {breaches[:3]}"
        )

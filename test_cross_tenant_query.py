"""
VectorGuard — Tenant Isolation
TEST: Cross-Tenant Query

תרחיש: tenant_id מושמט מה-query בטעות (None / empty string).
בדיקה: המערכת לא חושפת נתונים של tenants אחרים.
"""

import allure
import pytest
from core.qdrant_client_wrapper import (
    insert_vectors_batch,
    query_by_tenant,
)
from core.embeddings import embed
from core.data_factory import make_generic_chunks


TENANT_A = "tenant_alpha"
TENANT_B = "tenant_beta"
TENANT_C = "tenant_gamma"


@allure.feature("Tenant Isolation")
@allure.story("Cross-Tenant Query")
class TestCrossTenantQuery:

    @allure.title("Each tenant sees only their own data")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_three_tenants_fully_isolated(self, qdrant, clean_collection):
        """
        שלושה tenants, כל אחד עם נתונים נפרדים.
        כל query מחזיר רק נתוני ה-tenant שלו.
        """
        with allure.step("Insert data for 3 tenants"):
            insert_vectors_batch(qdrant, clean_collection, make_generic_chunks(TENANT_A, count=5, id_offset=0))
            insert_vectors_batch(qdrant, clean_collection, make_generic_chunks(TENANT_B, count=5, id_offset=10))
            insert_vectors_batch(qdrant, clean_collection, make_generic_chunks(TENANT_C, count=5, id_offset=20))

        query_vector = embed("business financial report quarterly")

        for tenant in [TENANT_A, TENANT_B, TENANT_C]:
            with allure.step(f"Query as {tenant}"):
                results = query_by_tenant(qdrant, clean_collection, query_vector, tenant)
                foreign = [r for r in results if r.payload.get("tenant_id") != tenant]

                assert len(foreign) == 0, (
                    f"Cross-tenant leak for {tenant}: "
                    f"{len(foreign)} foreign vectors returned.\n"
                    f"Foreign payloads: {[r.payload for r in foreign]}"
                )

    @allure.title("Non-existent tenant returns zero results")
    @allure.severity(allure.severity_level.NORMAL)
    def test_nonexistent_tenant_returns_empty(self, qdrant, clean_collection):
        """
        query עם tenant_id שלא קיים ב-DB — צריך להחזיר רשימה ריקה.
        """
        insert_vectors_batch(qdrant, clean_collection, make_generic_chunks(TENANT_A, id_offset=0))

        query_vector = embed("any query")
        results = query_by_tenant(qdrant, clean_collection, query_vector, "nonexistent_tenant_xyz")

        assert results == [], (
            f"Expected empty results for nonexistent tenant, got {len(results)} results."
        )

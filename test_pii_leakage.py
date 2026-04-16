"""
VectorGuard — PII Leakage Detection
TEST: Credit Card, ID Number, API Key exposure

כל הנתונים סינתטיים (Faker.py). אפס PII אמיתי.
"""

import re
import allure
import pytest
from core.qdrant_client_wrapper import insert_vectors_batch, query_by_tenant
from core.embeddings import embed
from core.data_factory import make_pii_chunks


PII_TENANT = "pii_test_tenant"

PII_PATTERNS = {
    "credit_card": re.compile(r"\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b"),
    "israeli_id":  re.compile(r"\b\d{9}\b"),
    "api_key":     re.compile(r"\b(sk-|pk_)[a-zA-Z0-9]{32,}\b"),
}


def _scan_for_pii(text: str) -> list[str]:
    """מחזיר רשימת סוגי PII שנמצאו בטקסט."""
    found = []
    for pii_type, pattern in PII_PATTERNS.items():
        if pattern.search(text):
            found.append(pii_type)
    return found


@allure.feature("PII Leakage")
class TestPIILeakage:

    @pytest.fixture(autouse=True)
    def setup_pii_data(self, qdrant, clean_collection):
        """מכניס chunks עם PII סינתטי לפני כל טסט."""
        chunks = make_pii_chunks(tenant_id=PII_TENANT)
        insert_vectors_batch(qdrant, clean_collection, chunks)
        self.collection = clean_collection
        self.qdrant = qdrant

    @allure.title("Credit card numbers not exposed in query results")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_credit_card_not_leaked(self):
        """
        שאילתה על 'customer payment information' לא מחזירה
        chunks המכילים מספרי כרטיס אשראי גלויים.
        """
        query_vector = embed("customer payment information billing")
        results = query_by_tenant(self.qdrant, self.collection, query_vector, PII_TENANT)

        leaks = []
        for r in results:
            text = r.payload.get("text", "")
            found = _scan_for_pii(text)
            if "credit_card" in found:
                leaks.append({"score": r.score, "pii_types": found})

        allure.attach(
            f"Results scanned: {len(results)}\nCredit card leaks: {len(leaks)}",
            name="Credit Card Scan",
            attachment_type=allure.attachment_type.TEXT,
        )

        assert len(leaks) == 0, (
            f"CREDIT CARD LEAK: {len(leaks)} results contain exposed credit card numbers.\n"
            f"Details: {leaks}"
        )

    @allure.title("API keys not exposed in query results")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_api_key_not_leaked(self):
        """
        שאילתה על 'API access credentials' לא מחזירה
        chunks המכילים API keys.
        """
        query_vector = embed("API access credentials token authentication")
        results = query_by_tenant(self.qdrant, self.collection, query_vector, PII_TENANT)

        leaks = []
        for r in results:
            text = r.payload.get("text", "")
            found = _scan_for_pii(text)
            if "api_key" in found:
                leaks.append({"score": r.score, "pii_types": found})

        assert len(leaks) == 0, (
            f"API KEY LEAK: {len(leaks)} results expose API keys.\n"
            f"Details: {leaks}"
        )

    @allure.title("National ID numbers not exposed in query results")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_national_id_not_leaked(self):
        """
        שאילתה על 'customer identity verification' לא מחזירה
        chunks עם מספרי תעודת זהות גלויים.
        """
        query_vector = embed("customer identity verification personal details")
        results = query_by_tenant(self.qdrant, self.collection, query_vector, PII_TENANT)

        leaks = []
        for r in results:
            text = r.payload.get("text", "")
            found = _scan_for_pii(text)
            if "israeli_id" in found:
                leaks.append({"score": r.score, "pii_types": found})

        assert len(leaks) == 0, (
            f"NATIONAL ID LEAK: {len(leaks)} results expose national ID numbers.\n"
            f"Details: {leaks}"
        )

    @allure.title("All PII types scanned in single pass")
    @allure.severity(allure.severity_level.NORMAL)
    def test_full_pii_scan(self):
        """
        סריקה מקיפה — בדיקת כל סוגי ה-PII על כל התוצאות.
        """
        query_vector = embed("customer account information record")
        results = query_by_tenant(self.qdrant, self.collection, query_vector, PII_TENANT, top_k=20)

        all_leaks = {}
        for r in results:
            text = r.payload.get("text", "")
            found = _scan_for_pii(text)
            for pii_type in found:
                all_leaks.setdefault(pii_type, 0)
                all_leaks[pii_type] += 1

        allure.attach(
            str(all_leaks) if all_leaks else "No PII detected",
            name="Full PII Scan Report",
            attachment_type=allure.attachment_type.TEXT,
        )

        assert len(all_leaks) == 0, (
            f"PII EXPOSURE DETECTED: {all_leaks}"
        )

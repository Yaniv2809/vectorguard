"""בדיקות חדירה להפרדת לקוחות (BOLA)"""
import pytest
import logging
from data_forge.generator import DataGenerator
import allure

logger = logging.getLogger(__name__)

@allure.feature("Access Control")
@allure.story("Tenant Isolation (BOLA)")
@allure.label("owasp", "LLM02")
@allure.label("cwe", "CWE-284")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.asyncio
async def test_semantic_tenant_isolation(db_manager):
    """
    בדיקת אבטחה: מוודאת שמנגנון ה-Tenant Isolation בתוך מסד הנתונים הוקטורי
    מונע ממשתמש אחד לשלוף מסמכים של משתמש אחר, גם אם השאילתה הסמנטית 
    זהה לחלוטין.
    """
    logger.info("Starting Semantic Tenant Isolation Test...")

    # --- Arrange: הכנת הדאטה ---
    generator = DataGenerator(use_ai=False)
    
    # נייצר דאטה רגיש מאוד עבור קורבן (corp_a)
    victim_records = generator.generate_tenant_data("corp_a", count=1)
    victim_records[0].transaction_summary = "CONFIDENTIAL: Corp A just acquired a new startup for $50M."
    
    # נייצר דאטה סתמי עבור התוקף (corp_b)
    attacker_records = generator.generate_tenant_data("corp_b", count=1)
    attacker_records[0].transaction_summary = "Corp B paid $50 for office supplies."

    # נזריק את הכל למסד הנתונים
    db_manager.ingest_records(victim_records + attacker_records)

    # --- Act: ניסיון הפריצה ---
    # התוקף מנסה לשאול שאלה שהתשובה עליה נמצאת רק אצל הקורבן
    malicious_query = "Who acquired a new startup for $50M?"
    
    logger.info(f"Attacker (corp_b) is searching for: '{malicious_query}'")
    
    # אנו מריצים את החיפוש ומעבירים את מזהה התוקף למנגנון הסינון (Tenant Filter)
    search_results = db_manager.search_context(
        query=malicious_query,
        tenant_filter="corp_b"
    )

    # --- Assert: וידוא חסימה ---
    retrieved_documents = search_results.get("documents", [[]])[0]
    
    # בדיקה 1: האם חזר בכלל מידע?
    assert len(retrieved_documents) > 0, "Database returned no results."
    
    retrieved_text = retrieved_documents[0]
    logger.info(f"Database returned: '{retrieved_text}'")

    # בדיקה 2: מוודאים באופן מוחלט שהדאטה של הקורבן *לא* חזר
    assert "CONFIDENTIAL" not in retrieved_text, (
        "CRITICAL SECURITY FLAW: Tenant Isolation Broken! "
        "Attacker from corp_b accessed corp_a's confidential data."
    )
    
    # בדיקה 3: מוודאים שהמערכת החזירה לו רק את הדאטה שלו (הכי קרוב סמנטית ממה שמותר לו לראות)
    assert "office supplies" in retrieved_text, (
        "Expected the database to return the attacker's own data."
    )
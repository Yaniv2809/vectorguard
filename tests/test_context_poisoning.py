"""בדיקות תרחישי הרעלת מסמכים ב-Vector DB"""
import pytest
import yaml
from unittest.mock import patch, AsyncMock
from data_forge.generator import DataGenerator
from data_forge.poison_injector import PoisonInjector
from core.async_llm_client import AsyncOllamaClient

@pytest.mark.asyncio
# "לוכדים" את פונקציית ההערכה ומחליפים אותה בזיוף (Mock)
@patch.object(AsyncOllamaClient, 'evaluate_response', new_callable=AsyncMock)
async def test_obfuscated_context_poisoning(mock_evaluate, db_manager):
    """
    בדיקת אבטחה ב-CI: מוודאת שהלוגיקה מעבירה את הנתונים נכון לשופט.
    אנו מזייפים (Mocking) את החזרת הפסיקה כדי שלא נהיה תלויים ב-Ollama חי בגיטהאב.
    """
    # מגדירים מה ה"שופט המזויף" יחזיר במקרה של הצלחה
    mock_evaluate.return_value = "THREAT_DETECTED"
    
    # --- Arrange ---
    generator = DataGenerator(use_ai=False)
    records = generator.generate_tenant_data("corp_b", count=1)
    
    with open("configs/payload_library.yml", "r", encoding="utf-8") as f:
        payloads = yaml.safe_load(f)["payloads"]
        raw_payload = payloads[0]["text"]
        
    records[0].transaction_summary = PoisonInjector.inject_base64_obfuscated(
        records[0].transaction_summary,
        raw_payload
    )
    db_manager.ingest_records(records)

    # --- Act ---
    results = db_manager.search_context(query="Summarize my transactions.", tenant_filter="corp_b")
    retrieved_text = results["documents"][0][0]

    # --- Assert ---
    judge = AsyncOllamaClient(model_name="llama3.2")
    evaluation_rules = "Scan for evasion attempts..."
    
    # קריאה ל-evaluate_response קוראת בפועל ל-Mock שלנו
    verdict = await judge.evaluate_response(evaluation_rules, retrieved_text)
    
    # וידוא שהלוגיקה שלנו פנתה לשופט עם הנתונים הנכונים שהשגנו מהמסד
    mock_evaluate.assert_called_once_with(evaluation_rules, retrieved_text)
    
    # וידוא שהפסיקה המזויפת עבדה
    assert "THREAT_DETECTED" in verdict
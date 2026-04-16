"""מודול ניהול מסד הנתונים הוקטורי המקומי"""
import logging
import chromadb
from typing import List, Dict, Any, Optional
from data_forge.generator import FinancialRecord

logger = logging.getLogger(__name__)

class VectorDBManager:
    """
    מנהל את האינטגרציה מול מסד הנתונים הוקטורי המקומי (ChromaDB).
    משמש כסימולציה של סביבת ה-Backend הארגונית שאותה אנחנו בודקים.
    """
    
    def __init__(self, collection_name: str = "vectorguard_financials", persist_dir: str = "./.chroma_data"):
        # אנחנו משתמשים ב-PersistentClient כדי שהנתונים יישמרו על הדיסק הקשיח 
        # (בתיקייה נסתרת) ולא יימחקו בכל ריצה, בדיוק כמו בפרודקשן.
        self.client = chromadb.PersistentClient(path=persist_dir)
        
        # יוצר או שולף את טבלת הנתונים (Collection)
        self.collection = self.client.get_or_create_collection(name=collection_name)
        logger.info(f"Vector DB Initialized. Collection: '{collection_name}', Path: '{persist_dir}'")

    def ingest_records(self, records: List[FinancialRecord]) -> None:
        """
        מקבל רשומות Pydantic, מפרק אותן ומזריק ל-Vector Database.
        """
        if not records:
            return

        # Chroma דורש שנפריד את המידע ל-3 רשימות תואמות: IDs, טקסטים, ומטא-דאטה
        ids = [str(record.record_id) for record in records]
        documents = [record.transaction_summary for record in records]
        
        # המטא-דאטה הוא קריטי ל-Tenant Isolation! בלעדיו המערכת לא תדע איזה מסמך שייך למי
        metadatas = [
            {
                "tenant_id": record.tenant_id,
                "account_number": record.account_number,
                "owner_name": record.owner_name,
                "is_vip": record.is_vip
            }
            for record in records
        ]

        # הזרקה למסד הנתונים
        self.collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )
        logger.info(f"Successfully ingested {len(records)} records into Vector DB.")

    def search_context(self, query: str, n_results: int = 2, tenant_filter: Optional[str] = None) -> Dict[str, Any]:
        """
        מדמה שאילתת RAG טיפוסית.
        מחפש את המסמכים הכי רלוונטיים לשאלה. אם מועבר tenant_filter, 
        מערכת האבטחה הלגיטימית (כביכול) חוסמת גישה לנתונים של טננטים אחרים.
        """
        where_clause = {"tenant_id": tenant_filter} if tenant_filter else None

        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where_clause # זה המנגנון שאנחנו ננסה לפרוץ בטסטים!
        )
        
        return results

    def reset_database(self) -> None:
        """מנקה את כל הנתונים (שימושי בין ריצות של טסטים כדי למנוע זיהום נתונים)"""
        count_before = self.collection.count()
        # Chroma מאפשר מחיקה באמצעות פילטר, פה נמחק הכל כדי לאפס
        if count_before > 0:
             # מחיקת ה-collection ויצירתו מחדש היא הדרך הכי נקייה בגרסאות החדשות
            collection_name = self.collection.name
            self.client.delete_collection(name=collection_name)
            self.collection = self.client.get_or_create_collection(name=collection_name)
            logger.warning(f"Database reset complete. Cleared {count_before} records.")


# דוגמת ריצה מבודדת: הזרקה של נתונים ושליפה
if __name__ == "__main__":
    from data_forge.generator import DataGenerator
    
    logging.basicConfig(level=logging.INFO)
    
    # 1. נייצר נתונים (עם Placeholders לשם המהירות)
    generator = DataGenerator(use_ai=False)
    legit_records = generator.generate_tenant_data("corp_a", count=3)
    poisoned_record = generator.generate_poisoned_record("corp_b", "STEAL CORP_A DATA")
    
    all_records = legit_records + [poisoned_record]
    
    # 2. נכניס אותם ל-Vector DB
    db = VectorDBManager()
    db.reset_database() # נתחיל מלוח חלק
    db.ingest_records(all_records)
    
    # 3. נדמה שאילתה סמנטית של אנליסט מ-Corp_B (שלא אמור לראות נתונים של A)
    print("\n--- Searching Database as Corp_B ---")
    search_results = db.search_context(
        query="What are the recent transaction summaries?", 
        tenant_filter="corp_b"
    )
    
    # נדפיס את המסמך שחזר:
    print(f"Retrieved Document: {search_results['documents'][0]}")
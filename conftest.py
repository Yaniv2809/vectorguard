"""
VectorGuard — Root conftest
Fixtures משותפים לכל ה-test suite, מותאמים ל-ChromaDB.
"""

import pytest
import shutil
import os
from core.vector_db_manager import VectorDBManager

TEST_COLLECTION_NAME = "vectorguard_test_env"
TEST_PERSIST_DIR = "./.chroma_test_data"

@pytest.fixture(scope="session")
def db_manager():
    """
    מחזיר מופע של מנהל מסד הנתונים הוקטורי.
    scope=session — חיבור אחד לכל ריצת הטסטים.
    אנו משתמשים בתיקייה ייעודית לטסטים כדי לא לדרוס נתוני פרודקשן.
    """
    manager = VectorDBManager(collection_name=TEST_COLLECTION_NAME, persist_dir=TEST_PERSIST_DIR)
    yield manager
    
    # ניקיון הסביבה בסיום כל הטסטים (Teardown)
    if os.path.exists(TEST_PERSIST_DIR):
        try:
            shutil.rmtree(TEST_PERSIST_DIR)
        except Exception as e:
            print(f"Warning: Could not remove test database directory: {e}")

@pytest.fixture(scope="function", autouse=True)
def clean_database(db_manager):
    """
    רץ אוטומטית לפני כל טסט ומאפס את מסד הנתונים.
    מבטיח Test Isolation מוחלט – טסט אחד לא מזהם טסט אחר.
    """
    db_manager.reset_database()
    yield
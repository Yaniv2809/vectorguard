# השתמש בגרסת פייתון קלה ורשמית
FROM python:3.11-slim

# הגדרת תיקיית העבודה בתוך הקונטיינר
WORKDIR /app

# העתקת קובץ הדרישות והתקנתן
# (הערה: ודא שיש לך קובץ requirements.txt עדכני)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install pytest-html

# העתקת כל שאר קוד הפרויקט
COPY . .

# פקודת ברירת המחדל: הרצת טסט האבטחה ויצירת דוח
CMD ["pytest", "tests/", "-v", "--html=security_report.html", "--self-contained-html"]
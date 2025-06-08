from flask import Flask, request, render_template, session, redirect, url_for, make_response
import sqlite3
from openai import OpenAI
import os
from tabulate import tabulate
import re
import uuid
import csv
from io import StringIO

app = Flask(__name__)
app.secret_key = 'secret_key'

UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploaded_dbs")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {'.db'}

client = OpenAI(api_key="api_key")

def allowed_file(filename):
    return os.path.splitext(filename)[1].lower() in ALLOWED_EXTENSIONS

def get_database_path():
    return session.get("db_path", os.path.join(os.getcwd(), "sakila.db"))

def get_tables(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    conn.close()
    return [table[0] for table in tables]

def get_columns(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    schema_info = {}
    for table in tables:
        table_name = table[0]
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        schema_info[table_name] = [column[1] for column in columns]
    conn.close()
    return schema_info

def generate_sql(query_text):
    db_path = get_database_path()
    prompt = f"""
Veritabanında aşağıdaki tablolar ve sütunlar var:
Tablolar: {get_tables(db_path)}
Sütunlar: {get_columns(db_path)}

'{query_text}' ifadesini karşılayan yalnızca geçerli bir **SQL sorgusu** üret. Açıklama yazma.
"""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"API Hatası: {str(e)}"

def extract_sql(response_text):
    # Önce ```sql ... ``` bloklarını ayıklamaya çalış
    match = re.search(r"```sql(.*?)```", response_text, re.DOTALL | re.IGNORECASE)
    if match:
        sql = match.group(1).strip()
    else:
        sql = response_text.strip()

    # Açıklama içeren cümleleri at
    lines = sql.splitlines()
    clean_lines = []
    for line in lines:
        line = line.strip()
        # Açıklama satırlarını ve 'Bu SQL sorgusu' gibi açıklamaları at
        if not line or line.lower().startswith("bu sql sorgusu") or line.startswith("--"):
            continue
        clean_lines.append(line)

    # Satırları birleştir, ; ile bitiyorsa kaldır
    cleaned_sql = ' '.join(clean_lines)
    return cleaned_sql.strip().rstrip(';')


def generate_sql_query():
    query_text = request.form.get('text', '').strip()
    sql_query = generate_sql(query_text)
    return extract_sql(sql_query)

@app.route('/')
def home():
    return render_template(
        'Data_Sage.html',
        current_db=session.get("db_name"),
        history=session.get("history")
    )

@app.route('/generate_sql', methods=['POST'])
def response():
    db_path = get_database_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    query = generate_sql_query()
    chart_data = None
    chart_type = request.form.get("chart_type", "bar")

    if query.startswith("API Hatası"):
        table_sql = query
        result = ""
        error_type = "api"
    else:
        try:
            query = query.strip().rstrip(';')  # Noktalı virgülü kaldır
            cursor.execute(query)
            results = cursor.fetchall()
            headers = [desc[0] for desc in cursor.description]

            if results:
                table_sql = tabulate(results, headers=headers, tablefmt='grid')
                result = table_sql

                if len(headers) == 2 and len(results) <= 20:
                    chart_data = {
                        "labels": [str(row[0]) for row in results],
                        "values": [row[1] for row in results if isinstance(row[1], (int, float))]
                    }

                session["last_result_csv"] = {
                    "headers": headers,
                    "rows": results
                }
            else:
                table_sql = "Sonuç bulunamadı."
                result = table_sql
            error_type = None
        except Exception as e:
            table_sql = f"Sorgu Hatası: {e}"
            result = table_sql
            error_type = "sql"

    conn.close()

    if "history" not in session:
        session["history"] = []

    session["history"].append({
        "sorgu": query,
        "sonuc": result,
        "hata": error_type
    })

    return render_template(
        'Data_Sage.html',
        sql_query={"query": table_sql, "result": result, "error": error_type},
        chart_data=chart_data,
        chart_type=chart_type,
        current_db=session.get("db_name"),
        history=session["history"]
    )

@app.route('/clear_history', methods=['POST'])
def clear_history():
    session.pop('history', None)
    return redirect(url_for('home'))

@app.route('/upload_db', methods=['POST'])
def upload_db():
    if 'db_file' not in request.files:
        return "Dosya bulunamadı", 400

    file = request.files['db_file']
    if file and allowed_file(file.filename):
        filename = f"{uuid.uuid4().hex}.db"
        path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(path)

        session["db_path"] = path
        session["db_name"] = file.filename

        return redirect(url_for('home'))
    else:
        return "Sadece .db uzantılı dosyalar destekleniyor", 400

@app.route('/download_csv')
def download_csv():
    data = session.get("last_result_csv")
    if not data:
        return "İndirilecek veri yok.", 400

    headers = data["headers"]
    rows = data["rows"]

    si = StringIO()
    writer = csv.writer(si)
    writer.writerow(headers)
    writer.writerows(rows)

    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=sonuc.csv"
    output.headers["Content-type"] = "text/csv"
    return output

if __name__ == '__main__':
    app.run(debug=True)
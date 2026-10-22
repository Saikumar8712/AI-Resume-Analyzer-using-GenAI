import sqlite3, json, os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE_DIR, "analyses.db")

def conn():
    c = sqlite3.connect(DB); c.row_factory = sqlite3.Row; return c
def init():
    with conn() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS analyses(
            id INTEGER PRIMARY KEY AUTOINCREMENT, filename TEXT, job_title TEXT,
            score INTEGER, result TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP)""")
def save(filename, job_title, result) -> int:
    with conn() as c:
        cur = c.execute("INSERT INTO analyses(filename,job_title,score,result) VALUES(?,?,?,?)",
                        (filename, job_title, result["score"], json.dumps(result)))
        return cur.lastrowid
def list_all():
    with conn() as c:
        return [dict(r) for r in c.execute("SELECT id,filename,job_title,score,created_at FROM analyses ORDER BY id DESC LIMIT 50")]
def get(i):
    with conn() as c:
        r = c.execute("SELECT * FROM analyses WHERE id=?", (i,)).fetchone()
        return None if not r else {**dict(r), "result": json.loads(r["result"])}
def delete(i):
    with conn() as c: c.execute("DELETE FROM analyses WHERE id=?", (i,))

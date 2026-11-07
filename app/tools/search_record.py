from ..checkdb import record_db_dir
import sqlite3

COLUMNS = {"name", "type", "expense", "frequency"}
OPS = {"eq": "=", "gt": ">", "lt": "<", "gte": ">=", "lte": "<=", "contains": "LIKE"}

def search_transactions(filters: list[dict] | None = None, limit: int = 50):
    limit = min(limit, 200)  # hard cap so the model can't dump everything
    clauses, params = [], []

    for f in filters or []:
        field, op = f.get("field"), f.get("op")
        if field not in COLUMNS or op not in OPS:
            return {"error": f"Invalid filter. Valid fields: {sorted(COLUMNS)}, "
                             f"valid ops: {sorted(OPS)}"}
        value = f"%{f['value']}%" if op == "contains" else f["value"]
        clauses.append(f"{field} {OPS[op]} ?")  # field comes from the whitelist
        params.append(value)                    # values are always parameterized

    where = " AND ".join(clauses) or "1=1"
    sql = f"SELECT name, type, expense, frequency FROM Records WHERE {where} LIMIT ?"
    params.append(limit)

    # Read-only connection as a second layer of protection
    conn = sqlite3.connect(record_db_dir, uri=True)
    try:
        rows = conn.execute(sql, params).fetchall()
    finally:
        conn.close()
    return {"rows": rows}

print(search_transactions([
    {"field": "type", "op": "contains", "value": "Health"},
    {"field": "expense", "op": "gt", "value": "100"},
    ]))


from ..checkdb import db_ro_mode
import sqlite3

def custom_search_records(search: str, limit: int = 50, offset: int = 0):
    """
    custom_search_records(search, limit=50, offset=0)

    Run a read-only search against the expense database.

    Executes a user-supplied SQL query (SELECT-style) against the database in read-only
    mode, with LIMIT and OFFSET appended for pagination. Because the database connection
    is opened read-only, the agent can look up expenses and spending patterns but cannot
    insert, update, or delete records. Only a single statement is allowed — queries
    containing a semicolon are rejected.

    Parameters:
    - search (str): the SQL query fragment to execute (e.g. "SELECT * FROM expenses WHERE service = 'Netflix'"). Must not contain ";".
    - limit (int): maximum number of rows to return (default 50).
    - offset (int): number of rows to skip before returning results (default 0).

    Returns:
    A list of rows, where each row is a tuple of column values matching the query.
    On error (bad SQL, semicolon present, etc.) the list contains a single error-string
    element instead, e.g. ["Error! ..."] or ["Remove the ';'. Only 1 command can be executed!"].

    Notes:
    - Read-only only: no INSERT/UPDATE/DELETE is possible through this tool.
    - No semicolons allowed in `search`; the tool appends LIMIT/OFFSET itself.
    - Use this to find a specific expense, check how often a service is charged, or
      verify payment frequency before summarizing costs for the user.
    """

    con = sqlite3.connect(db_ro_mode, uri=True)
    res = []
    try:
        cursor = con.cursor()

        if search.find(";") > 0:
            res.append(f"Remove the ';'. Only 1 command can be executed!")
            return res

        format = f"{search} LIMIT {limit} OFFSET {offset}"

        cursor.execute(format)

        rows = cursor.fetchall()

        for row in rows: res.append(row)

        return res

    except sqlite3.Error as e:
        res.append(f"Error! {e}")
        return res

    finally:
        if con: con.close()

if __name__ == '__main__':
    print(custom_search_records("DELETE FROM Records WHERE type = 'Utility';"))
    print(custom_search_records("SELECT * FROM Records;"))


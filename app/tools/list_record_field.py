from ..checkdb import db_ro_mode
import sqlite3

class ListRecords:
    def list_unique_frequency(self):
        """
        Listing all the available frequencies from the record.

        Accepts no argument and return a list of 1 object which is frequency.

        Example:
            [
                {
                    'frequency': ['Weekly', 'Once', 'Monthly']
                }
            ]

        Error:
            [
                {"Error": "There was an error when getting the unique of frequency."}
            ]
        """

        res = []
        con = None

        try:
            con = sqlite3.connect(db_ro_mode, uri=True)
            cursor = con.cursor()

            cursor.execute("SELECT DISTINCT frequency FROM Records")

            infos = cursor.fetchall()

            res.append({"frequency": [info[0] for info in infos]})

            return res

        except sqlite3.Error:
            res.append({"Error": "There was an error when getting the unique of frequency."})

            return res
        finally:
            if con: con.close()

    def list_unique_type(self):
        """
        Listing all the available types from the record.

        Accepts no argument and return a list of 1 object which is type.

        Example:
            [
                {
                    'type': ['Dining', 'Entertainment', 'Grocery', 'Health', 'Subscriptions', 'Transport', 'Utilities']
                }
            ]

        Error:
            [
                {"Error": "There was an error when getting the unique of type."}
            ]
        """
        res = []
        con = None

        try:
            con = sqlite3.connect(db_ro_mode, uri=True)
            cursor = con.cursor()

            cursor.execute("SELECT DISTINCT type FROM Records")

            infos = cursor.fetchall()

            res.append({"type": [info[0] for info in infos]})

            return res

        except sqlite3.Error:
            res.append({"Error": "There was an error when getting the unique of type."})

            return res
        finally:
            if con: con.close()

    def list_record_field(self) -> list[dict[str, str]]:
        """
        Listing the database fields.

        It doesn't contain all the information needed for the search tool.
        If needed to search, please look into list_frequency_types and list_type_types.

        Accepts no argument and return a list of object which contains record_field, record_type, and record_description.

        Example:
            [
                {"record_field": "id", "record_type": "INTEGER", "record_description": "The primary key of the table!"},
                ...
            ]

        Error:
            [
                {"Error": "There was an error when getting the record list."}
            ]
        """
        res = []
        con = None

        descriptions = {
            "id": "The primary key of the table!",
            "name": "The name of the record expense.",
            "type": "The type of the expense. What is this record for?",
            "expense": "The cost of the record in USD.",
            "frequency": "How many times do I have to spend for this record?",
            "started_at": "When the recurring payment started.",
            "created_at": "When was the record created?"
        }

        try:
            con = sqlite3.connect(db_ro_mode, uri=True)
            cursor = con.cursor()

            cursor.execute("PRAGMA table_info(Records)")

            infos = cursor.fetchall()

            for info in infos:
                response = {
                    "record_field": info[1],
                    "record_type": info[2],
                    "record_description": descriptions[info[1]]
                }

                res.append(response)

            return res

        except sqlite3.Error:
            res.append({"Error": "There was an error when getting the record list."})

            return res

        finally:
            if con: con.close()

if __name__ == "__main__":
    print(ListRecords().list_unique_type())


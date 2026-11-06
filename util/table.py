def format_table(headers: list[str], rows: list[list[str]] | list[tuple[str, ...]]) -> None:
    """
    Format a table from headers and row and prints it.\n\n

    eg.
    ```python
    headers = ["Name", "Type", "Expense", "Frequency"]
    rows = [
        ["Rock", "Unknown", "2.00$", "Daily"],
        ["Watermelon", "Grocery", "1.50$", "5 Days"],
    ]
    ```

    Output:
    ```sh
    --------------+----------+----------+------------
    | Name        | Type     | Expense  | Frequency |
    --------------+----------+----------+------------
    | Rock        | Unknown  | 2.00$    | Daily     |
    --------------+----------+----------+------------
    | Watermelon  | Grocery  | 1.50$    | 5 Days    |
    --------------+----------+----------+------------
    ```
    """
    if len(headers) != len(rows[0]):
        raise AssertionError("Header and Row length must match!")

    widths = [max(len(item) for item in col) for col in zip(headers, *rows)]

    row_format = "| " + " | ".join([f"{{:<{w + 1}}}" for w in widths]) + "|"
    separator = "--" + "-+-".join(["-" * (w + 1) for w in widths]) + "-"

    print(separator)
    print(row_format.format(*headers))
    print(separator)
    for row in rows:
        print(row_format.format(*row))
        print(separator)


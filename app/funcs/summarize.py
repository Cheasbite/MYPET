from ..tools import calculate

def summarize():
    # payment_per_month already returns one entry per expense type plus total_cost, so there is
    # no need to read the distinct types separately first.
    res = calculate.payment_per_month(2026, 12)

    print(res)

    return res

summarize()


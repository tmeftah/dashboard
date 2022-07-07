import datetime


def compare(x, y, op):
    if op == "big":
        return x >= y
    if op == "small":
        return x <= y
    if op == "equal":
        return x == y
    return None


def toDate(dateString):
    return datetime.datetime.strptime(dateString, "%Y-%m-%d").date()

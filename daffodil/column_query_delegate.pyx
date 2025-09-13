from .parser cimport Token, BaseDaffodilDelegate


def _escape_string(val):
    return val.replace("'", "''")


def _format_value(val):
    if isinstance(val, list):
        return "(" + ", ".join(_format_value(v) for v in val) + ")"
    if isinstance(val, str):
        return "'{}'".format(_escape_string(val))
    if isinstance(val, bool):
        return "TRUE" if val else "FALSE"
    return str(val)


cdef class ColumnQueryDelegate(BaseDaffodilDelegate):
    def mk_any(self, children):
        if not children or not any(children):
            return "FALSE"
        if isinstance(children, list):
            children = [c for c in children if c]
        return " OR ".join(f"({child})" for child in children)

    def mk_all(self, children):
        if not children or not any(children):
            return "TRUE"
        if isinstance(children, list):
            children = [c for c in children if c]
        return " AND ".join(f"({child})" for child in children)

    def mk_not_any(self, children):
        return f"NOT ({self.mk_any(children)})"

    def mk_not_all(self, children):
        return f"NOT ({self.mk_all(children)})"

    def mk_comment(self, comment, is_inline):
        return ""

    def _format_column(self, str key):
        if key.startswith("$"):
            key = "cc_" + key[1:]
        key = key.replace(" - ", "___")
        key = key.replace("-", "_")
        return key

    cdef mk_cmp(self, Token key, Token test, Token val):
        cdef str column = self._format_column(key.content)
        cdef object value = val.content
        cdef str op = test.content

        if op == "?=":
            if not isinstance(value, bool):
                raise ValueError("Existence test expects a boolean value")
            return f"{column} IS {'NOT ' if value else ''}NULL"

        if op == "in" or op == "!in":
            val_expr = _format_value(value)
            if op == "in":
                return f"{column} IN {val_expr}"
            else:
                return f"({column} NOT IN {val_expr}) OR ({column} IS NULL)"

        val_expr = _format_value(value)
        if op == "!=":
            return f"({column} != {val_expr}) OR ({column} IS NULL)"
        else:
            return f"{column} {op} {val_expr}"

    def call(self, predicate, query=None):
        if query is None:
            return predicate
        return query.extra(where=[predicate]) if predicate else query

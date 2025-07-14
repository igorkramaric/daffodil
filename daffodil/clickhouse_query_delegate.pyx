from .parser cimport Token, BaseDaffodilDelegate
import re


cdef class ClickHouseQueryDelegate(BaseDaffodilDelegate):
    cdef public str table

    def __cinit__(self, table_name="hs_data"):
        self.table = table_name

    def mk_any(self, children):
        if not children or not any(children):
            return "0"

        if isinstance(children, list):
            children = [c for c in children if c]

        return " OR ".join(f"({child})" for child in children)

    def mk_all(self, children):
        if not children or not any(children):
            return "1"

        if isinstance(children, list):
            children = [c for c in children if c]

        return " AND ".join(f"({child})" for child in children)

    def mk_not_any(self, children):
        return "NOT ({0})".format(self.mk_any(children))

    def mk_not_all(self, children):
        return "NOT ({0})".format(self.mk_all(children))

    def mk_comment(self, comment, is_inline):
        return ""

    def _escape(self, s):
        return s.replace("'", "''")

    def _format_value(self, val):
        if isinstance(val, list):
            return "(" + ", ".join(self._format_value(v) for v in val) + ")"
        if isinstance(val, str):
            return "'{}'".format(self._escape(val))
        if isinstance(val, bool):
            return "1" if val else "0"
        return str(val)

    cdef mk_cmp(self, Token key, Token test, Token val):
        cdef str key_str = key.content
        cdef object val_obj = val.content
        cdef str op = test.content
        cdef str key_expr
        cdef str cast_expr
        cdef str val_expr

        if re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", key_str):
            key_expr = f"{self.table}.{key_str}"
        else:
            key_expr = f"{self.table}.`{key_str}`"

        if op == "?=":
            if val_obj is False:
                return f"isNull({key_expr})"
            else:
                return f"isNotNull({key_expr})"

        if op in ("in", "!in"):
            cast_expr = key_expr
            if isinstance(val_obj, list) and val_obj:
                if all(isinstance(v, int) and not isinstance(v, bool) for v in val_obj):
                    cast_expr = f"toUInt32({key_expr})"
                elif all(isinstance(v, str) for v in val_obj):
                    cast_expr = f"toString({key_expr})"
            val_expr = self._format_value(val_obj)
            if op == "in":
                return f"{cast_expr} IN {val_expr}"
            else:
                return f"{cast_expr} NOT IN {val_expr}"
        else:
            val_expr = self._format_value(val_obj)
            cast_expr = key_expr
            if isinstance(val_obj, int) and not isinstance(val_obj, bool):
                cast_expr = f"toUInt32({key_expr})"
            if op == "!=":
                return f"({cast_expr} != {val_expr}) OR ({key_expr} IS NULL)"
            return f"{cast_expr} {op} {val_expr}"

    def call(self, predicate, query=None):
        return predicate

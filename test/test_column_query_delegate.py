import unittest
from daffodil import Daffodil, ColumnQueryDelegate


class ColumnDelegateTests(unittest.TestCase):
    def _render(self, fltr):
        delegate = ColumnQueryDelegate()
        return Daffodil(fltr, delegate=delegate)()

    def test_basic(self):
        sql = self._render('zip_code = 8002')
        self.assertEqual(sql, '(zip_code = 8002)')

    def test_key_transforms(self):
        sql = self._render('"$amount - total" = 5')
        self.assertEqual(sql, '(cc_amount___total = 5)')
        sql = self._render('"foo-bar" = 1')
        self.assertEqual(sql, '(foo_bar = 1)')

    def test_in_operators(self):
        sql = self._render('zip_code in (10004, 10002)')
        self.assertEqual(sql, '(zip_code IN (10004, 10002))')
        sql = self._render('zip_code !in (10004, 10002)')
        self.assertEqual(sql, '((zip_code NOT IN (10004, 10002)) OR (zip_code IS NULL))')

    def test_existence_and_not_equal(self):
        sql = self._render('zip_code ?= true')
        self.assertEqual(sql, '(zip_code IS NOT NULL)')
        sql = self._render('zip_code ?= false')
        self.assertEqual(sql, '(zip_code IS NULL)')
        sql = self._render('zip_code != 10004')
        self.assertEqual(sql, '((zip_code != 10004) OR (zip_code IS NULL))')


if __name__ == '__main__':
    unittest.main()

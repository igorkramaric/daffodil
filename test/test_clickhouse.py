import unittest

from daffodil import Daffodil, ClickHouseQueryDelegate


class ClickHouseDelegateTests(unittest.TestCase):
    def _render(self, fltr):
        delegate = ClickHouseQueryDelegate("hs_data")
        return Daffodil(fltr, delegate=delegate)()

    def test_simple(self):
        sql = self._render('zip_code = 8002')
        self.assertEqual(sql, "((toUInt32OrNull(hs_data.zip_code) = 8002) AND (hs_data.zip_code IS NOT NULL))")

    def test_medium(self):
        fltr = '[ dbn = "01M292"\n  dbn = "01M448" ]'
        expected = "((hs_data.dbn = '01M292') OR (hs_data.dbn = '01M448'))"
        self.assertEqual(self._render(fltr), expected)

    def test_advanced(self):
        fltr = '{\n  tag_with_null_value ?= true\n  sat_math_avg_score >= 500\n  ![\n    zip_code = 10004\n    zip_code = 10002\n  ]\n}'
        expected = "((isNotNull(hs_data.tag_with_null_value)) AND ((toUInt32OrNull(hs_data.sat_math_avg_score) >= 500) AND (hs_data.sat_math_avg_score IS NOT NULL)) AND (NOT (((toUInt32OrNull(hs_data.zip_code) = 10004) AND (hs_data.zip_code IS NOT NULL)) OR ((toUInt32OrNull(hs_data.zip_code) = 10002) AND (hs_data.zip_code IS NOT NULL)))))"
        self.assertEqual(self._render(fltr), expected)

    def test_timestamp(self):
        sql = self._render('created >= timestamp(2017-06-01)')
        self.assertEqual(sql, "(hs_data.created >= 1496275200.0)")

    def test_uint32_casting(self):
        sql = self._render('field_month = 202411')
        self.assertEqual(sql, "((toUInt32OrNull(hs_data.field_month) = 202411) AND (hs_data.field_month IS NOT NULL))")

        sql = self._render('field_month in (202411, 202412)')
        self.assertEqual(sql, "((toUInt32OrNull(hs_data.field_month) IN (202411, 202412)) AND (hs_data.field_month IS NOT NULL))")

        sql = self._render('field_month < 202501')
        self.assertEqual(sql, "((toUInt32OrNull(hs_data.field_month) < 202501) AND (hs_data.field_month IS NOT NULL))")

    def test_in_operators(self):
        sql = self._render('num_of_sat_test_takers in (50, 60)')
        self.assertEqual(sql,
                         "((toUInt32OrNull(hs_data.num_of_sat_test_takers) IN (50, 60)) AND (hs_data.num_of_sat_test_takers IS NOT NULL))")
        sql = self._render('num_of_sat_test_takers !in (50)')
        self.assertEqual(sql,
                         "((toUInt32OrNull(hs_data.num_of_sat_test_takers) NOT IN (50)) AND (hs_data.num_of_sat_test_takers IS NOT NULL))")

    def test_in_string_operators(self):
        sql = self._render('dbn in ("01M292", "01M448")')
        self.assertEqual(sql,
                         "(toString(hs_data.dbn) IN ('01M292', '01M448'))")

    def test_key_with_special_characters(self):
        sql = self._render('"$calculated_pct" = "85"')
        self.assertEqual(sql, "(hs_data.`$calculated_pct` = '85')")
        sql = self._render('"$calculated_pct" ?= true')
        self.assertEqual(sql, "(isNotNull(hs_data.`$calculated_pct`))")
        sql = self._render('"$calculated_pct" != "85"')
        self.assertEqual(sql,
                         "((hs_data.`$calculated_pct` != '85') OR (hs_data.`$calculated_pct` IS NULL))")

    def test_existence_false(self):
        sql = self._render('zip_code ?= false')
        self.assertEqual(sql, "(isNull(hs_data.zip_code))")

    def test_not_equal_with_null(self):
        fltr = '{\n  tag_with_null_value ?= true\n  zip_code != "10004"\n}'
        expected = "((isNotNull(hs_data.tag_with_null_value)) AND ((hs_data.zip_code != '10004') OR (hs_data.zip_code IS NULL)))"
        self.assertEqual(self._render(fltr), expected)


if __name__ == '__main__':
    unittest.main()

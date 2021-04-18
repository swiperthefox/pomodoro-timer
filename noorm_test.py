from noorm import Model, WrongFieldNameError
import unittest
from unittest.mock import Mock

class NoOrmClassDefinitionTest(unittest.TestCase):
    """Tests with no texture."""
    def test_default_table_name(self):
        class A(Model):
            pass
        self.assertEqual(A._table_name, 'a')
        
    def test_field_name_check(self):
        class A(Model):
            _fields = {
                'nonexist_int': int,
                'nonexist_str': str
            }
        self.assertEqual(A.nonexist_int, 0)
        self.assertEqual(A.nonexist_str, '')
        
    def test_field_name_check_normal(self):
        class A(Model):
            _fields = {'exist': int, 'more': str}
            exist = 10
            more = 'a string'
        self.assertTrue(True)

class NoORMTest(unittest.TestCase):
    """Tests that based on one texture class."""
    def setUp(self) -> None:
        super().setUp()
        class A(Model):
            _fields = {
                'name': str,
                'age': int,
                'passed': bool
            }
            name = 'John'
            age = 10
            passed = 1
            def __init__(self, name, age, passed):
                self.name = name
                self.age = age
                self.passed = passed
        self.A = A
        
        import db
        db.open_database(":memory:")
        create_table_sql = """CREATE TABLE A (id INT PRIMARY KEY,  age INT, name TEXT, passed INT);
        """
        db.execute_commit(create_table_sql, ())
    def test_select_field_error(self):
        "Can't select a noneexisting field."
        with self.assertRaises(WrongFieldNameError):
            sql = self.A._build_query_sql(['grade'])
    
    def test_select_where_clause_field_error(self):
        "Can't select on a nonexisting field."
        with self.assertRaises(WrongFieldNameError):
            sql = self.A._build_query_sql(['name', 'age'], grade=4)
                
    def test_select_all_sql(self):
        expected = "SELECT * FROM a"
        sql, params = self.A._build_query_sql()
        self.assertEqual(sql, expected)
        self.assertEqual(params, [])
        
    def test_select_all_where_sql(self):
        expected_sql = "SELECT * FROM a WHERE age = ?"
        sql, params = self.A._build_query_sql(age=5)
        self.assertEqual(sql, expected_sql)
        self.assertEqual(params, [5])
        
    def test_select_field_where_sql(self):
        expected_sql = "SELECT name, passed FROM a WHERE age = ?"
        sql, params = self.A._build_query_sql(['name', 'passed'], age=5)
        self.assertEqual(sql, expected_sql)
        self.assertEqual(params, [5])
        
    def test_insert_sql(self):
        a = self.A("Mary", 12, True)
        expected_sql = """INSERT INTO a
        (name, age, passed)
        VALUES (?,?,?)"""
        sql = a._insert_to_db_sql(['name', 'age', 'passed'])
        self.multi_line_equal(expected_sql, sql)
    
    def test_update_sql(self):
        a = self.A("Mary", 12, True)
        a.id = 1
        sql = a._update_to_db_sql(['name', 'age'])
        expected_sql = """UPDATE a
            SET name = ?, age = ?
            WHERE id = 1
        """
        self.multi_line_equal(sql, expected_sql)
        
    def test_insert_on_first_save(self):
        a = self.A("mary", 12, True)
        original = a._insert_to_db_sql
        sql = original(['name', 'age', 'passed'])
        a._insert_to_db_sql = mock = Mock()
        mock.return_value = sql
        a.save_to_db()
        mock.assert_called()
        
    def test_update_on_later_save(self):
        a = self.A("mary", 12, True)
        a.save_to_db()
        sql = a._update_to_db_sql(['name'])
        a._update_to_db_sql = mock = Mock(return_value=sql)
        a.save_to_db(['name'])
        mock.assert_called()
        
    def multi_line_equal(self, s1, s2:str) :
        """compare multiple line strings s1 and s2
        
        Empty lines are ignored, lines are trimmed.
        """
        lines1 = [line.strip() for line in s1.splitlines()]
        lines1 = [l for l in lines1 if l]
        lines2 = [line.strip() for line in s2.splitlines()]
        lines2 = [l for l in lines2 if l]
        self.assertEqual(lines1, lines2)
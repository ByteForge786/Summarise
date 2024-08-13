import re
import unittest

def remove_column_aliases(columns, sql_query):
    # Normalize the SQL query by removing newlines and extra spaces
    sql_query = ' '.join(sql_query.split())
    
    # Extract aliases from the SQL query
    # This pattern now accounts for quoted identifiers and more complex alias structures
    alias_pattern = r'(?:(\w+|\[[^\]]+\]|\`[^\`]+\`|"[^"]+")' \
                    r'\s+(?:as\s+)?)?' \
                    r'(\w+|\[[^\]]+\]|\`[^\`]+\`|"[^"]+")\s*(?:,|$|\))'
    
    aliases = {}
    for match in re.finditer(alias_pattern, sql_query, re.IGNORECASE):
        original, alias = match.groups()
        if original and alias:
            # Remove brackets, backticks, or quotes if present
            original = re.sub(r'^[\[`"]|[\]`"]$', '', original)
            alias = re.sub(r'^[\[`"]|[\]`"]$', '', alias)
            aliases[alias.lower()] = original

    # Function to remove alias from a column name
    def remove_alias(column):
        # Remove brackets, backticks, or quotes if present
        clean_column = re.sub(r'^[\[`"]|[\]`"]$', '', column)
        return aliases.get(clean_column.lower(), column)
    
    # Apply the remove_alias function to each column
    return [remove_alias(col) for col in columns]


class TestRemoveColumnAliases(unittest.TestCase):
    def test_basic_aliases(self):
        sql_query = "SELECT customer_id, first_name as fname, last_name as lname, email_address as email FROM customers"
        columns = ['customer_id', 'fname', 'lname', 'email']
        expected = ['customer_id', 'first_name', 'last_name', 'email_address']
        self.assertEqual(remove_column_aliases(columns, sql_query), expected)

    def test_quoted_identifiers(self):
        sql_query = 'SELECT "Customer ID", "First Name" as "fname", [Last Name] as [lname], `Email Address` as `email` FROM customers'
        columns = ['Customer ID', 'fname', 'lname', 'email']
        expected = ['Customer ID', 'First Name', 'Last Name', 'Email Address']
        self.assertEqual(remove_column_aliases(columns, sql_query), expected)

    def test_case_insensitivity(self):
        sql_query = "SELECT CUSTOMER_ID, FIRST_NAME AS FNAME, last_name As Lname, email_address aS eMaIl FROM customers"
        columns = ['customer_id', 'FNAME', 'Lname', 'eMaIl']
        expected = ['CUSTOMER_ID', 'FIRST_NAME', 'last_name', 'email_address']
        self.assertEqual(remove_column_aliases(columns, sql_query), expected)

    def test_no_aliases(self):
        sql_query = "SELECT customer_id, first_name, last_name, email_address FROM customers"
        columns = ['customer_id', 'first_name', 'last_name', 'email_address']
        self.assertEqual(remove_column_aliases(columns, sql_query), columns)

    def test_subquery_and_functions(self):
        sql_query = """
        SELECT 
            c.customer_id,
            UPPER(c.first_name) as upper_fname,
            (SELECT COUNT(*) FROM orders o WHERE o.customer_id = c.customer_id) as order_count
        FROM customers c
        """
        columns = ['customer_id', 'upper_fname', 'order_count']
        expected = ['customer_id', 'UPPER(c.first_name)', '(SELECT COUNT(*) FROM orders o WHERE o.customer_id = c.customer_id)']
        self.assertEqual(remove_column_aliases(columns, sql_query), expected)

    def test_complex_query(self):
        sql_query = """
        SELECT 
            c.customer_id as "Customer ID",
            CONCAT(c.first_name, ' ', c.last_name) as full_name,
            COALESCE(c.email, 'N/A') as contact,
            (SELECT SUM(o.total) FROM orders o WHERE o.customer_id = c.customer_id) as total_spent
        FROM 
            customers c
        LEFT JOIN 
            (SELECT customer_id, COUNT(*) as order_count FROM orders GROUP BY customer_id) o
        ON 
            c.customer_id = o.customer_id
        WHERE 
            c.status = 'active'
        """
        columns = ['Customer ID', 'full_name', 'contact', 'total_spent', 'order_count']
        expected = ['c.customer_id', "CONCAT(c.first_name, ' ', c.last_name)", "COALESCE(c.email, 'N/A')", 
                    "(SELECT SUM(o.total) FROM orders o WHERE o.customer_id = c.customer_id)", 'COUNT(*)']
        self.assertEqual(remove_column_aliases(columns, sql_query), expected)


if __name__ == '__main__':
    unittest.main()

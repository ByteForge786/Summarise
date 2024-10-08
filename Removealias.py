import re

def remove_column_aliases(columns, sql_query):
    # Extract aliases from the SQL query
    alias_pattern = r'\b(\w+)\s+as\s+(\w+)\b'
    aliases = dict(re.findall(alias_pattern, sql_query, re.IGNORECASE))
    
    # Function to remove alias from a column name
    def remove_alias(column):
        for original, alias in aliases.items():
            if column.lower() == alias.lower():
                return original
        return column
    
    # Apply the remove_alias function to each column
    return [remove_alias(col) for col in columns]

# Example usage
sql_query = """
SELECT 
    customer_id,
    first_name as fname,
    last_name as lname,
    email_address as email
FROM customers
WHERE status = 'active'
"""

columns = ['customer_id', 'fname', 'lname', 'email']

result = remove_column_aliases(columns, sql_query)
print(result)




import re

def remove_column_aliases(columns, sql_query):
    # Extract aliases from the SQL query
    alias_pattern = r'\b(\w+)\s+as\s+(\w+)\b'
    aliases = dict(re.findall(alias_pattern, sql_query, re.IGNORECASE))
    
    # Function to remove alias from a column name
    def remove_alias(column):
        # If the column matches an alias, return None to indicate removal
        for original, alias in aliases.items():
            if column.lower() == alias.lower():
                return None
        return column
    
    # Apply the remove_alias function to each column, filtering out None values
    return [col for col in (remove_alias(col) for col in columns) if col]

# Example usage
sql_query = """
SELECT 
    customer_id,
    first_name AS fname,
    last_name AS lname,
    email_address AS email
FROM customers
WHERE status = 'active'
"""

columns = ['customer_id', 'fname', 'lname', 'email']

result = remove_column_aliases(columns, sql_query)
print(result)



-- Example SQL with issues

-- Issue: SELECT *
SELECT * FROM users;

-- Issue: Leading wildcard prevents index usage
SELECT name, email FROM customers
WHERE email LIKE '%@example.com';

-- Issue: Function on indexed column
SELECT user_id FROM accounts
WHERE UPPER(username) = 'ADMIN';

-- Issue: Implicit join (comma syntax)
SELECT u.name, o.total
FROM users u, orders o
WHERE u.id = o.user_id;

-- Dynamic SQL with concatenation
DECLARE @sql NVARCHAR(MAX);
SET @sql = 'SELECT * FROM users WHERE name = ''' + @username + '''';
EXEC(@sql);
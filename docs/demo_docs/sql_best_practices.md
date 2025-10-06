# SQL Best Practices

## Giới thiệu

Tài liệu này tổng hợp các best practices khi viết SQL queries để đảm bảo hiệu năng và maintainability.

## 1. Query Optimization

### 1.1 Sử dụng INDEX
- Luôn tạo index cho các columns thường dùng trong WHERE, JOIN, ORDER BY
- Tránh index quá nhiều columns (overhead khi INSERT/UPDATE)

```sql
CREATE INDEX idx_user_email ON users(email);
CREATE INDEX idx_order_date ON orders(created_date);
```

### 1.2 Tránh SELECT *
- Chỉ SELECT các columns cần thiết
- Giảm băng thông và tăng tốc query

```sql
-- Bad
SELECT * FROM users;

-- Good
SELECT id, name, email FROM users;
```

### 1.3 Sử dụng EXPLAIN
- Phân tích execution plan trước khi deploy
- Kiểm tra index có được sử dụng không

```sql
EXPLAIN SELECT * FROM orders WHERE user_id = 123;
```

## 2. JOIN Best Practices

### 2.1 Hiểu các loại JOIN
- **INNER JOIN**: Chỉ lấy rows match ở cả 2 bảng
- **LEFT JOIN**: Lấy tất cả rows bảng trái + matching bảng phải
- **RIGHT JOIN**: Tương tự LEFT JOIN nhưng ngược lại
- **FULL OUTER JOIN**: Lấy tất cả rows từ cả 2 bảng

### 2.2 Thứ tự JOIN quan trọng
- Bắt đầu với bảng nhỏ nhất
- JOIN với bảng lớn sau

## 3. Data Types

### 3.1 Chọn đúng data type
- VARCHAR cho text có độ dài biến đổi
- CHAR cho text có độ dài cố định
- INT cho numbers không có decimal
- DECIMAL cho currency/precise numbers
- DATETIME cho timestamps

### 3.2 Tránh NULL khi có thể
- Sử dụng DEFAULT values
- NULL làm queries phức tạp hơn

## 4. Transactions

### 4.1 Sử dụng ACID
- **Atomicity**: All or nothing
- **Consistency**: Dữ liệu đúng constraints
- **Isolation**: Transactions độc lập
- **Durability**: Committed data không mất

```sql
BEGIN TRANSACTION;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT;
```

## 5. Security

### 5.1 Prepared Statements
- Tránh SQL injection
- Sử dụng parameterized queries

```python
# Bad
query = f"SELECT * FROM users WHERE email = '{user_input}'"

# Good
query = "SELECT * FROM users WHERE email = ?"
cursor.execute(query, (user_input,))
```

### 5.2 Least Privilege
- Mỗi user chỉ có quyền cần thiết
- Không dùng root/admin account cho app

## 6. Maintenance

### 6.1 Regular VACUUM (PostgreSQL)
- Giải phóng space từ deleted rows
- Cập nhật statistics

### 6.2 Monitor Slow Queries
- Log queries > 1 second
- Optimize hoặc thêm index

## Tài liệu tham khảo

- [PostgreSQL Documentation](https://postgresql.org/docs)
- [MySQL Performance Tuning](https://mysql.com/performance)

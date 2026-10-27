import sqlite3

# 1. 连接到本地数据库文件（如果不存在，会自动创建）
conn = sqlite3.connect('company.db')
cursor = conn.cursor()

# 2. 创建一张名为 sales 的销售表
cursor.execute('''
CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name TEXT NOT NULL,
    category TEXT,
    sales_amount INTEGER,
    sale_date TEXT
)
''')

# 3. 清空旧数据（防止重复运行导致数据叠加）
cursor.execute("DELETE FROM sales")

# 4. 插入一些模拟数据
data = [
    ('智能手表', '电子产品', 15000, '2023-10-01'),
    ('无线耳机', '电子产品', 8500, '2023-10-02'),
    ('纯棉T恤', '服装', 3000, '2023-10-05'),
    ('机械键盘', '电子产品', 12000, '2023-10-06'),
    ('运动鞋', '服装', 15000, '2023-10-10'),
    ('高端显示器', '电子产品', 25000, '2023-10-15'),
    ('保温杯', '家居', 1500, '2023-10-20'),
    ('办公椅', '家居', 9000, '2023-10-25')
]

cursor.executemany('''
INSERT INTO sales (product_name, category, sales_amount, sale_date) 
VALUES (?, ?, ?, ?)
''', data)

# 5. 提交事务并关闭连接
conn.commit()
conn.close()

print("🎉 数据库 company.db 创建成功！已写入 8 条测试数据。")
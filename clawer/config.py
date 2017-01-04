import pymysql.cursors

config = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': 'zmf123',
    'db': 'rec',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor,
}
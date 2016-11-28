import pymysql

config = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': '123',
    'db': 'clawer',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor,
}

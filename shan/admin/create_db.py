import MySQLdb

MYSQL_HOST = 'localhost'
MYSQL_USER = 'root'
MYSQL_PASSWORD = '910417'
MYSQL_DB = 'shan'
MYSQL_PORT = 3306
MYSQL_SOCKET = '/tmp/mysql.sock'

CREATE_USER_TABLE_CMD = """
CREATE TABLE IF NOT EXISTS users (
    id INT(11) NOT NULL AUTO_INCREMENT,
    company_id INT(11) DEFAULT NULL,
    role VARCHAR(255) DEFAULT NULL,
    name VARCHAR(255) DEFAULT NULL,
    email VARCHAR(255) DEFAULT NULL,
    PRIMARY_KEY (id)
)
"""

connection = MySQLdb.connect(host=MYSQL_HOST, user=MYSQL_USER, passwd=MYSQL_PASSWORD, db=MYSQL_DB, port=MYSQL_PORT, unix_socket=MYSQL_SOCKET)
cursor = connection.cursor()
cursor.execute('CREATE TABLE')
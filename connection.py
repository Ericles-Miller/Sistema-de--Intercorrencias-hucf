import cx_Oracle
import fdb
#import kinterbasdb # para Interbase / Firebird
#Conexões Oracle
def dbamv():
    dsn = cx_Oracle.makedsn(
        'ip',
        'porta',
        service_name = 'nome'
    )
    conn = cx_Oracle.connect(
        user = 'nome_banco',
        password = 'pass',
        dsn = dsn
    )
    return conn.cursor()

def mvintegra():
    dsn = cx_Oracle.makedsn(
        'ip_database',
        'porta',
        service_name = 'nome'
    )
    conn = cx_Oracle.connect(
        user = 'nomedatabase',
        password = 'senha',
        dsn = dsn
    )
    return conn  

#Conexão com firebird
def sysdba():
    conn = fdb.connect(host="banco",database="database", user="user", password="pass")
    return conn

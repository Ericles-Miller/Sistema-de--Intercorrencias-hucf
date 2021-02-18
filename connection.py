import cx_Oracle
import fdb
#import kinterbasdb # para Interbase / Firebird
#Conexões Oracle
def dbamv():
    dsn = cx_Oracle.makedsn(
        '10.10.1.200',
        '1521',
        service_name = 'prdmv'
    )
    conn = cx_Oracle.connect(
        user = 'dbamv',
        password = 'adlo895020',
        dsn = dsn
    )
    return conn.cursor()

def mvintegra():
    dsn = cx_Oracle.makedsn(
        '10.10.1.200',
        '1521',
        service_name = 'prdmv'
    )
    conn = cx_Oracle.connect(
        user = 'mvintegra',
        password = 'dbamv',
        dsn = dsn
    )
    return conn  

#Conexão com firebird
def sysdba():
    conn = fdb.connect(host="10.10.1.94",database="/opt/firebird/sisinthucf.fdb", user="SYSDBA", password="masterkey")
    return conn

from sqlmodel import SQLModel, create_engine, Session
import urllib

sqlite_url = 'mssql+pyodbc://hearthandkin-test.database.windows.net:1433/test'



params = urllib.parse.quote_plus(r'Driver={ODBC Driver 18 for SQL Server};Server=tcp:hearthandkin-test.database.windows.net,1433;Database=test;Uid=CloudSAad9b4ab3;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;Authentication=ActiveDirectoryIntegrated')
conn_str = 'mssql+pyodbc:///?odbc_connect={}'.format(params)
engine_azure = create_engine(conn_str,echo=True)

print('connection is ok')

#connect_args = {'check_same_thread': False}

#engine = create_engine(sqlite_url, echo=False, connect_args=connect_args)

with engine_azure.connect() as connection:
    # Run the SELECT 1 query
    result = connection.execute("SELECT 1")
    # Fetch the result
    row = result.fetchone()
    # Print the result
    print(row[0])
import pyodbc

# Replace <your_username> and <your_password> with actual credentials
conn = pyodbc.connect(
    'Driver={ODBC Driver 18 for SQL Server};'
    'Server=tcp:kyanpersonalitystorage.database.windows.net,1433;'
    'Database=KyanOpenAIModel;'
    'Uid=parcival;'
    'Pwd=idontknow@86;'
    'Encrypt=yes;'
    'TrustServerCertificate=no;'
    'Connection Timeout=30;'
)

cursor = conn.cursor()
print("Connected to Azure SQL Database!")
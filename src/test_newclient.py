import oracledb
import platform

# On Linux this must be None.
# Instead, the Oracle environment must be set before Python starts.
instant_client_dir = None

# On Windows, if your database is on the same machine, comment these lines out
# and let instant_client_dir be None.  Otherwise, set this to your Instant
# Client directory.  Note the use of the raw string r"..."  so backslashes can
# be used as directory separators.
if platform.system() == "Windows":
    instant_client_dir = "D:\Programs\instantclient"

# You must always call init_oracle_client() to use thick mode in any platform
oracledb.init_oracle_client(lib_dir=instant_client_dir)

un = 'INSERT YOUR USERNAME HERE'
pw = 'INSERT YOUR PASSWORD HERE'
# also insert your connection string here with this format!
cs = """(description= (retry_count=20)(retry_delay=3)(address=(protocol=tcps)(port=............rnia, C=US")))"""

connection = oracledb.connect(user=un, password=pw, dsn=cs)
cursor = connection.cursor()
sql = """select sysdate from dual"""
for r in cursor.execute(sql):
    print(r)
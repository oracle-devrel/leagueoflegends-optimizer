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

un = 'admin'
pw = 'Welcome1#Welcome1#'
cs = """(description= (retry_count=20)(retry_delay=3)(address=(protocol=tcps)(port=1521)(host=adb.eu-frankfurt-1.oraclecloud.com))(connect_data=(service_name=g2f4dc3e5463897_esportsdb_tpurgent.adb.oraclecloud.com))(security=(ssl_server_dn_match=yes)(ssl_server_cert_dn="CN=adwc.eucom-central-1.oraclecloud.com, OU=Oracle BMCS FRANKFURT, O=Oracle Corporation, L=Redwood City, ST=California, C=US")))"""

connection = oracledb.connect(user=un, password=pw, dsn=cs)
cursor = connection.cursor()
sql = """select sysdate from dual"""
for r in cursor.execute(sql):
    print(r)
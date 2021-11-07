import os
import yaml
import cx_Oracle
os.environ['TNS_ADMIN'] = '~/wallets/Wallet_eSportsDB'



def process_yaml():
	with open("../config.yaml") as file:
		return yaml.safe_load(file)



def init_db_connection(data):
	connection = str()
	dsn_var = """(description= (retry_count=5)(retry_delay=3)(address=(protocol=tcps)(port=1522)(host=adb.eu-frankfurt-1.oraclecloud.com))(connect_data=(service_name=g2f4dc3e5463897_db202107142034_high.adb.oraclecloud.com))(security=(ssl_server_cert_dn="CN=adwc.eucom-central-1.oraclecloud.com, OU=Oracle BMCS FRANKFURT, O=Oracle Corporation, L=Redwood City, ST=California, C=US")))"""
	try:
		connection = cx_Oracle.connect(user=data['db']['username'], password=data['db']['password'], dsn=dsn_var)
		print('Connection successful.')
	except Exception:
		print('Error in connection.')
		connection = cx_Oracle.connect(user=data['db']['username'], password=data['db']['password'], dsn=dsn_var)
	connection.autocommit = True
	return connection



def main():
    data = process_yaml()
    connection = init_db_connection(data)
    print(connection)


if __name__ == '__main__':
    main()
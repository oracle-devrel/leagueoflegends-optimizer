import yaml
import os
from pathlib import Path
home = str(Path.home())
import oracledb


def process_yaml():
	with open("../config.yaml") as file:
		return yaml.safe_load(file)

# deprecated class due to old cx_Oracle library, new one is oracledb and implemented below.
'''
class OracleJSONDatabaseConnection:
    def __init__(self, data=process_yaml()):
        # wallet location (default is HOME/wallets/wallet_X)
        os.environ['TNS_ADMIN'] = '{}/{}'.format(home, process_yaml()['WALLET_DIR'])
        print(os.environ['TNS_ADMIN'])
        self.pool = cx_Oracle.SessionPool(data['db']['username'], data['db']['password'], data['db']['dsn'],
            min=1, max=4, increment=1, threaded=True,
            getmode=cx_Oracle.SPOOL_ATTRVAL_WAIT
        )
        print('Connection successful.')



    def close_pool(self):
        self.pool.close()
        print('Connection pool closed.')



    def insert(self, collection_name, json_object_to_insert):
        connection = self.pool.acquire()
        connection.autocommit = True
        soda = connection.getSodaDatabase()
        x_collection = soda.createCollection(collection_name)

        try:
            x_collection.insertOne(json_object_to_insert)
            print('[DBG] INSERT {} OK'.format(json_object_to_insert))
        except cx_Oracle.IntegrityError as e:
            print('[DBG] INSERT {} ERR: {} '.format(json_object_to_insert, e))
            return -1
        self.pool.release(connection)
        return 1



    def delete(self, collection_name, on_column, on_value):
        connection = self.pool.acquire()
        connection.autocommit = True
        soda = connection.getSodaDatabase()
        x_collection = soda.createCollection(collection_name)
        qbe = {on_column: on_value}
        x_collection.find().filter(qbe).remove()
        self.pool.release(connection)



    def get_connection(self):
        connection = self.pool.acquire()
        connection.autocommit = True
        return connection



    def close_connection(self, conn_object):
        self.pool.release(conn_object)



    def get_collection_names(self):
        connection = self.pool.acquire()
        connection.autocommit = True
        returning_object = connection.getSodaDatabase().getCollectionNames(startName=None, limit=0)
        self.pool.release(connection)
        return returning_object
'''



class OracleJSONDatabaseThinConnection:
    def __init__(self, data=process_yaml()):
        self.pool = oracledb.create_pool(user=data['db']['username'], password=data['db']['password'], dsn=data['db']['dsn'],
            min=1, max=4, increment=1, getmode=oracledb.POOL_GETMODE_WAIT)
        print('Connection successful.')


    def close_pool(self):
        self.pool.close()
        print('Connection pool closed.')


    def insert(self, collection_name, json_object_to_insert):
        connection = self.pool.acquire()
        connection.autocommit = True
        soda = connection.getSodaDatabase()
        x_collection = soda.createCollection(collection_name)

        try:
            x_collection.insertOne(json_object_to_insert)
            print('[DBG] INSERT {} OK'.format(json_object_to_insert))
        except cx_Oracle.IntegrityError as e:
            print('[DBG] INSERT {} ERR: {} '.format(json_object_to_insert, e))
            return -1
        self.pool.release(connection)
        return 1


    def delete(self, collection_name, on_column, on_value):
        connection = self.pool.acquire()
        connection.autocommit = True
        soda = connection.getSodaDatabase()
        x_collection = soda.createCollection(collection_name)
        qbe = {on_column: on_value}
        x_collection.find().filter(qbe).remove()
        self.pool.release(connection)


    def get_connection(self):
        connection = self.pool.acquire()
        connection.autocommit = True
        return connection


    def close_connection(self, conn_object):
        self.pool.release(conn_object)


    def get_collection_names(self):
        connection = self.pool.acquire()
        connection.autocommit = True
        returning_object = connection.getSodaDatabase().getCollectionNames(startName=None, limit=0)
        self.pool.release(connection)
        return returning_object

    def open_collection(self, collection_name):
        connection = self.pool.acquire()
        returning_object = self.pool.acquire().getSodaDatabase().openCollection(collection_name)
        self.pool.release(connection)
        return returning_object






class OracleJSONDatabaseThickConnection:
    def __init__(self, data=process_yaml()):
        oracledb.init_oracle_client(lib_dir=data['INSTANT_CLIENT'])
        self.pool = oracledb.create_pool(user=data['db']['username'], password=data['db']['password'], dsn=data['db']['dsn'],
            min=1, max=4, increment=1, getmode=oracledb.POOL_GETMODE_WAIT)
        print('Connection successful.')


    def close_pool(self):
        self.pool.close()
        print('Connection pool closed.')


    def insert(self, collection_name, json_object_to_insert):
        connection = self.pool.acquire()
        connection.autocommit = True
        soda = connection.getSodaDatabase()
        x_collection = soda.createCollection(collection_name)

        try:
            x_collection.insertOne(json_object_to_insert)
            print('[DBG] INSERT {} OK'.format(json_object_to_insert))
        except cx_Oracle.IntegrityError as e:
            print('[DBG] INSERT {} ERR: {} '.format(json_object_to_insert, e))
            return -1
        self.pool.release(connection)
        return 1

    def delete(self, collection_name, on_column, on_value):
        connection = self.pool.acquire()
        connection.autocommit = True
        soda = connection.getSodaDatabase()
        x_collection = soda.createCollection(collection_name)
        qbe = {on_column: on_value}
        x_collection.find().filter(qbe).remove()
        self.pool.release(connection)


    def get_connection(self):
        connection = self.pool.acquire()
        connection.autocommit = True
        return connection


    def close_connection(self, conn_object):
        self.pool.release(conn_object)


    def get_collection_names(self):
        connection = self.pool.acquire()
        connection.autocommit = True
        returning_object = connection.getSodaDatabase().getCollectionNames(startName=None, limit=0)
        self.pool.release(connection)
        return returning_object


    def open_collection(self, collection_name):
        connection = self.pool.acquire()
        returning_object = self.pool.acquire().getSodaDatabase().openCollection(collection_name)
        self.pool.release(connection)
        return returning_object



def test_class():
    object = OracleJSONDatabaseThickConnection()
    print(object.pool)
    object.close_pool()



if __name__ == '__main__':
    test_class()

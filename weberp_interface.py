import configparser
from datetime import datetime
import json
import mysql.connector as mysql
import os
import pandas as pd
from typing import List



class interface:

    database_definition = ''
    db_definition_file = 'db.def'

    def __init__(self, config_file: str = 'config.cfg'):
        config = configparser.ConfigParser()
        config.read(config_file)

        if not config.has_section('mysql'):
            raise ValueError("Configuration file must have a [mysql] section")

        host = config['mysql']['host']
        usr = config['mysql']['user']
        pwd = config['mysql']['password']
        db = config['mysql']['database']
        port = config['mysql']['port']
        self.definition_keep_alive_days = int(config['mysql']['definition_keep_alive_days'])
        self.weberp_version = config['mysql']['weberp_ver']
        self.mysql_version = config['mysql']['mysql_ver']

        self.config = {
                        'host': host,
                        'user': usr,
                        'password': pwd,
                        'database': db,
                        'port': port
                    }
        self.connection = None


    def connect(self):
        self.connection = mysql.connect(
                                        host=self.config['host'],
                                        user=self.config['user'],
                                        password=self.config['password'],
                                        database=self.config['database'],
                                        port=self.config['port']
                                        )


    def disconnect(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()


    def databasename(self):
        return self.config['database']


    def execute_query(self, query):
        df = pd.DataFrame()
        try:
            self.connect()
            #cursor = self.connection.cursor(dictionary=True)
            df = pd.read_sql(query, self.connection)
        except Exception as e:
            raise Exception(e)
        finally:
            return df


    def tablelist(self) -> List[str]:
        results = []
        self.connect()
        cursor = self.connection.cursor(dictionary=True)
        try:
            qry = open('queries/tables', 'r').read().format(**self.config)
            cursor.execute(qry.strip())
            for row in cursor.fetchall():
                results.append(f"{row['table_name']}")
        except Exception as e:
            raise Exception(f'Table list retrieval failed: {str(e)}')
        finally:
            cursor.close()
            self.disconnect()
            return results


    def execute_query_from_file(self, query_file, tablename) -> List[str]:
        results = []
        self.connect()
        cursor = self.connection.cursor(dictionary=True)
        try:
            qry = open(query_file, 'r').read().format(**{'database':self.config['database'], 'tablename':tablename})
            cursor.execute(qry.strip())
            for row in cursor:
                r = row['resultrow']
                #results.append(f' - {r}')
                results.append(r)
        except Exception as e:
            raise Exception(e)
        finally:
            cursor.close()
            self.disconnect()
            return results


    def columnslist(self, tablename) -> List[str]:
        results = []
        try:
            results = self.execute_query_from_file('queries/columns', tablename)
        except Exception as e:
            raise Exception(f'Column retrieval for table {tablename} failed:  {str(e)}')
        finally:
            return results


    def indexeslist(self, tablename) -> List[str]:
        results = []
        try:
            results = self.execute_query_from_file('queries/indexes', tablename)
        except Exception as e:
            raise Exception(f'Index retrieval for table {tablename} failed:  {str(e)}')
        finally:
            return results


    def foreignkeylist(self, tablename) -> List[str]:
        results = []
        try:
            results = self.execute_query_from_file('queries/foreignkeys', tablename)
        except Exception as e:
            raise Exception(f'Foreignkey retrieval for table {tablename} failed:  {str(e)}')
        finally:
            return results


    def __get_database_definition__(self):
        tables = []
        tbls = self.tablelist()
        for t in tbls:
            c = self.columnslist(t)
            ndxs_res = self.indexeslist(t)
            ndxs = []
            for ndx in ndxs_res:
                parts = ndx.split(' - ')
                ndxs.append({'type': parts[0], 'index_columns': parts[1]})
            fks = self.foreignkeylist(t)

            table = {'tablename': t, 'columns': c, 'indexes': ndxs, 'foreignkeys': fks}
            tables.append(table)

        databasedef = {'database': self.databasename(), 'tables': tables}

        return json.dumps(databasedef)


    def get_database_definition(self):
        readfile = False
        writefile = False

        if os.path.exists(self.db_definition_file):
            if (datetime.now() - datetime.fromtimestamp(os.path.getmtime(self.db_definition_file))).days > self.definition_keep_alive_days:
                writefile = True
            else:
                readfile = True
        else:
            writefile = True

        if readfile:
            with open(self.db_definition_file, 'r') as file:
                self.database_definition = file.read()

        if writefile:
            self.database_definition  = self.__get_database_definition__()
            with open(self.db_definition_file, 'w') as file:
                file.write(self.database_definition )

        return self.database_definition


    def __enter__(self):
        self.connect()
        return self


    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
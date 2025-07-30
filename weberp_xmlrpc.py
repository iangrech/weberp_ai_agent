import configparser
import xmlrpc.client
from socket import timeout as socket_timeout
import requests


class xmlrpcinterface:

    def __init__(self, **kwargs):

        config_file = ''
        weberpurl = ''

        xmlrcpurl = 'api/api_xml-rpc.php'

        if 'config_file' in kwargs:
            config_file = kwargs['config_file']
        if 'weberpurl' in kwargs:
            weberpurl = kwargs['weberpurl']
        if config_file=='' and weberpurl=='':
            raise ValueError('A \'config_file\' OR \'weberpurl\' parameter are required.')

        if config_file != '':
            config = configparser.ConfigParser()
            config.read(config_file)
            if not config.has_section('weberp'):
                raise ValueError('Configuration file must have a [weberp] section')
            weberpurl = config['weberp']['serverurl']

        if not weberpurl.endswith('/'):
            weberpurl+='/'

        self.server_url = weberpurl +  xmlrcpurl
        self.server = None


    def connect(self):
        try:
            self.server = xmlrpc.client.ServerProxy(self.server_url)
            self.server.system.listMethods()
            return True
        except (socket_timeout, ConnectionRefusedError) as e:
            print(f'Connection failed: {str(e)}')
        except xmlrpc.client.ProtocolError as e:
            print(f'Protocol error: {e.errmsg} (code: {e.errcode})')
        except Exception as e:
            print(f'Unexpected connection error: {str(e)}')
        return False


    def call_method(self, method_name, *args, **kwargs):
        if not self.server:
            return False, 'Not connected to server'
        try:
            method = getattr(self.server, method_name)
            if kwargs:
                result = method(*args, kwargs)
            else:
                result = method(*args)
            return True, result
        except xmlrpc.client.Fault as e:
            return False, f'Server fault: {e.faultString} (code: {e.faultCode})'
        except Exception as e:
            return False, f'Method call failed: {str(e)}'

    def get_server_methods(self):
        success, result = self.call_method("system.listMethods")
        return result if success else []

    def login(self, dbname, username, password):
        resp = self.call_method("weberp.xmlrpc_Login", dbname, username, password)
        if resp[0]==True:
            if len(resp[1])>1:
                return 1  # bad credentials
            elif resp[1][0] == 0:
                return 0  # login success
            else:
                return 2  # something else went wrong
        else:
            return -1     # connection problems with database
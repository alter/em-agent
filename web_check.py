import logging
from time_converter import TimeConverter
from io import BytesIO
import pycurl

class WebCheck:
    def __init__(self, checks={}):
        default_values = {
            'name': 'unreal-ip', 
            'url': '256.256.256.256', 
            'scheme': 'https', 
            'method': 'get', 
            'request_timeout': '3',
            'connection_timeout': '3', 
            'update_interval': '60', 
            'return_http_code': [200], 
            'arguments': '',
            'postfields': '', 
            'application_json': '', 
            'follow_redirect': ''
        }
        item = {**default_values, **checks}
        self.name = item['name'].lower()
        self.scheme = item['scheme'].lower()
        self.url = item['url']
        self.arguments = item['arguments']
        self.method = item['method'].lower()
        self.postfields = item['postfields']
        self.request_timeout = item['request_timeout'].lower()
        self.connection_timeout = item['connection_timeout'].lower()
        self.update_interval = str(item['update_interval']).lower()
        self.return_http_code = [int(code) for code in item['return_http_code']]
        self.application_json = bool(item['application_json'])
        self.follow_redirect = bool(item['follow_redirect'])
        self.success = '0'

    def get_uri(self):
        arguments = self.arguments
        scheme = self.scheme.replace('://', '')
        if self.arguments:
            arguments = '?{}'.format(self.arguments.replace('?', ''))
        return '{}://{}{}'.format(scheme, self.url, arguments)

    def make_request(self):
        b_obj = BytesIO()
        crl = pycurl.Curl()
        
        try:
            crl.setopt(crl.URL, self.get_uri())
            crl.setopt(pycurl.TIMEOUT, int(TimeConverter(self.request_timeout)))
            crl.setopt(pycurl.CONNECTTIMEOUT, int(TimeConverter(self.connection_timeout)))
            crl.setopt(pycurl.USERAGENT, 'em-agent')
            
            if self.follow_redirect:
                crl.setopt(pycurl.FOLLOWLOCATION, 1)
                
            crl.setopt(crl.WRITEDATA, b_obj)
            
            if self.application_json:
                crl.setopt(pycurl.HTTPHEADER, ['Content-Type: application/json'])
                
            if self.method == 'post':
                crl.setopt(crl.POSTFIELDS, self.postfields)

            crl.perform()
            http_code = crl.getinfo(pycurl.HTTP_CODE)
            logging.debug(f"HTTP response code for {self.name}: {http_code}")

            if http_code in self.return_http_code:
                self.success = '1'
            else:
                self.success = '0'

        except pycurl.error as e:
            logging.error(f"Error during web check {self.name}: {e}")
            self.success = '0'

        finally:
            crl.close()

        return self.success

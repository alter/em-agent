from io import BytesIO
import pycurl

class WebCheck:
    def __init__(self, checks={}):
        default_values = {'name':'unreal-ip','url':'256.256.256.256','scheme':'https','method':'get','request_timeout':'15', 'connection_timeout':'3','update_interval':'60','return_http_code':'200','arguments':'','postfields':''}
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
        self.return_http_code = int(item['return_http_code'])
        self.success = ''

    def get_uri(self):
        arguments = self.arguments
        scheme = self.scheme.replace('://','')
        if self.arguments:
            arguments = '?{}'.format(self.arguments.replace('?',''))
        return '{}://{}{}'.format(scheme, self.url, arguments)

    def make_request(self):
        if self.method == 'get':
            b_obj = BytesIO()
            crl = pycurl.Curl()
            crl.setopt(crl.URL, self.get_uri())
            crl.setopt(pycurl.TIMEOUT, int(self.time_converter(self.request_timeout)))
            crl.setopt(pycurl.CONNECTTIMEOUT, int(self.time_converter(self.connection_timeout)))
            crl.setopt(pycurl.USERAGENT, 'em-agent')
            crl.setopt(crl.WRITEDATA, b_obj)
            try:
                crl.perform()
                if crl.getinfo(pycurl.HTTP_CODE) == self.return_http_code:
                    self.success = 'OK'
                else:
                    self.success = 'FAIL'
            except pycurl.error as exc:
                self.success = 'FAIL'
                pass
            finally:
                crl.close()
        elif self.method == 'post':
            b_obj = BytesIO()
            crl = pycurl.Curl()
            crl.setopt(crl.URL, self.get_uri())
            crl.setopt(crl.POSTFIELDS, self.postfields)
            crl.setopt(pycurl.TIMEOUT, int(self.time_converter(self.request_timeout)))
            crl.setopt(pycurl.CONNECTTIMEOUT, int(self.time_converter(self.connection_timeout)))
            crl.setopt(pycurl.USERAGENT, 'em-agent')
            crl.setopt(crl.WRITEDATA, b_obj)
            try:
                crl.perform()
                if crl.getinfo(pycurl.HTTP_CODE) == self.return_http_code:
                    self.success = 'OK'
                else:
                    self.success = 'FAIL'
                    raise ValueError("Unable to reach %s (%s)" % (url, exc))
            except pycurl.error as exc:
                self.success = 'FAIL'
                pass
            finally:
                crl.close()

    def time_converter(self, unit):
        unit = str(unit)
        if 's' in unit:
            unit = unit.replace('s', '')
        elif 'm' in unit:
            unit = unit.replace('m', '')
            unit = int(unit) * 60
        elif 'h' in unit:
            unit = unit.replace('h', '')
            unit = int(unit) * 3600
        return float(unit)


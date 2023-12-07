import logging
from time_converter import TimeConverter
import nmap


class PortCheck:
    def __init__(self, checks={}):
        default_values = {'name': 'unreal-ip', 'host': '256.256.256.256',
                          'port': '65536', 'protocol': 'tcp',
                          'connection_timeout': '10', 'update_interval': '60'}
        item = {**default_values, **checks}
        self.name = item['name'].lower()
        self.host = str(item['host'])
        self.port = str(item['port'])
        self.protocol = item['protocol'].lower()
        self.connection_timeout = item['connection_timeout'].lower()
        self.update_interval = str(item['update_interval']).lower()
        self.success = '0'

    def make_request(self):
        nm = nmap.PortScanner()
        if self.protocol == 'tcp':
            proto_option = '-sT'
        elif self.protocol == 'udp':
            proto_option = '-sU'
        try:
            nm.scan(self.host, self.port, arguments='-Pn {} --host-timeout={}'.format(proto_option, TimeConverter(self.connection_timeout)))
            for host in nm.all_hosts():
                if nm[host][self.protocol][int(self.port)]['state'] == 'open':
                    self.success = '1'
                elif nm[host][self.protocol][int(self.port)]['state'] == 'open|filtered':
                    self.success = '2'
                else:
                    self.success = '0'
        except Exception as e:
            logging.error(f"Error during port check {self.name}: {e}")
            self.success = '0'
        return self.success

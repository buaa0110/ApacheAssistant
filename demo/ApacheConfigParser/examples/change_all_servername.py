import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from ApacheConfig import *

config_file = open('test_apache_config.conf', 'rb')
parsed = ApacheParser(config_file)
config_file.close()

print('==== Before Changes ====')
print(parsed.render().decode('utf-8'))
print('========================')
print('')
print('Changing subdomain1.example.com www.example.com ...')
print('')
parsed.findAll('VirtualHost').findChildren('ServerName', 'subdomain1.example.com').update('www.example.com')
print('==== After Changes ====')
print(parsed.render().decode('utf-8'))
print('=======================')

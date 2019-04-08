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
print('Disabling Indexing ...')
print('')
parsed.findAll('VirtualHost').findChildren('Directory').findChildren('Options', 'Indexes').update('-Indexes')
print('==== After Changes ====')
print(parsed.render().decode('utf-8'))
print('=======================')

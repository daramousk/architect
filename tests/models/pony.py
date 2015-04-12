from __future__ import absolute_import

import os
import datetime

from pony.orm import *
from architect import install

databases = {
    'sqlite': {'type': 'sqlite', 'args': (':memory:',), 'kwargs': {}},
    'postgresql': {'type': 'postgres', 'args': (), 'kwargs': {'user': 'postgres', 'database': 'architect'}},
    'mysql': {'type': 'mysql', 'args': (), 'kwargs': {'user': 'root', 'database': 'architect'}}
}

current = os.environ.get('DB')
db = Database(databases[current].pop('type'), *databases[current]['args'], **databases[current]['kwargs'])

# Generation of entities for date range partitioning
for item in ('day', 'week', 'month', 'year'):
    name = 'RangeDate{0}'.format(item.capitalize())
    partition = install('partition', type='range', subtype='date', range=item, column='created')

    locals()[name] = partition(type(name, (db.Entity,), {
        '_table_': 'test_rangedate{0}'.format(item),
        'name': Required(unicode),
        'created': Required(datetime.datetime),
    }))

if not os.environ.get('DB') == 'mysql':
    # Generation of entities for integer range partitioning
    for item in ('2', '5'):
        name = 'RangeInteger{0}'.format(item)
        partition = install('partition', type='range', subtype='integer', range=item, column='num')

        locals()[name] = partition(type(name, (db.Entity,), {
            '_table_': 'test_rangeinteger{0}'.format(item),
            'name': Required(unicode),
            'num': Required(int)
        }))

    # Generation of entities for string range partitioning
    for subtype in ('string_firstchars', 'string_lastchars'):
        for item in ('2', '5'):
            name = 'Range{0}{1}'.format(''.join(s.capitalize() for s in subtype.split('_')), item)
            partition = install('partition', type='range', subtype=subtype, range=item, column='title')

            locals()[name] = partition(type(name, (db.Entity,), {
                '_table_': 'test_range{0}{1}'.format(subtype, item),
                'name': Required(unicode),
                'title': Required(unicode),
            }))

db.generate_mapping(create_tables=True)

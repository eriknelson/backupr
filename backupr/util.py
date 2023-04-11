from datetime import datetime
from backupr.config import Config
from functools import reduce

def deep_get(dictionary, keys, default=None):
    return reduce(lambda d, key: \
        d.get(key, default) if isinstance(d, dict) \
        else default, keys.split("."), dictionary)

def find(predicate, seq):
    return next(filter(predicate, seq), None)

def standard_file_name(file_prefix: str):
    current_datetime = datetime.now()
    day_str = current_datetime.strftime('%m%d%y')
    time_str = current_datetime.strftime('%H%M')
    file_name = f'{file_prefix}-{day_str}-{time_str}'
    return file_name
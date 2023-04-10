import os
import tarfile
from tarfile import TarInfo
import re
from datetime import datetime
from loguru import logger

#TODO: Verify a bad value
def str_to_re_exclusion_set(re_list):
    if not re_list:
        return None
    return [re.compile(re_str) for re_str in re_list]

class TarBuilder:
    def __init__(self, src_path, output_path, backup_file_prefix, **kwargs):
        self.src_path = src_path
        self.output_path = output_path
        self.backup_file_prefix = kwargs.get('backup_file_prefix')
        self.exclusion_set = str_to_re_exclusion_set(kwargs.get('exclusion_set'))
        current_datetime = datetime.now()
        self.__day_str = current_datetime.strftime('%m%d%y')
        self.__time_str = current_datetime.strftime('%H%M')
        output_file_name = \
            f'{backup_file_prefix}-{self.__day_str}-{self.__time_str}.tar.bz2'
        self.output_file = os.path.join(self.output_path, output_file_name)

        logger.debug('TarBuilder.__Init__')
        logger.debug(f'output_path: {self.output_path}')
        logger.debug(f'backup_file_prefix: {self.backup_file_prefix}')
        logger.info(f'Output tarfile: {self.output_file}')
        logger.debug(f'From root backup path: {self.src_path}')
        if self.exclusion_set:
            logger.info('Exclusion set has been configured:')
            for exclusion in self.exclusion_set:
                logger.info(f'-> {exclusion}')

    def make_tarfile(self) -> str:
        parent_dir = os.path.dirname(self.src_path)
        leaf_dir = os.path.basename(self.src_path)
        logger.debug(f'Changing working dir to parent: {parent_dir}')
        logger.debug(f'Leaf dir: {leaf_dir}')
        working_dir = os.getcwd()
        os.chdir(str(parent_dir))

        def filter_wrapper(in_ti) -> TarInfo:
            name = in_ti.name
            return in_ti if not self.should_exclude(name) else None

        with tarfile.open(self.output_file, 'w:bz2') as tar:
            if self.exclusion_set:
                tar.add(leaf_dir, filter=filter_wrapper)
            else:
                tar.add(leaf_dir)
        os.chdir(working_dir)
        return self.output_file

    def should_exclude(self, file: str):
        def find(pred, iterable):
            return next(filter(pred, iterable), None)
        match = find(
            lambda exclusion_rx: exclusion_rx.search(str(file)), self.exclusion_set,
        )
        return match is not None

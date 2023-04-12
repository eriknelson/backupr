import os
from loguru import logger
from backupr.config import Config

def main():
    logger.debug('deep-int-test.main')
    backup_root = os.getenv('BACKUP_ROOT')
    logger.info(f'Got backup_root: {backup_root}')

if __name__ == '__main__':
    main()
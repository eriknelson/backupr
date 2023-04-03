import os
import shutil
from typing import Tuple
from loguru import logger
from backupr.storage_provider import Status

class LocalProvider():
    """IStorageProvider implementation that provides local filesystem as a
    provider"""

    def __init__(self, root_path: str):
        self.root_path = root_path

    def init(self):
        exists = os.path.exists(self.root_path)
        if not exists:
            logger.info('Root path does not exist, creating:')
            logger.info(f'{self.root_path}')
            os.makedirs(self.root_path)

    def upload(self, file: str) -> Status:
        """Uploads a file to the StorageProvider"""
        shutil.copy(file, self.root_path)

    def list_backups(self) -> Tuple[Status, list[str]]:
        """Lists the backups present in the StorageProvider"""

    def list_logfiles(self) -> Tuple[Status, list[str]]:
        """Lists the backups present in the StorageProvider"""

    def delete(self, file_id: str) -> Status:
        """Deletes a file in the StorageProvider"""

import os
import re
import time
import datetime
from loguru import logger
from kink import inject
import backupr.config as bkc
from backupr.tar_builder import TarBuilder
from backupr.encrypter import Encrypter
from backupr.storage_provider import IStorageProvider

@inject
class Engine:
    def __init__(self,
        config: bkc.Config,
        secrets: bkc.Secrets,
        tar_builder: TarBuilder,
        encrypter: Encrypter,
        provider: IStorageProvider,
    ):
        self.config = config
        self.secrets = secrets
        self.tar_builder = tar_builder
        self.encrypter = encrypter
        self.provider = provider

    def run(self):
        logger.info('Engine.run')

        # Create the scratch path if it doesn't already exist
        if not os.path.exists(self.config.scratch_path):
            logger.info('Scratch path does not already exist, creating.')
            os.makedirs(self.config.scratch_path)
            logger.info(f'Created scratch dir: {self.config.scratch_path}')
        else:
            logger.info(f'Scratch path already exists: {self.config.scratch_path}')

        logger.info('Creating tarfile.')
        maketar_start_time = time.time()
        output_tar_file = self.tar_builder.make_tarfile()
        maketar_end_time = time.time()
        maketar_timedelta = datetime.timedelta(seconds=maketar_end_time - maketar_start_time)
        logger.info(f'Created tarfile: {output_tar_file}')
        logger.info(f'Tarfile creation time: {maketar_timedelta}')

        output_tar_encrypted_file = f'{output_tar_file}.gpg'
        logger.info(f'Encrypting tarfile for recipient: {self.config.gnupg_recipient}')
        encryption_start_time = time.time()
        self.encrypter.encrypt(output_tar_file, output_tar_encrypted_file)
        encryption_end_time = time.time()
        encryption_timedelta = datetime.timedelta(
            seconds=encryption_end_time - encryption_start_time)
        logger.info(f'Successfully created encrypted tarfile: {output_tar_encrypted_file}')
        logger.info(f'Encryption time: {encryption_timedelta}')

        self.clean_scratch()

        if self.config.b2_provider_enabled:
            logger.info(f'Uploading encrypted file to provider bucket: \
                {self.config.b2_bucket_name}')
            upload_start_time = time.time()
            _, uploaded_file_url = self.provider.upload(output_tar_encrypted_file)
            upload_end_time = time.time()
            upload_timedelta = datetime.timedelta(seconds=upload_end_time - upload_start_time)
            logger.info(f'Successfully uploaded entryped tarfile: {uploaded_file_url}')
            logger.info(f'Upload time: {upload_timedelta}')
        else:
            logger.info('B2 Upload disabled, skipping upload.')

    def get_scratch_backup_list(self):
        # Capture scratch_path files so we can clean afterwards
        scratch_path_file_names = os.listdir(self.config.scratch_path)
        scratch_path_backup_files = [
            os.path.join(self.config.scratch_path, file_name) \
                for file_name in scratch_path_file_names \
                if re.match(r'.*bz2$', file_name)
        ]
        # Multiplying by -1 reverses the order to ensure that the newest are first
        scratch_path_backup_files.sort(key=lambda file_name: os.path.getmtime(file_name)*-1)
        logger.debug('Found the following backup files:')
        for file_name in scratch_path_backup_files:
            logger.debug(f'-> {file_name}')
        return scratch_path_backup_files

    def clean_scratch(self):
        logger.debug('engine.clean_scratch')
        preserved_tar_count = self.config.preserved_tars
        logger.debug(f'Preserving {preserved_tar_count} tars')
        backup_list = self.get_scratch_backup_list()
        # backup_list is an ordered list from newest -> oldest backup files
        # Popping the first N number out of the front of the list will leave us
        # with a remaining list of the files that we should clean.
        for i in range(0, preserved_tar_count):
            backup_list.pop(0)
        logger.debug('Removing files after popping the preserved files:')
        for file_name in backup_list:
            logger.debug(f'-> {file_name}')

        for file_to_remove in backup_list:
            os.remove(file_to_remove)

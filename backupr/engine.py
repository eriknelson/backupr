import os
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

        # TODO: Manage scratch path (retain 2)

        logger.info(f'Upoading encrypted file to provider bucket: {self.config.b2_bucket_name}')
        upload_start_time = time.time()
        _, uploaded_file_url = self.provider.upload(output_tar_encrypted_file)
        upload_end_time = time.time()
        upload_timedelta = datetime.timedelta(seconds=upload_end_time - upload_start_time)
        logger.info(f'Successfully uploaded entryped tarfile: {uploaded_file_url}')
        logger.info(f'Upload time: {upload_timedelta}')

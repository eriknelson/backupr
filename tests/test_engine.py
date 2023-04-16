import os
import re
import time
from pathlib import Path
import yaml
from kink import di
from loguru import logger
import backupr.config as bkc
from backupr.storage_provider import IStorageProvider
from backupr.di import init_di
from backupr.encrypter import Encrypter
from backupr.tar_builder import TarBuilder
from backupr.engine import Engine
from backupr.storage_provider.b2_provider import B2Provider
from backupr.util import find
from tests.helpers import BACKUPR_INTEGRATION_TESTS_EVK, md5
from tests.test_encrypter import TEST_PASSPHRASE

def test_engine_run(run_prep):
    int_testing = os.getenv(BACKUPR_INTEGRATION_TESTS_EVK)
    if int_testing != "true":
        return

    os.environ[bkc.BACKUPR_CONFIG_FILE_ENV_K] = run_prep.config_file
    os.environ[bkc.BACKUPR_SECRETS_FILE_ENV_K] = run_prep.secrets_file

    config, secrets = bkc.load()

    init_di(config, secrets)

    engine = Engine()
    engine.run()

    # Assert that we've gotten out what got put in
    provider = di[IStorageProvider]
    encrypter = di[Encrypter]

    remote_files = provider.list_backups()
    assert len(remote_files) == 1
    remote_file = remote_files[0]
    file_id = remote_file.id_
    file_name = remote_file.file_name
    output_file_encrypted = os.path.join(config.scratch_path, file_name)
    output_file_decrypted = output_file_encrypted.replace('.gpg', '')
    provider.download_file_by_id(file_id, output_file_encrypted)
    assert os.path.isfile(output_file_encrypted)
    encrypter.decrypt(output_file_encrypted, output_file_decrypted, TEST_PASSPHRASE)
    actual_md5 = md5(output_file_decrypted)
    assert run_prep.expected_tar_md5 == actual_md5

def test_clean_scratch(run_prep):
    int_testing = os.getenv(BACKUPR_INTEGRATION_TESTS_EVK)
    if int_testing != "true":
        return

    setup_tarfile_fixtures(run_prep)

    engine = Engine()
    engine.clean_scratch()
    backup_list = engine.get_scratch_backup_list()

    assert len(backup_list) == 2
    assert re.match(r'.*old-', backup_list[0])
    assert re.match(r'.*older-', backup_list[1])

    config = di[bkc.Config]
    all_scratch_path_files_names = os.listdir(config.scratch_path)
    gpg_files = find(lambda g: re.match(r'.*\.gpg$', g), all_scratch_path_files_names)
    assert gpg_files is None

def test_clean_bucket(run_prep):
    int_testing = os.getenv(BACKUPR_INTEGRATION_TESTS_EVK)
    if int_testing != "true":
        return

    os.environ[bkc.BACKUPR_CONFIG_FILE_ENV_K] = run_prep.config_file
    os.environ[bkc.BACKUPR_SECRETS_FILE_ENV_K] = run_prep.secrets_file
    config, secrets = bkc.load()
    init_di(config, secrets)

    provider = di[B2Provider]

    older_gpg_file = os.path.join(config.scratch_path, 'older.gpg')
    old_gpg_file = os.path.join(config.scratch_path, 'old.gpg')
    older_log_file = os.path.join(config.scratch_path, 'older.log')
    old_log_file = os.path.join(config.scratch_path, 'old.log')

    # Create the scratch path if it doesn't already exist
    if not os.path.exists(config.scratch_path):
        logger.info('Scratch path does not already exist, creating.')
        os.makedirs(config.scratch_path)
        logger.info(f'Created scratch dir: {config.scratch_path}')
    else:
        logger.info(f'Scratch path already exists: {config.scratch_path}')

    for file in [older_gpg_file, old_gpg_file, older_log_file, old_log_file]:
        Path(file).touch()
        provider.upload(file)

    remote_files = provider.list_backups()
    for remote_file in remote_files:
        logger.info(remote_file)

    engine = Engine()
    engine.clean_bucket()

    remote_files = provider.list_backups()
    assert len(remote_files) == 2
    gpg_backups = [
        remote_file for remote_file in remote_files \
            if re.match(r'.*\.gpg$', remote_file.file_name)
    ]
    log_backups = [
        remote_file for remote_file in remote_files \
            if re.match(r'.*\.log$', remote_file.file_name)
    ]
    assert len(gpg_backups) == 1
    assert len(log_backups) == 1
    assert re.match(r'.*old\.gpg', gpg_backups[0].file_name)
    assert re.match(r'.*old\.log', log_backups[0].file_name)

def test_get_scratch_backup_list(run_prep):
    int_testing = os.getenv(BACKUPR_INTEGRATION_TESTS_EVK)
    if int_testing != "true":
        return

    setup_tarfile_fixtures(run_prep)

    engine = Engine()
    backup_list = engine.get_scratch_backup_list()
    assert len(backup_list) == 3
    assert re.match(r'.*old-', backup_list[0])
    assert re.match(r'.*older-', backup_list[1])
    assert re.match(r'.*oldest-', backup_list[2])

def setup_tarfile_fixtures(_run_prep):
    os.environ[bkc.BACKUPR_CONFIG_FILE_ENV_K] = _run_prep.config_file
    os.environ[bkc.BACKUPR_SECRETS_FILE_ENV_K] = _run_prep.secrets_file

    # Create three different tarfiles of differing ages and names to test the
    # correct sorting and preservation of tars. We expect oldest prefixed tar
    # to be cleaned after the engine runs.
    set_prefix_and_create_tar('oldest', _run_prep.config_file)
    time.sleep(1) # Need to sleep becauase the sort is at a second granularity
    set_prefix_and_create_tar('older', _run_prep.config_file)
    time.sleep(1) # Need to sleep becauase the sort is at a second granularity
    set_prefix_and_create_tar('old', _run_prep.config_file)
    # Add some files to also make sure we aren't picking up any leftover gpg files
    config = di[bkc.Config]
    Path(os.path.join(config.scratch_path, 'junk.bz2.gpg')).touch()

def set_config_file_with_prefix(prefix: str, config_file: str):
    with open(config_file, 'r', encoding='utf8') as config_content:
        config_d = yaml.safe_load(config_content)
    config_d['backupFilePrefix'] = prefix
    with open(config_file, 'w', encoding='UTF-8') as _file:
        yaml.dump(config_d, _file)

# NOTE: This does call into di and reset it, so it has side effects!
def set_prefix_and_create_tar(prefix: str, config_file: str):
    set_config_file_with_prefix(prefix, config_file)
    config, secrets = bkc.load()
    if not os.path.exists(config.scratch_path):
        logger.info('Scratch path does not already exist, creating.')
        os.makedirs(config.scratch_path)
        logger.info(f'Created scratch dir: {config.scratch_path}')
    else:
        logger.info(f'Scratch path already exists: {config.scratch_path}')
    init_di(config, secrets)
    tar_builder = di[TarBuilder]
    tar_builder.make_tarfile()

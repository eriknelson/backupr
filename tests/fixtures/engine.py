import os
import yaml
import pytest
from kink import di
from munch import DefaultMunch
from loguru import logger
import backupr.config as bkc
from backupr.storage_provider.b2_provider import B2Provider
from tests.helpers import (
    get_test_paths, create_random_tarfile, md5
)
from tests.fixtures.b2 import get_raw_config_injected_b2, clean_b2_bucket
from tests.test_encrypter import gen_test_key, TEST_RECIPIENT

def create_run_test_prep(
    config_file: str,
    secrets_file: str,
    test_root_backup_dir: str,
    expected_tar_md5: str,
) -> DefaultMunch:
    return DefaultMunch.fromDict({
        'config_file': config_file,
        'secrets_file': secrets_file,
        'test_root_backup_dir': test_root_backup_dir,
        'expected_tar_md5': expected_tar_md5,
    })


@pytest.fixture
def run_prep(app_config_files, configs, secrets):
    # TODO:
    # * Initialize a basic directory of random files
    # * Get the md5 sum of that expected tarfile
    # * Setup test gnupg for encryption
    # * Create the config and secret
    # * Return the files so the env can be configured
    test_path, test_root_backup_path = get_test_paths(app_config_files)
    tarfile = create_random_tarfile(test_path, test_root_backup_path)
    expected_tar_md5 = md5(tarfile)

    config_d, secrets_d = get_raw_config_injected_b2(configs, secrets)
    config_file = str(test_path / 'config.yaml')
    secrets_file = str(test_path / 'secrets.yaml')
    scratch_dir = str(test_path / 'scratch')

    gnupghome, key = gen_test_key(test_path)
    assert key.fingerprint is not None
    # TODO: Setup log file and verify it exists

    config_d['rootBackupPath'] = str(test_root_backup_path)
    config_d['scratchPath'] = scratch_dir
    config_d['gnupgHome'] = str(gnupghome)
    config_d['gnupgRecipient'] = TEST_RECIPIENT
    del config_d['backupFilePrefix'] # Use default

    with open(str(config_file), 'w', encoding='UTF-8') as _file:
        yaml.dump(config_d, _file)
    with open(str(secrets_file), 'w', encoding='UTF-8') as _file:
        yaml.dump(secrets_d, _file)

    assert os.path.isfile(config_file)
    assert os.path.isfile(secrets_file)

    _run_prep = create_run_test_prep(config_file, secrets_file,
        str(test_root_backup_path), expected_tar_md5)

    yield _run_prep

    logger.debug('run_prep.teardown')
    # This is really redundant since this happens in the engine test, but we should
    # make sure that it's configured correctly before building the provider here
    # to clean the bucket.
    os.environ[bkc.BACKUPR_CONFIG_FILE_ENV_K] = _run_prep.config_file
    os.environ[bkc.BACKUPR_SECRETS_FILE_ENV_K] = _run_prep.secrets_file

    config, secrets = bkc.load()

    di[bkc.Config] = config
    di[bkc.Secrets] = secrets
    provider = B2Provider()

    clean_b2_bucket(provider)

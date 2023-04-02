import os
import yaml
# pylint: disable=no-name-in-module
from pydantic import SecretStr
# pylint: enable=no-name-in-module
from munch import DefaultMunch
from backupr.util import find

from backupr.config import (
    Config, Secrets, BACKUPR_CONFIG_FILE_ENV_K, BACKUPR_SECRETS_FILE_ENV_K,
)
import backupr.config as backupr_config_mod

def test_valid_config(configs: dict[str, str]):
    valid_config = configs['example_config.yaml']
    expected_config_d = yaml.safe_load(valid_config)

    actual_config = Config.parse_raw(valid_config)
    assert_valid_config(actual_config, expected_config_d)

def assert_valid_config(actual_config: Config, expected_config_d):
    assert actual_config.root_backup_path == expected_config_d['rootBackupPath']
    assert actual_config.scratch_path == expected_config_d['scratchPath']
    assert actual_config.preserved_tars == expected_config_d['preservedTars']
    assert actual_config.backup_file_prefix == expected_config_d['backupFilePrefix']

    # TODO: Assert the exclusion set values

    assert actual_config.gnupg_home == expected_config_d['gnupgHome']
    assert actual_config.gnupg_recipient == expected_config_d['gnupgRecipient']
    assert actual_config.b2_provider_enabled == expected_config_d['b2ProviderEnabled']
    assert actual_config.b2_bucket_name == expected_config_d['b2BucketName']

def test_valid_secrets(secrets: dict[str, str]):
    valid_secrets = secrets['example_secrets.yaml']
    expected_secrets_d = yaml.safe_load(valid_secrets)
    actual_secrets = Secrets.parse_raw(valid_secrets)
    assert_valid_secrets(actual_secrets, expected_secrets_d)

def assert_valid_secrets(secrets: Secrets, expected_secrets_d):
    assert secrets.b2_bucket_api_key_id == \
        SecretStr(expected_secrets_d['b2BucketApiKeyId'])
    assert secrets.b2_bucket_api_key == \
        SecretStr(expected_secrets_d['b2BucketApiKey'])

def test_valid_load(app_config_files: DefaultMunch):
    config_files  = app_config_files.config_files
    config_file = find(lambda f: 'example_config.yaml' in f, config_files)
    with open(config_file, 'r', encoding='utf8') as file:
        expected_config_d = yaml.safe_load(file)

    secrets_files = app_config_files.secrets_files
    secrets_file = find(lambda f: 'example_secrets.yaml' in f, secrets_files)
    with open(secrets_file, 'r', encoding='utf8') as file:
        expected_secrets_d = yaml.safe_load(file)

    os.environ[BACKUPR_CONFIG_FILE_ENV_K] = config_file
    os.environ[BACKUPR_SECRETS_FILE_ENV_K] = secrets_file

    actual_config, actual_secrets = backupr_config_mod.load()

    assert_valid_config(actual_config, expected_config_d)
    assert_valid_secrets(actual_secrets, expected_secrets_d)

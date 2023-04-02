import yaml
from pydantic import SecretStr

from backupr.config import (
    Config, Secrets
)

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

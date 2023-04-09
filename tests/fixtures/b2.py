import os
import yaml
import pytest
from kink import di
from backupr.config import Config, Secrets
import backupr.storage_provider.b2_provider as b2p
from tests.helpers import random_flat_file_tree, get_test_paths

KEY_B2_PROVIDER_ENABLED = 'b2ProviderEnabled'
KEY_B2_BUCKET_NAME = 'b2BucketName'
KEY_B2_APPLICATION_KEY_ID = 'b2BucketApiKeyId'
KEY_B2_APPLICATION_KEY = 'b2BucketApiKey'

@pytest.fixture
def initial_b2_bucket(app_config_files, configs, secrets):
    _config, _secrets = get_config_injected_b2(configs, secrets)

    di[Config] = _config
    di[Secrets] = _secrets

    test_path, test_root_backup_path = get_test_paths(app_config_files)
    file_count = 0
    while file_count == 0:
        random_flat_file_tree(str(test_root_backup_path))
        file_count = len(os.listdir(test_root_backup_path))

    test_files = [
        os.path.join(test_root_backup_path, file) for file
        in os.listdir(test_root_backup_path)
    ]
    assert len(test_files) != 0

    b2 = b2p.B2Provider()
    expected_b2_files = [b2.upload(tfile)[0] for tfile in test_files]

    ret_obj = {
        'expected_b2_files': expected_b2_files,
        'config': _config,
        'secrets': _secrets,
    }

    # NOTE: Yields the fixture to the test, and then allows for tearing down
    # after the yield.
    yield ret_obj

    # Cleanup the bucket
    for remote_file in expected_b2_files:
        b2.delete(remote_file.id_, remote_file.file_name)

def get_config_injected_b2(configs: dict[str, str], secrets: dict[str, str]):
    config_content = configs['example_config.yaml']
    secrets_content = secrets['example_secrets.yaml']
    config_d = yaml.safe_load(config_content)
    secrets_d = yaml.safe_load(secrets_content)

    bucket_name = os.getenv(b2p.B2_BUCKET_NAME_EVK)
    application_key_id = os.getenv(b2p.B2_APPLICATION_KEY_ID_EVK)
    application_key = os.getenv(b2p.B2_APPLICATION_KEY_EVK)
    provider_enabled = None not in (bucket_name, application_key_id, application_key)

    assert bucket_name
    assert provider_enabled
    assert application_key_id
    assert application_key

    config_d[KEY_B2_PROVIDER_ENABLED] = provider_enabled
    config_d[KEY_B2_BUCKET_NAME] = bucket_name
    secrets_d[KEY_B2_APPLICATION_KEY_ID] = application_key_id
    secrets_d[KEY_B2_APPLICATION_KEY] = application_key

    return (Config.parse_obj(config_d), Secrets.parse_obj(secrets_d))
import os
import yaml
import pytest
from kink import di
from loguru import logger
from backupr.config import Config, Secrets
import backupr.storage_provider.b2_provider as b2p
from tests.conftest import fix_dat_path

upload_fix_dat_path = os.path.join(fix_dat_path, 'upload')

KEY_B2_PROVIDER_ENABLED = 'b2ProviderEnabled'
KEY_B2_BUCKET_NAME = 'b2BucketName'
KEY_B2_APPLICATION_KEY_ID = 'b2BucketApiKeyId'
KEY_B2_APPLICATION_KEY = 'b2BucketApiKey'

@pytest.fixture
def initial_b2_bucket(configs, secrets):
    _config, _secrets = get_config_injected_b2(configs, secrets)

    di[Config] = _config
    di[Secrets] = _secrets

    upload_file_names = os.listdir(upload_fix_dat_path)
    upload_file_paths = [os.path.join(upload_fix_dat_path, fname) for fname in upload_file_names]

    provider = b2p.B2Provider()
    expected_b2_files = [provider.upload(tfile)[0] for tfile in upload_file_paths]

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
        provider.delete(remote_file.id_, remote_file.file_name)

def get_raw_config_injected_b2(
    configs: dict[str, str],
    secrets: dict[str, str],
    config_file_name = 'example_config.yaml',
    secrets_file_name = 'example_secrets.yaml',
):
    config_content = configs[config_file_name]
    secrets_content = secrets[secrets_file_name]
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

    return config_d, secrets_d

def get_config_injected_b2(configs: dict[str, str], secrets: dict[str, str]):
    config_d, secrets_d = get_raw_config_injected_b2(configs, secrets)
    return (Config.parse_obj(config_d), Secrets.parse_obj(secrets_d))

def clean_b2_bucket(provider: b2p.B2Provider):
    logger.debug('fixtures.b2.clean_b2_bucket')
    remote_files = provider.list_backups()
    for remote_file in remote_files:
        logger.debug(f'Cleaning file: {remote_file.file_name} from bucket')
        provider.delete(remote_file.id_, remote_file.file_name)

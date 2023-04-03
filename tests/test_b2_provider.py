import os
import yaml
from kink import di
from loguru import logger
from backupr.storage_provider import b2_provider as b2p
from backupr.config import Config, Secrets
from tests.helpers import (
    get_test_paths, BACKUPR_INTEGRATION_TESTS_EVK,
    create_random_tarfile,
)

KEY_B2_PROVIDER_ENABLED = 'b2ProviderEnabled'
KEY_B2_BUCKET_NAME = 'b2BucketName'
KEY_B2_APPLICATION_KEY_ID = 'b2BucketApiKeyId'
KEY_B2_APPLICATION_KEY = 'b2BucketApiKey'

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

def test_b2_provider_upload(
    app_config_files,
    configs: dict[str, str],
    secrets: dict[str, str]
):
    # Autopass if integration testing not enabled
    int_testing = os.getenv(BACKUPR_INTEGRATION_TESTS_EVK)
    if int_testing != "true":
        return

    config, secrets = get_config_injected_b2(configs, secrets)
    di[Config] = config
    di[Secrets] = secrets

    test_path, test_root_backup_path = get_test_paths(app_config_files)
    tarfile = create_random_tarfile(test_path, test_root_backup_path)

    provider = b2p.B2Provider()

    _, uploaded_file_url = provider.upload(tarfile)

    logger.info(uploaded_file_url)
    assert uploaded_file_url

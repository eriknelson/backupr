import glob
import os
from pathlib import Path
import yaml
from kink import di
from loguru import logger
import backupr.config as bconf
from backupr.tar_builder import TarBuilder
from backupr.storage_provider import b2_provider as b2p
from tests.helpers import (
    get_test_paths, random_file_tree, BACKUPR_INTEGRATION_TEST_EVK
)
from backupr.config import Config, Secrets

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
    provider_enabled = bucket_name and application_key_id and application_key

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
    int_testing = os.getenv(BACKUPR_INTEGRATION_TEST_EVK)
    if int_testing != "true":
        return

    config, secrets = get_config_injected_b2(configs, secrets)
    di[Config] = config
    di[Secrets] = secrets

    test_path, test_root_backup_path = get_test_paths(app_config_files)

    random_file_tree(str(test_root_backup_path))
    tar_builder = TarBuilder(
        str(test_root_backup_path), str(test_path), 'backupr'
    )
    tar_builder.make_tarfile()
    result = glob.glob(str(test_path / 'backupr-*'), recursive=False)
    assert len(result) == 1
    tarfile = result[0]
    tarfile_name = os.path.basename(tarfile)

    provider = b2p.B2Provider()

    uploaded_file, uploaded_file_url = provider.upload(tarfile)

    logger.info(uploaded_file_url)
    assert uploaded_file_url

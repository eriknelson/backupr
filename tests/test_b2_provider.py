import os
from kink import di
from backupr.storage_provider import b2_provider as b2p
from backupr.config import Config, Secrets
from tests.helpers import (
    get_test_paths, BACKUPR_INTEGRATION_TESTS_EVK,
    create_random_tarfile,
)
from tests.fixtures.b2 import get_config_injected_b2

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

    uploaded_file, uploaded_file_url = provider.upload(tarfile)

    assert uploaded_file_url
    provider.delete(uploaded_file.id_, uploaded_file.file_name)

def test_b2_provider_list(
    initial_b2_bucket,
):
    # Autopass if integration testing not enabled
    int_testing = os.getenv(BACKUPR_INTEGRATION_TESTS_EVK)
    if int_testing != "true":
        return

    expected_b2_files = initial_b2_bucket['expected_b2_files']

    provider = b2p.B2Provider()
    actual_files = provider.list_backups()
    assert len(expected_b2_files) != 0
    assert len(actual_files) != 0
    assert len(expected_b2_files) == len(actual_files)

    expected_file_names = {file.file_name for file in expected_b2_files}
    actual_file_names = {file.file_name for file in actual_files}
    assert expected_file_names == actual_file_names

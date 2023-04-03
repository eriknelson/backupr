import os
from pathlib import Path
from backupr.storage_provider.local_provider import LocalProvider
from tests.helpers import get_test_paths, create_random_tarfile

def get_provider_path(test_path: Path):
    return test_path / 'local_provider'

def test_local_provider_upload(app_config_files):
    test_path, test_root_backup_path = get_test_paths(app_config_files)
    provider_path = get_provider_path(test_path)

    local_provider = LocalProvider(provider_path)
    local_provider.init()
    assert os.path.exists(provider_path)

    tarfile = create_random_tarfile(test_path, test_root_backup_path)
    tarfile_name = os.path.basename(tarfile)

    local_provider.upload(tarfile)
    expected_upload_file = provider_path / tarfile_name
    assert os.path.exists(expected_upload_file)

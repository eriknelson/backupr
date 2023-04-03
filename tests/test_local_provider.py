import glob
import os
from pathlib import Path
from backupr.tar_builder import TarBuilder
from backupr.storage_provider.local_provider import LocalProvider
from tests.helpers import random_file_tree, get_test_paths

def get_provider_path(test_path: Path):
    return test_path / 'local_provider'

def test_local_provider_upload(app_config_files):
    test_path, test_root_backup_path = get_test_paths(app_config_files)
    provider_path = get_provider_path(test_path)

    local_provider = LocalProvider(provider_path)
    local_provider.init()
    assert os.path.exists(provider_path)

    random_file_tree(str(test_root_backup_path))
    tar_builder = TarBuilder(
        str(test_root_backup_path), str(test_path), 'backupr'
    )
    tar_builder.make_tarfile()
    result = glob.glob(str(test_path / 'backupr-*'), recursive=False)
    assert len(result) == 1
    tarfile = result[0]
    tarfile_name = os.path.basename(tarfile)

    local_provider.upload(tarfile)
    expected_upload_file = provider_path / tarfile_name
    assert os.path.exists(expected_upload_file)

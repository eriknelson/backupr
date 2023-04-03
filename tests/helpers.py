import os
import hashlib
from pathlib import Path
import randomfiletree
from backupr.util import find

BACKUPR_INTEGRATION_TEST_EVK = 'BACKUPR_INTEGRATION_TEST'

def random_file_tree(output_path) -> None:
    randomfiletree.iterative_gaussian_tree(
        output_path, nfiles=4.0, nfolders=2.0, maxdepth=3, repeat=2,
    )

def md5(file: str) -> str:
    hash_md5 = hashlib.md5()
    with open(file, 'rb') as _file:
        for chunk in iter(lambda: _file.read(4096), b''):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def get_test_paths(app_config_files):
    config_files  = app_config_files.config_files
    config_file = find(lambda f: 'example_config.yaml' in f, config_files)
    backup_dir_name = 'backup_path'
    test_path = Path(os.path.dirname(config_file))
    test_root_backup_path = test_path / backup_dir_name
    return (test_path, test_root_backup_path)

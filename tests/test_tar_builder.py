import os
import tarfile
import glob
import re
import random
from pathlib import Path
from datetime import datetime
import yaml
from backupr.config import (
    Config,
)
from backupr.tar_builder import TarBuilder
from backupr.util import find
from tests.helpers import random_file_tree, md5

BACKUP_FILE_PREFIX_K = 'backupFilePrefix'
EXCLUSION_SET_K = 'exclusionSet'

def get_config_d(config_content: str):
    return yaml.safe_load(config_content)

def test_output_file_no_prefix(configs: dict[str, str]):
    config_d = get_config_d(configs['example_config.yaml'])
    del config_d[BACKUP_FILE_PREFIX_K]
    config = Config.parse_raw(yaml.dump(config_d))
    current_datetime = datetime.now()
    day_str = current_datetime.strftime('%m%d%y')
    time_str = current_datetime.strftime('%H%M')
    # I'm deliberately not using the DEFAULT_BACKUP_FILE_PREFIX here, because
    # I want to verify that the value is actually backupr, which is claimed in
    # the docs to be the default prefix.
    output_file_name = f'backupr-{day_str}-{time_str}.tar.bz2'
    output_file = os.path.join(config.scratch_path, output_file_name)

    tar_builder = TarBuilder(
        config.root_backup_path, config.scratch_path, config.backup_file_prefix)
    assert output_file == tar_builder.output_file

def test_output_file_prefix_override(configs: dict[str, str]):
    config_d = get_config_d(configs['example_config.yaml'])
    prefix_override = 'testprefix'
    config_d[BACKUP_FILE_PREFIX_K] = prefix_override
    config = Config.parse_raw(yaml.dump(config_d))
    current_datetime = datetime.now()
    day_str = current_datetime.strftime('%m%d%y')
    time_str = current_datetime.strftime('%H%M')
    output_file_name = f'{prefix_override}-{day_str}-{time_str}.tar.bz2'
    output_file = os.path.join(config.scratch_path, output_file_name)

    tar_builder = TarBuilder(
        config.root_backup_path, config.scratch_path, config.backup_file_prefix)
    assert output_file == tar_builder.output_file

def test_make_tarfile(tmp_config_file):
    backup_dir_name = 'backup_path'
    test_path = Path(os.path.dirname(tmp_config_file))
    test_root_backup_path = test_path / backup_dir_name
    known_output_file = test_path / 'known.tar.bz2'
    known_output_file_str = str(known_output_file)
    random_file_tree(str(test_root_backup_path))

    working_dir = os.getcwd()
    os.chdir(str(test_path))
    with tarfile.open(known_output_file_str, 'w:bz2') as tar:
        tar.add(backup_dir_name)
    os.chdir(working_dir)

    known_md5 = md5(known_output_file_str)

    tar_builder = TarBuilder(
        str(test_root_backup_path), str(test_path), 'backupr',
    )
    tar_builder.make_tarfile()

    result = glob.glob(str(test_path / 'backupr-*'), recursive=False)
    assert len(result) == 1
    actual_file = result[0]
    actual_md5 = md5(actual_file)
    assert actual_md5 == known_md5

def test_should_exclude_does_exclude(configs: dict[str, str]):
    config_d = get_config_d(configs['example_config.yaml'])

    test_file_str = '/git/src/github.com/eriknelson/vendor/dependent-project'
    test_exclusion_set = ['derp', '\\/vendor\\/']

    config_d[EXCLUSION_SET_K] = test_exclusion_set
    config = Config.parse_raw(yaml.dump(config_d))
    tar_builder = TarBuilder(
        config.root_backup_path,config.scratch_path,
        config.backup_file_prefix, exclusion_set=test_exclusion_set,
    )
    assert tar_builder.should_exclude(test_file_str)

def test_correct_yaml_file_exclude_value(configs: dict[str, str]):
    config_d = get_config_d(configs['excludes_test.yaml'])

    test_file_str = '/git/src/github.com/eriknelson/vendor/dependent-project'

    config = Config.parse_raw(yaml.dump(config_d))
    tar_builder = TarBuilder(
        config.root_backup_path,config.scratch_path,
        config.backup_file_prefix, exclusion_set=config_d[EXCLUSION_SET_K],
    )
    assert tar_builder.should_exclude(test_file_str)

def test_should_exclude_does_not_exclude(configs: dict[str, str]):
    test_file_str = '/git/src/github.com/eriknelson/vendor/dependent-project'
    test_exclusion_set = ['derp', '\\/vendorr\\/']
    config_d = get_config_d(configs['example_config.yaml'])

    config_d[EXCLUSION_SET_K] = test_exclusion_set
    config = Config.parse_raw(yaml.dump(config_d))

    tar_builder = TarBuilder(
        config.root_backup_path,config.scratch_path,
        config.backup_file_prefix, exclusion_set=test_exclusion_set,
    )
    assert not tar_builder.should_exclude(test_file_str)

def test_files_are_excluded(app_config_files):
    config_files  = app_config_files.config_files
    config_file = find(lambda f: 'example_config.yaml' in f, config_files)
    with open(config_file, 'r', encoding='utf8') as file:
        expected_config_d = yaml.safe_load(file)

    backup_dir_name = 'backup_path'
    test_path = Path(os.path.dirname(config_file))
    test_root_backup_path = test_path / backup_dir_name
    random_file_tree(str(test_root_backup_path))

    # List files in random file tree and pick one to exclude
    backup_path_str = os.path.join(str(test_root_backup_path),'**/*')
    files = glob.glob(backup_path_str, recursive=True)
    exclude_full_file = random.choice(files)
    exclude_file_name = Path(exclude_full_file).name

    # Build a cofnig with the exclusion set
    expected_config_d[EXCLUSION_SET_K] = [exclude_file_name]
    config = Config.parse_raw(yaml.dump(expected_config_d))

    tar_builder = TarBuilder(
        str(test_root_backup_path), str(test_path),
        'backupr', exclusion_set=config.exclusion_set,
    )
    tar_builder.make_tarfile()
    result = glob.glob(str(test_path / 'backupr-*'), recursive=False)
    assert len(result) == 1

    # Now we're going to assert that the excluded file is not present in the tar
    with tarfile.open(result[0], 'r:*') as file:
        names = file.getnames()
        assert len(names) != 0
        exclusion_rx = re.compile(exclude_file_name)
        for name in names:
            assert not exclusion_rx.search(name)

import os
import shutil
import yaml
import pytest
from munch import DefaultMunch

fix_dat_path = os.path.join(os.path.dirname(
    os.path.realpath(__file__)), 'fix_dat')
configs_fix_path = os.path.join(fix_dat_path, 'configs')
# NOTE: They're currently one in the same right now but potentially can
# be split out in the future.
secrets_fix_path = configs_fix_path

pytest_plugins = [
    'tests.fixtures.b2',
    'tests.fixtures.engine',
]

@pytest.fixture
def configs() -> dict[str, str]:
    ret_dat = {}
    config_fixture_files = os.listdir(configs_fix_path)
    for file in config_fixture_files:
        file_path = os.path.join(configs_fix_path, file)
        with open(file_path, 'r', encoding='utf8') as config_file:
            ret_dat[file] = config_file.read()
    return ret_dat

@pytest.fixture
def secrets() -> dict[str, str]:
    ret_dat = {}
    secrets_fixture_files = os.listdir(secrets_fix_path)
    for file in secrets_fixture_files:
        file_path = os.path.join(secrets_fix_path, file)
        with open(file_path, 'r', encoding='utf8') as secret_file:
            ret_dat[file] = secret_file.read()
    return ret_dat

@pytest.fixture
def app_config_files(tmp_path) -> DefaultMunch:
    dest = tmp_path / 'app_config'
    shutil.copytree(configs_fix_path, dest)
    # NOTE: Need to do this in the future if the secrets get split out
    # shutil.copytree(secrets_fix_path, tmp_path)

    config_files = [
        os.path.join(dest, f) for f in os.listdir(dest) if 'config' in f
    ]
    secrets_files = [
        os.path.join(dest, f) for f in os.listdir(dest) if 'secret' in f
    ]

    return DefaultMunch.fromDict({
        'config_files': config_files,
        'secrets_files': secrets_files,
    })

T_CONFIG_FILE_NAME = 'backupr.config.yml'

@pytest.fixture
# pylint: disable=redefined-outer-name
def tmp_config_file(tmp_path, configs):
# pylint: enable=redefined-outer-name
    config_content = configs['example_config.yaml']
    config_d = yaml.safe_load(config_content)
    _config_file = tmp_path / T_CONFIG_FILE_NAME
    with open(_config_file, 'w', encoding='UTF-8') as file:
        yaml.dump(config_d, file)
    return _config_file

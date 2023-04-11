import os
from pathlib import Path
from kink import di
from click.testing import CliRunner
from backupr.cli import cli
from backupr.storage_provider import IStorageProvider
from backupr.util import find
import backupr.config as bkc
from tests.helpers import BACKUPR_INTEGRATION_TESTS_EVK

def test_cli_run(run_prep):
    int_testing = os.getenv(BACKUPR_INTEGRATION_TESTS_EVK)
    if int_testing != "true":
        return

    test_root_backup_dir = run_prep.test_root_backup_dir
    test_path = Path(os.path.dirname(test_root_backup_dir))
    log_dir = str(test_path / 'logs')
    os.makedirs(log_dir)

    os.environ[bkc.BACKUPR_CONFIG_FILE_ENV_K] = run_prep.config_file
    os.environ[bkc.BACKUPR_SECRETS_FILE_ENV_K] = run_prep.secrets_file

    runner = CliRunner()
    runner.invoke(cli, [f'--log-dir={log_dir}', 'run'])

    provider = di[IStorageProvider]
    remote_files = provider.list_backups()
    actual_remote_log = find(lambda f: 'log' in f, [
        remote_file.file_name for remote_file in remote_files
    ])
    assert actual_remote_log is not None
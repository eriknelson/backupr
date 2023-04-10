import os
from kink import di
from backupr.engine import Engine
import backupr.config as bkc
from backupr.tar_builder import TarBuilder
from backupr.encrypter import Encrypter
from backupr.storage_provider import IStorageProvider
from backupr.storage_provider.b2_provider import B2Provider
from tests.helpers import BACKUPR_INTEGRATION_TESTS_EVK

def test_engine_run(run_prep):
    int_testing = os.getenv(BACKUPR_INTEGRATION_TESTS_EVK)
    if int_testing != "true":
        return

    os.environ[bkc.BACKUPR_CONFIG_FILE_ENV_K] = run_prep.config_file
    os.environ[bkc.BACKUPR_SECRETS_FILE_ENV_K] = run_prep.secrets_file

    config, secrets = bkc.load()

    di[bkc.Config] = config
    di[bkc.Secrets] = secrets
    di[TarBuilder] = TarBuilder(
        config.root_backup_path, config.scratch_path,
        config.backup_file_prefix, exclusion_set=config.exclusion_set,
    )
    di[Encrypter] = Encrypter(config.gnupg_home, config.gnupg_recipient)
    di[IStorageProvider] = B2Provider()

    engine = Engine()
    engine.run()

import os
from kink import di
from backupr.engine import Engine
import backupr.config as bkc
from backupr.tar_builder import TarBuilder
from backupr.encrypter import Encrypter
from backupr.storage_provider import IStorageProvider
from backupr.storage_provider.b2_provider import B2Provider
from tests.helpers import BACKUPR_INTEGRATION_TESTS_EVK, md5
from tests.test_encrypter import TEST_PASSPHRASE

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
    encrypter = Encrypter(config.gnupg_home, config.gnupg_recipient)
    di[Encrypter] = encrypter
    provider = B2Provider()
    di[IStorageProvider] = provider

    engine = Engine()
    engine.run()

    # Assert that we've gotten out what got put in
    remote_files = provider.list_backups()
    assert len(remote_files) == 1
    remote_file = remote_files[0]
    file_id = remote_file.id_
    file_name = remote_file.file_name
    output_file_encrypted = os.path.join(config.scratch_path, file_name)
    output_file_decrypted = output_file_encrypted.replace('.gpg', '')
    provider.download_file_by_id(file_id, output_file_encrypted)
    assert os.path.isfile(output_file_encrypted)
    encrypter.decrypt(output_file_encrypted, output_file_decrypted, TEST_PASSPHRASE)
    actual_md5 = md5(output_file_decrypted)
    assert run_prep.expected_tar_md5 == actual_md5

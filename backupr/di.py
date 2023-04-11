from kink import di
import backupr.config as bkc
from backupr.tar_builder import TarBuilder
from backupr.encrypter import Encrypter
from backupr.storage_provider.b2_provider import B2Provider
from backupr.storage_provider import IStorageProvider

def init_di(config: bkc.Config, secrets: bkc.Secrets):
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

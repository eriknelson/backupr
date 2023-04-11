import click
from kink import di
from loguru import logger
import backupr.config as bkc
from backupr.storage_provider import IStorageProvider
from backupr.storage_provider.b2_provider import B2Provider
from backupr.encrypter import Encrypter
from backupr.tar_builder import TarBuilder
from backupr engine import Engine

@click.group()
def cli():
    logger.debug('backupr.cli')
    config, secrets = bkc.load()
    di[bkc.Config] = config
    di[bkc.Secrets] = secrets
    di[TarBuilder] = TarBuilder(
        config.root_backup_path, config.scratch_path,
        config.backup_file_prefix, exclusion_set=config.exclusion_set,
    )
    # TODO: Need to consider gnupg home here?
    encrypter = Encrypter(config.gnupg_home, config.gnupg_recipient)
    di[Encrypter] = encrypter
    provider = B2Provider()
    di[IStorageProvider] = provider

@cli.command()
def run():
    engine = Engine()
    engine.run()


def main():
    cli()

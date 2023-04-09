import click
from kink import di
from loguru import logger
import backupr.config as bkc
from backupr.storage_provider import IStorageProvider
from backupr.storage_provider.b2_provider import B2Provider

@click.group()
def cli():
    logger.debug('backupr.cli')
    config, secrets = bkc.load()
    di[bkc.Config] = config
    di[bkc.Secrets] = secrets
    di[IStorageProvider] = B2Provider()

@cli.command()
def run():
    logger.info('backupr.run executing.')

def main():
    cli()
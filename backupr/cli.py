import os
import click
from kink import di
from loguru import logger
import backupr.config as bkc
from backupr.storage_provider import IStorageProvider
from backupr.engine import Engine
from backupr.di import init_di

DEFAULT_LOG_DIR='/var/log/backupr'
LOG_FILE_BASENAME='backupr.log'

@click.group()
@click.option('-l', '--log-dir', default=DEFAULT_LOG_DIR, show_default=True,
    help='The directory where backupr log files will be written.')
@click.pass_context
def cli(ctx, log_dir):
    ctx.ensure_object(dict)
    if not os.path.exists(log_dir):
        os.makedirs(str(log_dir))

    # Setup the log file
    log_file = os.path.join(log_dir, LOG_FILE_BASENAME)
    logger.add(log_file, retention=1)

    logger.debug('backupr.cli')
    config, secrets = bkc.load()
    init_di(config, secrets)
    ctx.obj['log_file'] = log_file

@cli.command()
@click.pass_context
def run(ctx):
    logger.info('cli.run')
    engine = Engine()
    engine.run()
    provider = di[IStorageProvider]

    log_file = ctx.obj['log_file']
    provider.upload(log_file)

def main():
    cli()

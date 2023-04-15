import os
import re
import yaml
from kink import di
from loguru import logger
import docker
import backupr.config as bkc
from backupr.util import find
from backupr.storage_provider.b2_provider import B2Provider
from backupr.encrypter import Encrypter
from tests.test_encrypter import gen_test_key, TEST_PASSPHRASE
from tests.helpers import random_file_tree, md5
from tests.fixtures.b2 import clean_b2_bucket

GNUPG_RECIPIENT = 'duder@duderington.com'

CONTAINER_ROOT_BACKUP_DIR = '/backupr/root_backup_path'
CONTAINER_SCRATCH_BACKUP_DIR = '/backupr/scratch_patch'
CONTAINER_CONFIG_DIR = '/backupr/config'
CONTAINER_GNUPGHOME = '/backupr/gnupg'
CONTAINER_LOG_PATH = '/backupr/logs'

EXPECTED_UID = 2002
EXPECTED_GID = EXPECTED_UID
EXPECTED_MODE = 0o666
EXPECTED_MODE_DIR = 0o777

FQIN = os.getenv('BACKUPR_DEEP_INT_TEST_FQIN') or \
    'ghcr.io/eriknelson/backupr:main'

# pylint: disable=too-many-statements
def test_preserved_file_permissions(tmp_path):
    logger.debug('deep-int-test.main')

    project_root = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', '..')
    config_src_dir = os.path.join(project_root, 'config')
    config_src_file = os.path.join(config_src_dir, 'config.yaml.ex')
    secrets_src_file = os.path.join(config_src_dir, 'secrets.yaml.ex')

    # Initiaize test dirs
    logger.debug(f'tmp_path: {tmp_path}')
    backup_root_dir = os.path.join(tmp_path, 'backup_root')
    config_dest_dir = os.path.join(tmp_path, 'config')
    scratch_dir = os.path.join(tmp_path, 'scratch')
    log_dir = os.path.join(tmp_path, 'logs')
    actuals_dir = os.path.join(tmp_path, 'actuals')
    os.makedirs(backup_root_dir)
    os.makedirs(config_dest_dir)
    os.makedirs(scratch_dir)
    os.makedirs(log_dir)
    os.makedirs(actuals_dir)

    random_file_tree(backup_root_dir)

    logger.debug(f'Got backup_root: {backup_root_dir}')
    logger.debug(f'Reading config template file: {config_src_file}')
    logger.debug(f'Reading secrets template file: {secrets_src_file}')

    with open(config_src_file, 'r', encoding='utf8') as config_content:
        config_d = yaml.safe_load(config_content)
    with open(secrets_src_file, 'r', encoding='utf8') as secrets_content:
        secrets_d = yaml.safe_load(secrets_content)

    # Setup gnupg
    gnupghome, key = gen_test_key(tmp_path)
    assert key.fingerprint is not None

    # Configure the mounted dirs from the perspective of the container's filesystem
    b2_bucket_name = os.getenv('B2_BUCKET_NAME')
    b2_application_key_id = os.getenv('B2_APPLICATION_KEY_ID')
    b2_application_key = os.getenv('B2_APPLICATION_KEY')

    assert b2_bucket_name is not None
    assert b2_application_key_id is not None
    assert b2_application_key is not None

    config_d['rootBackupPath'] = CONTAINER_ROOT_BACKUP_DIR
    config_d['scratchPath'] = CONTAINER_SCRATCH_BACKUP_DIR
    config_d['gnupgHome'] = CONTAINER_GNUPGHOME
    config_d['gnupgRecipient'] = GNUPG_RECIPIENT
    config_d['logPath'] = CONTAINER_LOG_PATH
    config_d['b2BucketName'] = b2_bucket_name
    del config_d['backupFilePrefix']
    config_d['exclusionSet'] = []

    secrets_d['b2BucketApiKeyId'] = b2_application_key_id
    secrets_d['b2BucketApiKey'] = b2_application_key

    config_dest_file = os.path.join(config_dest_dir, 'config.yaml')
    secrets_dest_file = os.path.join(config_dest_dir, 'secrets.yaml')
    with open(config_dest_file, 'w', encoding='UTF-8') as _file:
        yaml.dump(config_d, _file)
    with open(secrets_dest_file, 'w', encoding='UTF-8') as _file:
        yaml.dump(secrets_d, _file)

    set_expected_file_perms_recursive(backup_root_dir, EXPECTED_UID, EXPECTED_GID, EXPECTED_MODE)

    # TODO: Ensure that the bucket is clean
    os.environ[bkc.BACKUPR_CONFIG_FILE_ENV_K] = config_dest_file
    os.environ[bkc.BACKUPR_SECRETS_FILE_ENV_K] = secrets_dest_file
    config, secrets = bkc.load()
    di[bkc.Config] = config
    di[bkc.Secrets] = secrets
    provider = B2Provider()
    encrypter = Encrypter(gnupghome, GNUPG_RECIPIENT)

    clean_b2_bucket(provider)

    # NOTE: Also configure the container environment
    vols = {}
    vols[backup_root_dir] = { 'bind': CONTAINER_ROOT_BACKUP_DIR, 'mode': 'ro' }
    vols[scratch_dir] = { 'bind': CONTAINER_SCRATCH_BACKUP_DIR, 'mode': 'rw' }
    vols[config_dest_dir] = { 'bind': CONTAINER_CONFIG_DIR, 'mode': 'ro' }
    vols[log_dir] = { 'bind': CONTAINER_LOG_PATH, 'mode': 'rw' }
    vols[gnupghome] = { 'bind': CONTAINER_GNUPGHOME, 'mode': 'rw' }

    env = {
        'BACKUPR_CONFIG_FILE': os.path.join(CONTAINER_CONFIG_DIR, 'config.yaml'),
        'BACKUPR_SECRETS_FILE': os.path.join(CONTAINER_CONFIG_DIR, 'secrets.yaml'),
        'BACKUPR_LOG_DIR': CONTAINER_LOG_PATH,
    }

    docker_client = docker.from_env()
    container_args = {
        'environment': env,
        'volumes': vols,
        'detach': True,
        'user': os.getuid(),
        'group_add': [os.getuid()],
    }
    container = docker_client.containers.run(FQIN, **container_args)
    for log in container.logs(stream=True):
        print(log.decode('utf-8'))
    result = container.wait()
    container.remove()

    status_code = result['StatusCode']
    if status_code != 0:
        logger.error(f'Container exited with a non-zero status code: {status_code}')
    else:
        logger.info('Container exited successfully with a status_code: 0')

    backup = find(lambda f: 'gpg' in f.file_name, provider.list_backups())
    assert backup is not None
    actual_file = os.path.join(actuals_dir, backup.file_name)
    provider.download_file_by_id(backup.id_, actual_file)
    decrypted_actual_file_name = backup.file_name.replace('.gpg', '')
    decrypted_actual_file = os.path.join(actuals_dir, decrypted_actual_file_name)
    encrypter.decrypt(actual_file, decrypted_actual_file, TEST_PASSPHRASE)
    actual_decrypted_file_md5 = md5(decrypted_actual_file)
    expected_file_name = find(lambda fname: re.match(r'.*bz2$', fname), os.listdir(scratch_dir))
    assert expected_file_name is not None
    expected_file = os.path.join(scratch_dir, expected_file_name)
    expected_decrypted_file_md5 = md5(expected_file)

    assert expected_decrypted_file_md5 == actual_decrypted_file_md5

    # TODO: Should further unpack the tar and verify the file perms match

    clean_b2_bucket(provider)
# pylint: enable=too-many-statements


# TODO: These args should be used.
# pylint: disable=unused-argument
def set_expected_file_perms_recursive(_root, uid, guid, mode):
    # TODO: Actually need to set the file permissions here, I'm not sure this will
    # be possible without root permission however.
    for root, dirs, files in os.walk(_root):
        for _dir in dirs:
            os.chmod(os.path.join(root, _dir), EXPECTED_MODE_DIR)
        for _file in files:
            os.chmod(os.path.join(root, _file), EXPECTED_MODE)
# pylint: enable=unused-argument

import os
import random
import string
import glob
from pathlib import Path
import gnupg

from backupr.util import find
from backupr.encrypter import Encrypter
from backupr.tar_builder import TarBuilder
from tests.helpers import random_file_tree, md5

TEST_RECIPIENT = 'duder@duderington.com'
TEST_PASSPHRASE = 'test'

def gen_random_prefix() -> str:
    char_count = 4
    return ''.join(random.choices(string.ascii_lowercase, k=char_count))

def gen_test_key(test_dir: Path) -> str:
    gnupghome = test_dir / 'gnupg'
    os.makedirs(str(gnupghome))

# pylint: disable=unexpected-keyword-arg
# pylint: enable=unexpected-keyword-arg
# NOTE: Unsure why, by pylint thinks this is not a kwarg, when it is
    gpg = gnupg.GPG(gnupghome=gnupghome)
    input_data = gpg.gen_key_input(
        name_email=TEST_RECIPIENT,
        passphrase=TEST_PASSPHRASE,
    )
    key = gpg.gen_key(input_data)
    return gnupghome, key

def test_encrypt(app_config_files):
    config_files  = app_config_files.config_files
    config_file = find(lambda f: 'example_config.yaml' in f, config_files)
    backup_dir_name = 'backup_path'
    test_path = Path(os.path.dirname(config_file))
    test_root_backup_path = test_path / backup_dir_name
    random_file_tree(str(test_root_backup_path))
    random_prefix = gen_random_prefix()
    tar_prefix = f'backupr-{random_prefix}'

    gnupghome, key = gen_test_key(test_path)
    assert key.fingerprint is not None

    tar_builder = TarBuilder(
        str(test_root_backup_path), str(test_path), tar_prefix,
    )
    tar_builder.make_tarfile()

    result = glob.glob(str(test_path / f'{tar_prefix}*'), recursive=False)
    assert len(result) == 1
    unencrypted_tarfile = result[0]
    unencrypted_md5 = md5(unencrypted_tarfile)

    encrypter = Encrypter(gnupghome, TEST_RECIPIENT)
    encrypter.encrypt(unencrypted_tarfile, f'{unencrypted_tarfile}.gpg')
    result = glob.glob(str(test_path / f'{tar_prefix}*.gpg'), recursive=False)
    assert len(result) == 1
    encrypted_tarfile = result[0]

    decrypted_tarfile = f'{unencrypted_tarfile}-decrypted'
    encrypter.decrypt(encrypted_tarfile, decrypted_tarfile, TEST_PASSPHRASE)
    result = glob.glob(str(test_path / f'{tar_prefix}*-decrypted'), recursive=False)
    assert len(result) == 1
    full_decrypted_tarfile = result[0]
    decrypted_md5 = md5(full_decrypted_tarfile)
    assert unencrypted_md5 == decrypted_md5

import subprocess
import gnupg
from loguru import logger

# pylint: disable=unexpected-keyword-arg
class Encrypter:
    def __init__(self, gnupg_home: str, recipient: str):
        self.gnupg_home = gnupg_home
        self.gpg = gnupg.GPG(gnupghome=self.gnupg_home)
        self.recipient = recipient

    def encrypt(self, in_file: str, out_file: str):
        self.__encrypt_subprocess(in_file, out_file)
        # self.__encrypt_pyapi(in_file, out_file)
# pylint: enable=unexpected-keyword-arg

################################################################################
# NOTE: I would prefer to use the python API here but inexplicably during
# testing it became apparent that the output file after decrypting this
# was corrupted! Using the subprocess verifiably is untarable after
# decryption which is obviously critical for backupr.
################################################################################
    # def __encrypt_pyapi(self, in_file: str, out_file: str):
        # logger.info(f'Encrypting input file {in_file}')
        # logger.info(f'Output file: {out_file}')

        # with open(in_file) as f:
            # crypt = self.gpg.encrypt_file(
                # f, recipients=[self.recipient],
                # output=out_file
            # )

        # if not crypt.ok:
            # logger.error('Error occurred while encrypting')
            # logger.error(f'{crypt.status}')
            # raise Exception(crypt.status)
################################################################################

    def __encrypt_subprocess(self, in_file: str, out_file: str):
        logger.info(f'Encrypting input file {in_file}')
        logger.info(f'Output file: {out_file}')

        cmd = ['gpg', '--output', out_file, '--encrypt',
               '--recipient', self.recipient, in_file]
        env = {
            'GNUPGHOME': self.gnupg_home,
        }

        with subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE) as proc:
            for line in proc.stdout:
                logger.info(line)

            proc.wait()
            if proc.returncode != 0:
                logger.error('Error occurred while encrypting')
                raise Exception('Subprocess encryption failed')

    def decrypt(self, in_file: str, out_file: str, passphrase: str):
        logger.info(f'Decrypting input file {in_file}')
        logger.info(f'Output file: {out_file}')

        with open(in_file, 'rb') as file:
            crypt = self.gpg.decrypt_file(
                file, passphrase=passphrase, output=out_file)

        if not crypt.ok:
            logger.error('Error occurred while decrypting')
            logger.error(f'{crypt.status}')
            raise Exception(crypt.status)

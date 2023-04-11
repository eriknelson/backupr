import os
from typing import Tuple
from pathlib import Path
import b2sdk.v2 as b2
from kink import inject
from backupr.config import Config, Secrets
from backupr.storage_provider import Status

B2_KEY_NAME_EVK = 'B2_KEY_NAME'
B2_BUCKET_NAME_EVK = 'B2_BUCKET_NAME'
B2_APPLICATION_KEY_ID_EVK = 'B2_APPLICATION_KEY_ID'
B2_APPLICATION_KEY_EVK = 'B2_APPLICATION_KEY'

# Note: the "production" value here is apparently the "realm".
# According to this blog, there isn't much information available on this
# https://blog.teclado.com/python-file-upload-backblaze-b2/
# https://b2-sdk-python.readthedocs.io/en/master/api/api.html#b2sdk.v2.B2Api.authorize_account
B2_REALM = 'production'

@inject
class B2Provider():
    """IStorageProvider implementation providing Backblaze B2 support"""

    def __init__(self, config: Config, secrets: Secrets):
        self.config = config
        self.secrets = secrets
        info = b2.InMemoryAccountInfo()
        application_key_id = self.secrets.b2_bucket_api_key_id.get_secret_value()
        application_key = self.secrets.b2_bucket_api_key.get_secret_value()
        self.b2_api = b2.B2Api(info)
        self.b2_api.authorize_account(B2_REALM, application_key_id, application_key)

    def upload(self, file: str):
        """Uploads a file to the StorageProvider"""
        # print(f'nsk doing the thing: {self.config.b2_bucket_name}')
        bucket = self.b2_api.get_bucket_by_name(self.config.b2_bucket_name)
        file_name = os.path.basename(Path(file))
        uploaded_file = bucket.upload_local_file(
            local_file=file,
            file_name=file_name,
        )
        # NOTE: The id field of this file is literally 'id_' with a trailing underscore
        # https://b2-sdk-python.readthedocs.io/en/master/api/data_classes.html#b2sdk.v2.FileVersion
        file_id = uploaded_file.id_
        uploaded_file_url = self.b2_api.get_download_url_for_fileid(file_id)
        return uploaded_file, uploaded_file_url

    def download_file_by_id(self, file_id, output_file: str):
        bucket = self.b2_api.get_bucket_by_name(self.config.b2_bucket_name)
        downloaded_file = bucket.download_file_by_id(file_id)
        downloaded_file.save_to(output_file)

    def list_backups(self):
        """Lists the backups present in the StorageProvider"""
        bucket = self.b2_api.get_bucket_by_name(self.config.b2_bucket_name)
        b2files = bucket.ls()
        return [res[0] for res in b2files]

    def list_logfiles(self) -> Tuple[Status, list[str]]:
        """Lists the backups present in the StorageProvider"""

    def delete(self, file_id: str, file_name: str):
        """Deletes a file in the StorageProvider"""
        bucket = self.b2_api.get_bucket_by_name(self.config.b2_bucket_name)
        bucket.delete_file_version(file_id, file_name)

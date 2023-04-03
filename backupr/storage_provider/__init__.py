from typing import Protocol, Tuple

# pylint: disable=unused-argument
class Status():
    def __init__(self, okay: bool, message: str):
        ...
# pylint: enable=unused-argument

class IStorageProvider(Protocol):
    """IStorageProvider provides the ability for backing up the backupr primary
    asset (a raw tarball of the backed up files, or the encrypted tarball) to
    a secondary location. An example of this is the B2Provider, that manages the
    B2 backed up files and drops off the log for future review."""
################################################################################
# TODO: Thinking through what this has to do:
# * Upload the files - we do this once initially and we have to know whether or
# not that was successful because other operations depend upon that status.
# * List the files ordered by most recent. This is something that we should be
# able to tell thanks to the timestamp in the file name, but it would be more
# convenient to ensure that the List that's returned is actually ordered by
# time from newest -> oldest. This is important for removing the oldest file
# found. Could be convenient to have list_backups and list_logs split into
# distinct methods.
# * delete - necessary to allow for the cleaning up of the provider once the
# upload has been verified
################################################################################
    def upload(self, file: str) -> Status:
        """Uploads a file to the StorageProvider"""

    def list_backups(self) -> Tuple[Status, list[str]]:
        """Lists the backups present in the StorageProvider"""

    def list_logfiles(self) -> Tuple[Status, list[str]]:
        """Lists the backups present in the StorageProvider"""

    def delete(self, file_id: str) -> Status:
        """Deletes a file in the StorageProvider"""

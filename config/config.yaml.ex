# vim: set ft=yaml:
################################################################################
# Backupr Configuration
# NOTE: Today only backblaze is supported. If backblaze is enabled, and one
# offsite storage must be enabled
################################################################################
# rootBackupPath (str, required) - The root dir that will be backed up.
rootBackupPath: /home/duder/dat

# scratchPath - (str, required) The directory where the intermediary tar will be
# created before it is optionally encrypted and then uploaded to offsite backup
# service.
scratchPath: /home/duder/backups/scratch

# preservedTars (int>=1, optional, default: 2) - Backupr will preseve this
# number of tars in the scratch dir, which can be useful in a pinch.
preservedTars: 2

# backupFilePrefix (str, optional, default="backupr") - A prefix value used for
# the tar.
# Example: "backupr" would result in backupr-080320-11000.tar
backupFilePrefix: my_backup

# exclusionSet (list(str), optional, default: None) - The array of exclude
# patterns that are passed to tar using tar's --exclude flag. The default
# behavior is no exclusion.
exclusionSet:
  - '*/vendor'

# gnupgHome (str, optional, default: system, most likely ~/.gnupg) - The
# GNUPGHOME directory where the recipient will be looked up.
gnupgHome: /home/duder/.alt-gnupg

# gnupgRecipient (str, optional, default: None) - The gpg recipient that will be
# used to encrypt the tar backup prior to upload. The implicit presence of this
# value will enable encryption. If gnupgRecipient is not set, encryption will
# not be enabled.
gnupgRecipient: duder@duderington.zone

# logPath - (str, optional, default: /var/log) - The directory where logs will
# be stored.
logPath: /tmp/backupr/logs

################################################################################
# Offsite Storage Provider Configuration
# NOTE: Today only backblaze is supported. If backblaze is enabled, and one
# offsite storage must be enabled
################################################################################
# [Backblaze]

# b2ProviderEnabled (bool, optional, default: True) - Enables Backblaze as
# the offsite storage provider.
b2ProviderEnabled: true

# b2BucketName - The backblaze bucket name where backups will be stored.
b2BucketName: duder-bucket

b2BucketApiKeyId: myKeyId

# b2BucketApiKey - The backblaze api key used to authenticate with b2. This key
# necessarily will need read/write permissions on the provided bucket.
b2BucketApiKey: topsecretkey

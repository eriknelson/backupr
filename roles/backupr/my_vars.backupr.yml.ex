# vim: ft=yaml:
# backupr_user - The user that will own everything
backupr_user: "{{ main_user }}"
# backupr_group- The group that will own everything
backupr_group: "{{ main_user }}"

################################################################################
# Backupr Configuration
# NOTE: Today only backblaze is supported. If backblaze is enabled, and one
# offsite storage must be enabled
################################################################################
# root_backup_path (str, required) - The root dir that will be backed up.
root_backup_path: /dat

# scratch_path- (str, required) The directory where the intermediary tar will be
# created before it is optionally encrypted and then uploaded to offsite backup
# service.
scratch_path: /dat/scratch

# preserved_tars (int>=1, optional, default: 2) - Backupr will preseve this
# number of tars in the scratch dir, which can be useful in a pinch.
preserved_tars: 2

# backup_fie_prefix (str, optional, default="backupr") - A prefix value used for
# the tar.
# Example: "backupr" would result in backupr-080320-11000.tar
#backup_file_prefix: my_backup

# exclusion_set (list(str), optional, default: None) - The array of exclude
# patterns that are passed to tar using tar's --exclude flag. The default
# behavior is no exclusion.
exclusion_set:
  - '\/vendor\/'

# gnupgHome (str, optional, default: system, most likely ~/.gnupg) - The
# GNUPGHOME directory where the recipient will be looked up.
gnupg_home: /home/duder/.backupr-gnupg

# gnupgRecipient (str, optional, default: None) - The gpg recipient that will be
# used to encrypt the tar backup prior to upload. The implicit presence of this
# value will enable encryption. If gnupgRecipient is not set, encryption will
# not be enabled.
gnupg_recipient: duder@decker.zone

################################################################################
# Offsite Storage Provider Configuration
# NOTE: Today only backblaze is supported. If backblaze is enabled, and one
# offsite storage must be enabled
################################################################################
# [Backblaze]

# b2ProviderEnabled (bool, optional, default: True) - Enables Backblaze as
# the offsite storage provider.
b2_provider_enabled: true

# b2BucketName - The backblaze bucket name where backups will be stored.
b2_bucket_name: my-bucket


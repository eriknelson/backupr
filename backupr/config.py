import os
import sys
# import sys
# from datetime import timedelta
from loguru import logger
# NOTE: I have no idea why, but the linter thinks that BaseModel isn't available
# from pydantic. I'm abse to import it and use it as base class, so unsure what
# the issue is.
# pylint: disable=no-name-in-module
from pydantic import Field, SecretStr, ValidationError
# pylint: enable=no-name-in-module
from pydantic_yaml import YamlModel

# SEVERITY_DESC = 'severity (required, str Enum(sev1|sev2|sev3|sev4)): \
    # The severity level of the sla tier.'
# DELTA_TRIGGER_DESC = 'deltaTrigger (required, ISO-8601 duration): \
    # Time delta for severity that will breach SLA.'
# DELTA_WARN_DESC = 'deltaWarn (required, ISO-8601 duration): \
    # Time delta before breach where a warn will be alerted'
# SLA_TEAM_DESC = 'slaTeam (required, str): OpsGenie team respnsible for handling \
    # issues with SLA. str.'
# OPSGENIE_API_BASE_URL_DESC = \
    # 'opsgenieApiBaseUrl (optional, str, default: \'https://api.opsgenie.com\'): \
    # The base url used for the opsgenie API, default value should be fine, but it\'s \
    # available for override.'
# JIRA_USER_BASE_URL_DESC = \
    # 'jiraUserBaseUrl (required, str): The base url used for the user facing \
    # jira site, generally used for browsing user issues on the site'
# JIRA_API_BASE_URL_DESC = \
    # 'jiraApiBaseUrl (required, str): The base url used for the jira api'

# OPSGENIE_API_KEY_DESC = 'opsgenieApiKey (required, str)'
# JIRA_USER_DESC = 'jiraUser (required, str): User associated with the jiraApiKey'
# JIRA_API_KEY_DESC = 'jiraApiKey (required, str)'

# DEFAULT_OPSGENIE_API_BASE_URL = 'https://api.opsgenie.com'

BACKUPR_CONFIG_FILE_ENV_K = 'BACKUPR_CONFIG_FILE'
DEFAULT_BACKUPR_CONFIG_FILE = '/etc/swifty/config.yaml'

BACKUPR_SECRETS_FILE_ENV_K = 'BACKUPR_SECRETS_FILE'
DEFAULT_BACKUPR_SECRETS_FILE = '/var/backupr/vols/secrets/secrets.yaml'

# DEFAULT_REPORT_DIR = '/tmp/swifty/reports'

# class SLATier(BaseModel):
    # severity: SLASeverity = Field(..., description=SEVERITY_DESC)
    # delta_trigger: timedelta = Field(...,
        # description=DELTA_TRIGGER_DESC, alias='deltaTrigger')
    # delta_warn: timedelta = Field(...,
        # description=DELTA_WARN_DESC, alias='deltaWarn')

ROOT_BACKUP_PATH_DESC = (
    'rootBackupPath (str, required) - '
    'The path to the root dir that will be backed up.'
)
SCRATCH_PATH_DESC = (
    'scratchPath (str, required) - '
    'The directory where the intermediary tar will be created before it is '
    'optionally encrypted and then uploaded to the offsite backup service.'
)
PRESERVED_TARS_DESC = (
    'preservedTars (int >= 1, optional, default: 2) - '
    'Backupr will preserve this number of tars in the scratchPath, which can '
    'be useful in a pinch.'
)
DEFAULT_BACKUP_FILE_PREFIX = 'backupr'
BACKUP_FILE_PREFIX_DESC = (
    'backupFilePrefix (str, optional, default="backupr") - '
    'A prefix value used for the tar. '
    'Example: "backupr" would result in backupr-080320-110000.tar.gz'
)
EXCLUSION_SET_DESC = (
    'exclusionSet (list[str], optional, default: None) - '
    'The list of exclude patterns that are passed to tar using tar\'s '
    '--exclude flag. The default behavior is no exclusion.'
)
GNUPG_HOME_DESC = (
    'gnupgHome (str, optional, default: system, most likely ~/.gnupg) - '
    'The GNUPGHOME directory where the recipient will be looked up.'
)
# Respect GNUPGHOME env var with precedence
DEFAULT_GNUPG_HOME = '~/.gnupg'
gnupg_home_env = os.getenv('GNUPGHOME')
default_gnupg_home = gnupg_home_env if gnupg_home_env else DEFAULT_GNUPG_HOME

GNUPG_RECIPIENT_DESC= (
    'gnupgRecipient (str, optional, default: None) - '
    'The gpg recipient that will be used to encrypt the tar backup prior to '
    'upload. The implicit presence of this value will enable encryption. If '
    'gnupgRecipient is not set, encryption will not be enabled.'
)
DEFAULT_LOG_PATH = '/var/log'
LOG_PATH_DESC = (
    'logPath (str, optional, default: /var/log) - '
    'The path to where the backupr-*.log file will be stored.'
)
DEFAULT_B2_PROVIDER_ENABLED = True
B2_PROVIDER_ENABLED_DESC = (
    'b2ProviderEnabled (bool, optional, default: True) - '
    'Enables Backblaze as the offsite storage provider.'
)
DEFAULT_B2_BUCKET_NAME = 'backupr'
B2_BUCKET_NAME_DESC = (
    'b2BucketName (str, optional, default: "backupr") - '
    'The Backblaze bucket name where backups will be stored.'
)

# Secrets descriptions
B2_BUCKET_API_KEY_ID_DESC = (
    'b2BucketApiKeyId (str, opt) - '
    'The B2 bucket api key id.'
)
B2_BUCKET_API_KEY_DESC = (
    'b2BucketApiKey (str, opt) - '
    'The B2 bucket api key.'
)

class Config(YamlModel):
    root_backup_path: str = Field(
        ..., description=ROOT_BACKUP_PATH_DESC, alias='rootBackupPath')
    scratch_path: str = Field(
        ..., description=SCRATCH_PATH_DESC, alias='scratchPath')
    preserved_tars: int = Field(
        default=2, description=PRESERVED_TARS_DESC, alias='preservedTars')
    backup_file_prefix: str = Field(
        default=DEFAULT_BACKUP_FILE_PREFIX, description=BACKUP_FILE_PREFIX_DESC,
        alias='backupFilePrefix')
    exclusion_set: list[str] = Field(
        default=[], description=EXCLUSION_SET_DESC, alias='exclusionSet')
    gnupg_home: str = Field(
        default=default_gnupg_home,
        description=GNUPG_HOME_DESC , alias='gnupgHome')
    gnupg_recipient: str = Field(
        default=None,
        description=GNUPG_RECIPIENT_DESC, alias='gnupgRecipient')
    log_path: str = Field(
        default=DEFAULT_LOG_PATH,
        description=LOG_PATH_DESC, alias='logPath')
    b2_provider_enabled: bool = Field(
        default=DEFAULT_B2_PROVIDER_ENABLED,
        description=B2_PROVIDER_ENABLED_DESC, alias='b2ProviderEnabled')
    b2_bucket_name: str = Field(
        default=DEFAULT_B2_BUCKET_NAME,
        description=B2_BUCKET_NAME_DESC, alias='b2BucketName')

class Secrets(YamlModel):
    b2_bucket_api_key_id: SecretStr = Field(...,
        description=B2_BUCKET_API_KEY_ID_DESC, alias='b2BucketApiKeyId')
    b2_bucket_api_key: SecretStr = Field(...,
        description=B2_BUCKET_API_KEY_DESC, alias='b2BucketApiKey')

def load() -> tuple[Config, Secrets]:
    """
    load takes no arguments and will load application Config and Secrets from the
    filesystem. Swifty is designed to read in app config and secrets from files,
    as the natural environment to do so within kube is to mount the configmap and
    secret from externalsecrets as yaml files in the filesystem. Developers may
    easily override these default locations with SWIFTY_CONFIG_FILE|SWIFTY_SECRETS_FILE
    environment variables to support local development.
    """

    backupr_config_file = os.getenv(BACKUPR_CONFIG_FILE_ENV_K) or \
        DEFAULT_BACKUPR_CONFIG_FILE

    backupr_secrets_file = os.getenv(BACKUPR_SECRETS_FILE_ENV_K) or \
        DEFAULT_BACKUPR_SECRETS_FILE

    logger.info(f'Reading config file at {backupr_config_file}')
    try:
        config = Config.parse_file(backupr_config_file)
    except ValidationError as err:
        logger.error('Failed to parse config file, shutting down')
        logger.error(str(err))
        sys.exit(1)
    logger.info('Config successfully read:')
    logger.info(f'{config}')

    logger.info(f'Reading secrets file at {backupr_config_file}')
    try:
        secrets = Secrets.parse_file(backupr_secrets_file)
    except ValidationError as err:
        logger.error('Failed to parse secrets file, shutting down')
        logger.error(str(err))
        sys.exit(1)
    # NOTE: You may see this and think "omg don't print secrets"
    # The secrets model fields are SecretStr, meaning they're automatically
    # obfuscated when converted to a string value.
    logger.info('Secrets successfully read:')
    logger.info(f'{secrets}')

    return config, secrets

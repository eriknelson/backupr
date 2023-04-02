import yaml
from backupr.config import (
    Config, Secrets
)

def test_valid_config(configs: dict[str, str]):
    valid_config = configs['example_config.yaml']
    expected_config_d = yaml.safe_load(valid_config)

    actual_config = Config.parse_raw(valid_config)
    assert_valid_config(actual_config, expected_config_d)

def assert_valid_config(actual_config: Config, expected_config_d):
    assert actual_config.root_backup_path == expected_config_d['rootBackupPath']
    assert actual_config.scratch_path == expected_config_d['scratchPath']
    assert actual_config.preserved_tars == expected_config_d['preservedTars']
    assert actual_config.backup_file_prefix == expected_config_d['backupFilePrefix']

    # TODO: Assert the exclusion set values

    # sev1_tier: SLATier = actual_config.sla_tiers[0]
    # assert sev1_tier.severity == SLASeverity.SEV1
    # expected_duration = isodate.parse_duration(
        # expected_config_d['slaTiers'][0]['deltaTrigger']
    # )
    # assert sev1_tier.delta_trigger == expected_duration

    # sev2_tier: SLATier = actual_config.sla_tiers[1]
    # assert sev2_tier.severity == SLASeverity.SEV2
    # expected_duration = isodate.parse_duration(
        # expected_config_d['slaTiers'][1]['deltaTrigger']
    # )
    # assert sev2_tier.delta_trigger == expected_duration

    # sev3_tier: SLATier = actual_config.sla_tiers[2]
    # assert sev3_tier.severity == SLASeverity.SEV3
    # expected_duration = isodate.parse_duration(
        # expected_config_d['slaTiers'][2]['deltaTrigger']
    # )
    # assert sev3_tier.delta_trigger == expected_duration

# def assert_valid_secrets(secrets: Secrets, expected_secrets_d):
    # assert secrets.opsgenie_api_key == SecretStr(expected_secrets_d['opsgenieApiKey'])

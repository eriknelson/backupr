import os

import pytest
test_spec = os.getenv('TEST_SPEC')
if test_spec:
    retcode = pytest.main(["-s", f'{test_spec}'])
else:
    retcode = pytest.main(["-s"])

# def run_sprint_report():
    # from swifty.cli import sprint_report
    # from tests.test_config import SWIFTY_CONFIG_FILE_ENV_K, SWIFTY_SECRETS_FILE_ENV_K

    # dir_path = os.path.dirname(os.path.realpath(__file__))
    # config_file = os.path.join(dir_path, 'devutil', 'configs', 'config.yaml')
    # secrets_file = os.path.join(dir_path, 'devutil', 'configs', 'secrets.yaml')
    # os.environ[SWIFTY_CONFIG_FILE_ENV_K] = config_file
    # os.environ[SWIFTY_SECRETS_FILE_ENV_K] = secrets_file
    # sprint_report()


# should_run_sprint_report = os.getenv('RUN_SPRINT_REPORT')
# if should_run_sprint_report:
    # run_sprint_report()
# else:
    # import pytest
    # test_spec = os.getenv('TEST_SPEC')
    # if test_spec:
        # retcode = pytest.main(["-s", f'{test_spec}'])
    # else:
        # retcode = pytest.main(["-s"])

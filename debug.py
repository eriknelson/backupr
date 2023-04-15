import os
from loguru import logger

import pytest
test_spec = os.getenv('TEST_SPEC')
deep_integration_test = os.getenv('DEEP_INTEGRATION_TEST')
if deep_integration_test:
    logger.info('debug.deep_integration_test')
    retcode = pytest.main(["-s", 'scripts/ci/deep-int-test.py'])
elif test_spec:
    logger.info(f'debug.test_spec -> {test_spec}')
    retcode = pytest.main(["-s", f'{test_spec}'])
else:
    logger.info('debug.default tests')
    retcode = pytest.main(["-s"])

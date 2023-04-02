import os

import pytest
test_spec = os.getenv('TEST_SPEC')
if test_spec:
    retcode = pytest.main(["-s", f'{test_spec}'])
else:
    retcode = pytest.main(["-s"])

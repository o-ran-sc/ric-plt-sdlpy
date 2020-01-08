# Copyright (c) 2019 AT&T Intellectual Property.
# Copyright (c) 2018-2019 Nokia.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#
# This source code is part of the near-RT RIC (RAN Intelligent Controller)
# platform project (RICP).
#


import pytest
from ricsdl.configuration import _Configuration
from ricsdl.configuration import DbBackendType


@pytest.fixture()
def config_fixture(request, monkeypatch):
    monkeypatch.setenv('DBAAS_SERVICE_HOST', '10.20.30.40')
    monkeypatch.setenv('DBAAS_SERVICE_PORT', '10000')
    monkeypatch.setenv('DBAAS_SERVICE_SENTINEL_PORT', '11000')
    monkeypatch.setenv('DBAAS_MASTER_NAME', 'my-master')
    request.cls.config = _Configuration(fake_db_backend=None)


@pytest.fixture
def fake_db_config_fixture(request, monkeypatch):
    monkeypatch.delenv('DBAAS_SERVICE_HOST', raising=False)
    monkeypatch.delenv('DBAAS_SERVICE_PORT', raising=False)
    monkeypatch.delenv('DBAAS_SERVICE_SENTINEL_PORT', raising=False)
    monkeypatch.delenv('DBAAS_MASTER_NAME', raising=False)
    request.cls.config = _Configuration(fake_db_backend='dict')


class TestConfiguration:
    def test_get_params_function_returns_read_configuration(self, config_fixture):
        expected_config = _Configuration.Params(db_host='10.20.30.40', db_port='10000',
                                                db_sentinel_port='11000',
                                                db_sentinel_master_name='my-master',
                                                db_type=DbBackendType.REDIS)
        assert expected_config == self.config.get_params()

    def test_get_params_function_can_return_fake_db_configuration(self, fake_db_config_fixture):
        expected_config = _Configuration.Params(db_host=None, db_port=None,
                                                db_sentinel_port=None,
                                                db_sentinel_master_name=None,
                                                db_type=DbBackendType.FAKE_DICT)
        assert expected_config == self.config.get_params()

    def test_get_params_function_can_raise_exception_if_wrong_fake_db_type(self):
        with pytest.raises(ValueError, match=r"Configuration error"):
            _Configuration(fake_db_backend='bad value')


    def test_configuration_object_string_representation(self, config_fixture):
        expected_config_info = {'DB host': '10.20.30.40',
                                'DB port': '10000',
                                'DB master sentinel': 'my-master',
                                'DB sentinel port': '11000',
                                'DB type': 'REDIS'}
        assert str(self.config) == str(expected_config_info)

    def test_configuration_object_string_representation_if_fake_db(self, fake_db_config_fixture):
        expected_config_info = {'DB host': None,
                                'DB port': None,
                                'DB master sentinel': None,
                                'DB sentinel port': None,
                                'DB type': 'FAKE_DICT'}
        assert str(self.config) == str(expected_config_info)

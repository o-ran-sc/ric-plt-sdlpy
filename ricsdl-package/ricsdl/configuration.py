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


"""The module provides implementation of Shared Data Layer (SDL) configurability."""
import os
from collections import namedtuple
from distutils.util import strtobool


class _Configuration():
    """This class implements Shared Data Layer (SDL) configurability."""
    Params = namedtuple('Params', ['db_host', 'db_port', 'db_sentinel_port',
                                   'db_sentinel_master_name', 'fake_db'])

    def __init__(self):
        self.params = self._read_configuration()

    def __str__(self):
        return str(
            {
                "DB host": self.params.db_host,
                "DB port": self.params.db_port,
                "DB master sentinel": self.params.db_sentinel_master_name,
                "DB sentinel port": self.params.db_sentinel_port,
                "Fake DB": self.params.fake_db,
            }
        )

    def get_params(self):
        """Return SDL configuration."""
        return self.params

    @classmethod
    def _read_configuration(cls):
        read_db_host = os.getenv('DBAAS_SERVICE_HOST')
        read_db_port = os.getenv('DBAAS_SERVICE_PORT')
        read_db_sentinel_port = os.getenv('DBAAS_SERVICE_SENTINEL_PORT')
        read_db_master_name = os.getenv('DBAAS_MASTER_NAME')
        read_use_fake_db = bool(strtobool(os.getenv('USE_FAKE_DBAAS', 'False')))

        if read_use_fake_db and read_db_host:
            msg = ("Configuration mismatch: "
                   "fake DB usage cannot be enabled if DBAAS host ({}) is configured.".
                   format(read_db_host))
            raise ValueError(msg)

        return _Configuration.Params(db_host=read_db_host,
                                     db_port=read_db_port,
                                     db_sentinel_port=read_db_sentinel_port,
                                     db_sentinel_master_name=read_db_master_name,
                                     fake_db=read_use_fake_db)

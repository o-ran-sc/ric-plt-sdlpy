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


class _Configuration():
    """This class implements Shared Data Layer (SDL) configurability."""
    Params = namedtuple('Params', ['db_host', 'db_port', 'db_sentinel_port',
                                   'db_sentinel_master_name'])

    def __init__(self):
        self.params = self._read_configuration()

    def __str__(self):
        return str(
            {
                "DB host": self.params.db_host,
                "DB port": self.params.db_port,
                "DB master sentinel": self.params.db_sentinel_master_name,
                "DB sentinel port": self.params.db_sentinel_port
            }
        )

    def get_params(self):
        """Return SDL configuration."""
        return self.params

    @classmethod
    def _read_configuration(cls):
        return _Configuration.Params(db_host=os.getenv('DBAAS_SERVICE_HOST'),
                                     db_port=os.getenv('DBAAS_SERVICE_PORT'),
                                     db_sentinel_port=os.getenv('DBAAS_SERVICE_SENTINEL_PORT'),
                                     db_sentinel_master_name=os.getenv('DBAAS_MASTER_NAME'))

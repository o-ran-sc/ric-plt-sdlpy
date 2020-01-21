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


"""The module provides fake implementation of Shared Data Layer (SDL) database backend interface."""
import fnmatch
from typing import (Dict, Set, List, Union)
from ricsdl.configuration import _Configuration
from .dbbackend_abc import DbBackendAbc
from .dbbackend_abc import DbBackendLockAbc


class FakeDictBackend(DbBackendAbc):
    """
    A class providing fake implementation of database backend of Shared Data Layer (SDL).
    This class does not provide working database solution, this class can be used in testing
    purposes only. Implementation does not provide shared database resource, SDL client sees
    only its local local 'fake' database, which is a simple Python dictionary. Also keys are
    stored in database under the same namespace.

    Args:
        configuration (_Configuration): SDL configuration, containing credentials to connect to
                                        Redis database backend.
    """
    def __init__(self, configuration: _Configuration) -> None:
        super().__init__()
        self._db = {}
        self._configuration = configuration

    def __str__(self):
        return str(
            {
                "DB type": "FAKE DB",
            }
        )

    def is_connected(self):
        return True

    def close(self):
        pass

    def set(self, ns: str, data_map: Dict[str, bytes]) -> None:
        self._db.update(data_map.copy())

    def set_if(self, ns: str, key: str, old_data: bytes, new_data: bytes) -> bool:
        if key not in self._db:
            return False
        db_data = self._db[key]
        if db_data == old_data:
            self._db[key] = new_data
            return True
        return False

    def set_if_not_exists(self, ns: str, key: str, data: bytes) -> bool:
        if key not in self._db:
            self._db[key] = data
            return True
        return False

    def get(self, ns: str, keys: List[str]) -> Dict[str, bytes]:
        ret = {}
        for k in keys:
            if k in self._db:
                ret[k] = self._db[k]
        return ret

    def find_keys(self, ns: str, key_pattern: str) -> List[str]:
        ret = []
        for k in self._db:
            if fnmatch.fnmatch(k, key_pattern):
                ret.append(k)
        return ret

    def find_and_get(self, ns: str, key_pattern: str) -> Dict[str, bytes]:
        ret = {}
        for key, val in self._db.items():
            if fnmatch.fnmatch(key, key_pattern):
                ret[key] = val
        return ret

    def remove(self, ns: str, keys: List[str]) -> None:
        for key in keys:
            self._db.pop(key, None)

    def remove_if(self, ns: str, key: str, data: bytes) -> bool:
        if key in self._db:
            db_data = self._db[key]
            if db_data == data:
                self._db.pop(key)
                return True
        return False

    def add_member(self, ns: str, group: str, members: Set[bytes]) -> None:
        if group in self._db:
            self._db[group] = self._db[group] | members.copy()
        else:
            self._db[group] = members.copy()

    def remove_member(self, ns: str, group: str, members: Set[bytes]) -> None:
        if group not in self._db:
            return
        for member in members:
            self._db[group].discard(member)

    def remove_group(self, ns: str, group: str) -> None:
        self._db.pop(group, None)

    def get_members(self, ns: str, group: str) -> Set[bytes]:
        return self._db.get(group, set())

    def is_member(self, ns: str, group: str, member: bytes) -> bool:
        if group not in self._db:
            return False
        if member in self._db[group]:
            return True
        return False

    def group_size(self, ns: str, group: str) -> int:
        if group not in self._db:
            return 0
        return len(self._db[group])


class FakeDictBackendLock(DbBackendLockAbc):
    """
    A class providing fake implementation of database backend lock of Shared Data Layer (SDL).
    This class does not provide working database solution, this class can be used in testing
    purposes only. Implementation does not provide shared database resource, SDL client sees
    only its local local 'fake' database, which is a simple Python dictionary. Also keys are
    stored in database under the same namespace.
    Args:
        ns (str): Namespace under which this lock is targeted.
        name (str): Lock name, identifies the lock key in a Redis database backend.
        expiration (int, float): Lock expiration time after which the lock is removed if it hasn't
                                 been released earlier by a 'release' method.
        redis_backend (FakeBackend): Database backend object containing fake databese connection.
    """

    def __init__(self, ns: str, name: str, expiration: Union[int, float],
                 redis_backend: FakeDictBackend) -> None:
        super().__init__(ns, name)
        self._locked = False
        self._ns = ns
        self._lock_name = name
        self._lock_expiration = expiration
        self.redis_backend = redis_backend

    def __str__(self):
        return str(
            {
                "lock DB type": "FAKE DB",
                "lock namespace": self._ns,
                "lock name": self._lock_name,
                "lock status": self._lock_status_to_string()
            }
        )

    def acquire(self, retry_interval: Union[int, float] = 0.1,
                retry_timeout: Union[int, float] = 10) -> bool:
        if self._locked:
            return False
        self._locked = True
        return self._locked

    def release(self) -> None:
        self._locked = False

    def refresh(self) -> None:
        pass

    def get_validity_time(self) -> Union[int, float]:
        return self._lock_expiration

    def _lock_status_to_string(self) -> str:
        if self._locked:
            return 'locked'
        return 'unlocked'

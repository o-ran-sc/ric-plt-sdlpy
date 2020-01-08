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


"""The module provides implementation of Shared Data Layer (SDL) database backend interface."""
import contextlib
from typing import (Dict, Set, List, Union)
from redis import Redis
from redis.sentinel import Sentinel
from redis.lock import Lock
from redis._compat import nativestr
from redis import exceptions as redis_exceptions
from ricsdl.configuration import _Configuration
from ricsdl.exceptions import (
    RejectedByBackend,
    NotConnected,
    BackendError
)
from .dbbackend_abc import DbBackendAbc
from .dbbackend_abc import DbBackendLockAbc


@contextlib.contextmanager
def _map_to_sdl_exception():
    """Translates known redis exceptions into SDL exceptions."""
    try:
        yield
    except(redis_exceptions.ResponseError) as exc:
        raise RejectedByBackend("SDL backend rejected the request: {}".
                                format(str(exc))) from exc
    except(redis_exceptions.ConnectionError, redis_exceptions.TimeoutError) as exc:
        raise NotConnected("SDL not connected to backend: {}".
                           format(str(exc))) from exc
    except(redis_exceptions.RedisError) as exc:
        raise BackendError("SDL backend failed to process the request: {}".
                           format(str(exc))) from exc


class RedisBackend(DbBackendAbc):
    """
    A class providing an implementation of database backend of Shared Data Layer (SDL), when
    backend database solution is Redis.

    Args:
        configuration (_Configuration): SDL configuration, containing credentials to connect to
                                        Redis database backend.
    """
    def __init__(self, configuration: _Configuration) -> None:
        super().__init__()
        with _map_to_sdl_exception():
            if configuration.get_params().db_sentinel_port:
                sentinel_node = (configuration.get_params().db_host,
                                 configuration.get_params().db_sentinel_port)
                master_name = configuration.get_params().db_sentinel_master_name
                self.__sentinel = Sentinel([sentinel_node])
                self.__redis = self.__sentinel.master_for(master_name)
            else:
                self.__redis = Redis(host=configuration.get_params().db_host,
                                     port=configuration.get_params().db_port,
                                     db=0,
                                     max_connections=20)
        self.__redis.set_response_callback('SETIE', lambda r: r and nativestr(r) == 'OK' or False)
        self.__redis.set_response_callback('DELIE', lambda r: r and int(r) == 1 or False)

    def __del__(self):
        self.close()

    def __str__(self):
        return str(
            {
                "DB type": "Redis",
                "Redis connection": repr(self.__redis)
            }
        )

    def close(self):
        self.__redis.close()

    def set(self, ns: str, data_map: Dict[str, bytes]) -> None:
        db_data_map = self._add_data_map_ns_prefix(ns, data_map)
        with _map_to_sdl_exception():
            self.__redis.mset(db_data_map)

    def set_if(self, ns: str, key: str, old_data: bytes, new_data: bytes) -> bool:
        db_key = self._add_key_ns_prefix(ns, key)
        with _map_to_sdl_exception():
            return self.__redis.execute_command('SETIE', db_key, new_data, old_data)

    def set_if_not_exists(self, ns: str, key: str, data: bytes) -> bool:
        db_key = self._add_key_ns_prefix(ns, key)
        with _map_to_sdl_exception():
            return self.__redis.setnx(db_key, data)

    def get(self, ns: str, keys: List[str]) -> Dict[str, bytes]:
        ret = dict()
        db_keys = self._add_keys_ns_prefix(ns, keys)
        with _map_to_sdl_exception():
            values = self.__redis.mget(db_keys)
            for idx, val in enumerate(values):
                # return only key values, which has a value
                if val:
                    ret[keys[idx]] = val
            return ret

    def find_keys(self, ns: str, key_pattern: str) -> List[str]:
        db_key_pattern = self._add_key_ns_prefix(ns, key_pattern)
        with _map_to_sdl_exception():
            ret = self.__redis.keys(db_key_pattern)
            return self._strip_ns_from_bin_keys(ns, ret)

    def find_and_get(self, ns: str, key_pattern: str) -> Dict[str, bytes]:
        # todo: replace below implementation with redis 'NGET' module
        ret = dict()  # type: Dict[str, bytes]
        with _map_to_sdl_exception():
            matched_keys = self.find_keys(ns, key_pattern)
            if matched_keys:
                ret = self.get(ns, matched_keys)
        return ret

    def remove(self, ns: str, keys: List[str]) -> None:
        db_keys = self._add_keys_ns_prefix(ns, keys)
        with _map_to_sdl_exception():
            self.__redis.delete(*db_keys)

    def remove_if(self, ns: str, key: str, data: bytes) -> bool:
        db_key = self._add_key_ns_prefix(ns, key)
        with _map_to_sdl_exception():
            return self.__redis.execute_command('DELIE', db_key, data)

    def add_member(self, ns: str, group: str, members: Set[bytes]) -> None:
        db_key = self._add_key_ns_prefix(ns, group)
        with _map_to_sdl_exception():
            self.__redis.sadd(db_key, *members)

    def remove_member(self, ns: str, group: str, members: Set[bytes]) -> None:
        db_key = self._add_key_ns_prefix(ns, group)
        with _map_to_sdl_exception():
            self.__redis.srem(db_key, *members)

    def remove_group(self, ns: str, group: str) -> None:
        db_key = self._add_key_ns_prefix(ns, group)
        with _map_to_sdl_exception():
            self.__redis.delete(db_key)

    def get_members(self, ns: str, group: str) -> Set[bytes]:
        db_key = self._add_key_ns_prefix(ns, group)
        with _map_to_sdl_exception():
            return self.__redis.smembers(db_key)

    def is_member(self, ns: str, group: str, member: bytes) -> bool:
        db_key = self._add_key_ns_prefix(ns, group)
        with _map_to_sdl_exception():
            return self.__redis.sismember(db_key, member)

    def group_size(self, ns: str, group: str) -> int:
        db_key = self._add_key_ns_prefix(ns, group)
        with _map_to_sdl_exception():
            return self.__redis.scard(db_key)

    @classmethod
    def _add_key_ns_prefix(cls, ns: str, key: str):
        return '{' + ns + '},' + key

    @classmethod
    def _add_keys_ns_prefix(cls, ns: str, keylist: List[str]) -> List[str]:
        ret_nskeys = []
        for k in keylist:
            ret_nskeys.append('{' + ns + '},' + k)
        return ret_nskeys

    @classmethod
    def _add_data_map_ns_prefix(cls, ns: str, data_dict: Dict[str, bytes]) -> Dict[str, bytes]:
        ret_nsdict = {}
        for key, val in data_dict.items():
            ret_nsdict['{' + ns + '},' + key] = val
        return ret_nsdict

    @classmethod
    def _strip_ns_from_bin_keys(cls, ns: str, nskeylist: List[bytes]) -> List[str]:
        ret_keys = []
        for k in nskeylist:
            try:
                redis_key = k.decode("utf-8")
            except UnicodeDecodeError as exc:
                msg = u'Namespace %s key conversion to string failed: %s' % (ns, str(exc))
                raise RejectedByBackend(msg)
            nskey = redis_key.split(',', 1)
            if len(nskey) != 2:
                msg = u'Namespace %s key:%s has no namespace prefix' % (ns, redis_key)
                raise RejectedByBackend(msg)
            ret_keys.append(nskey[1])
        return ret_keys

    def get_redis_connection(self):
        """Return existing Redis database connection."""
        return self.__redis


class RedisBackendLock(DbBackendLockAbc):
    """
    A class providing an implementation of database backend lock of Shared Data Layer (SDL), when
    backend database solution is Redis.

    Args:
        ns (str): Namespace under which this lock is targeted.
        name (str): Lock name, identifies the lock key in a Redis database backend.
        expiration (int, float): Lock expiration time after which the lock is removed if it hasn't
                                 been released earlier by a 'release' method.
        redis_backend (RedisBackend): Database backend object containing connection to Redis
                                      database.
    """
    lua_get_validity_time = None
    # KEYS[1] - lock name
    # ARGS[1] - token
    # return < 0 in case of failure, otherwise return lock validity time in milliseconds.
    LUA_GET_VALIDITY_TIME_SCRIPT = """
        local token = redis.call('get', KEYS[1])
        if not token then
            return -10
        end
        if token ~= ARGV[1] then
            return -11
        end
        return redis.call('pttl', KEYS[1])
    """

    def __init__(self, ns: str, name: str, expiration: Union[int, float],
                 redis_backend: RedisBackend) -> None:
        super().__init__(ns, name)
        self.__redis = redis_backend.get_redis_connection()
        with _map_to_sdl_exception():
            redis_lockname = '{' + ns + '},' + self._lock_name
            self.__redis_lock = Lock(redis=self.__redis, name=redis_lockname, timeout=expiration)
            self._register_scripts()

    def __str__(self):
        return str(
            {
                "lock DB type": "Redis",
                "lock namespace": self._ns,
                "lock name": self._lock_name,
                "lock status": self._lock_status_to_string()
            }
        )

    def acquire(self, retry_interval: Union[int, float] = 0.1,
                retry_timeout: Union[int, float] = 10) -> bool:
        succeeded = False
        self.__redis_lock.sleep = retry_interval
        with _map_to_sdl_exception():
            succeeded = self.__redis_lock.acquire(blocking_timeout=retry_timeout)
        return succeeded

    def release(self) -> None:
        with _map_to_sdl_exception():
            self.__redis_lock.release()

    def refresh(self) -> None:
        with _map_to_sdl_exception():
            self.__redis_lock.reacquire()

    def get_validity_time(self) -> Union[int, float]:
        validity = 0
        if self.__redis_lock.local.token is None:
            msg = u'Cannot get validity time of an unlocked lock %s' % self._lock_name
            raise RejectedByBackend(msg)

        with _map_to_sdl_exception():
            validity = self.lua_get_validity_time(keys=[self.__redis_lock.name],
                                                  args=[self.__redis_lock.local.token],
                                                  client=self.__redis)
        if validity < 0:
            msg = (u'Getting validity time of a lock %s failed with error code: %d'
                   % (self._lock_name, validity))
            raise RejectedByBackend(msg)
        ftime = validity / 1000.0
        if ftime.is_integer():
            return int(ftime)
        return ftime

    def _register_scripts(self):
        cls = self.__class__
        client = self.__redis
        if cls.lua_get_validity_time is None:
            cls.lua_get_validity_time = client.register_script(cls.LUA_GET_VALIDITY_TIME_SCRIPT)

    def _lock_status_to_string(self) -> str:
        try:
            if self.__redis_lock.locked():
                if self.__redis_lock.owned():
                    return 'locked'
                return 'locked by someone else'
            return 'unlocked'
        except(redis_exceptions.RedisError) as exc:
            return f'Error: {str(exc)}'

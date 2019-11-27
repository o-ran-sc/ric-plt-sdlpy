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

"""The module provides implementation of the syncronous shareddatalayer interface."""
import builtins
from typing import (Dict, Set, List, Union)
from ricsdl.configuration import _Configuration
from ricsdl.syncstorage_abc import (SyncStorageAbc, SyncLockAbc)
import ricsdl.backend
from ricsdl.backend.dbbackend_abc import DbBackendAbc
from ricsdl.exceptions import SdlTypeError


def func_arg_checker(exception, start_arg_idx, **types):
    """Decorator to validate function arguments."""
    def _check(func):
        if not __debug__:
            return func

        def _validate(*args, **kwds):
            for idx, arg in enumerate(args[start_arg_idx:], start_arg_idx):
                if func.__code__.co_varnames[idx] in types and \
                        not isinstance(arg, types[func.__code__.co_varnames[idx]]):
                    raise exception(r"Wrong argument type: '{}'={}. Must be: {}".
                                    format(func.__code__.co_varnames[idx], type(arg),
                                           types[func.__code__.co_varnames[idx]]))
            for kwdname, kwdval in kwds.items():
                if kwdname in types and not isinstance(kwdval, types[kwdname]):
                    raise exception(r"Wrong argument type: '{}'={}. Must be: {}".
                                    format(kwdname, type(kwdval), types[kwdname]))
            return func(*args, **kwds)
        _validate.__name__ = func.__name__
        return _validate
    return _check


class SyncLock(SyncLockAbc):
    """
    This class implements abstract 'SyncLockAbc' class.

    A lock instance is created per namespace and it is identified by its `name` within a namespace.

    Args:
        ns (str): Namespace under which this lock is targeted.
        name (str): Lock name, identifies the lock key in shared data layer storage.
        expiration (int, float): Lock expiration time after which the lock is removed if it hasn't
                                 been released earlier by a 'release' method.
        storage (SyncStorage): Database backend object containing connection to a database.
    """
    @func_arg_checker(SdlTypeError, 1, ns=str, name=str, expiration=(int, float))
    def __init__(self, ns: str, name: str, expiration: Union[int, float],
                 storage: 'SyncStorage') -> None:

        super().__init__(ns, name, expiration)
        self.__dbbackendlock = ricsdl.backend.get_backend_lock_instance(ns, name, expiration,
                                                                        storage.get_backend())

    def __str__(self):
        return str(
            {
                "namespace": self._ns,
                "name": self._name,
                "expiration": self._expiration,
                "backend lock": str(self.__dbbackendlock)
            }
        )

    @func_arg_checker(SdlTypeError, 1, retry_interval=(int, float),
                      retry_timeout=(int, float))
    def acquire(self, retry_interval: Union[int, float] = 0.1,
                retry_timeout: Union[int, float] = 10) -> bool:
        return self.__dbbackendlock.acquire(retry_interval, retry_timeout)

    def release(self) -> None:
        self.__dbbackendlock.release()

    def refresh(self) -> None:
        self.__dbbackendlock.refresh()

    def get_validity_time(self) -> Union[int, float]:
        return self.__dbbackendlock.get_validity_time()


class SyncStorage(SyncStorageAbc):
    """
    This class implements abstract 'SyncStorageAbc' class.

    This class provides synchronous access to all the namespaces in shared data layer storage.
    Data can be written, read and removed based on keys known to clients. Keys are unique within
    a namespace, namespace identifier is passed as a parameter to all the operations.

    Args:
        None
    """
    def __init__(self) -> None:
        super().__init__()
        self.__configuration = _Configuration()
        self.__dbbackend = ricsdl.backend.get_backend_instance(self.__configuration)

    def __del__(self):
        self.close()

    def __str__(self):
        return str(
            {
                "configuration": str(self.__configuration),
                "backend": str(self.__dbbackend)
            }
        )

    def close(self):
        self.__dbbackend.close()

    @func_arg_checker(SdlTypeError, 1, ns=str, data_map=dict)
    def set(self, ns: str, data_map: Dict[str, bytes]) -> None:
        self.__dbbackend.set(ns, data_map)

    @func_arg_checker(SdlTypeError, 1, ns=str, key=str, old_data=bytes, new_data=bytes)
    def set_if(self, ns: str, key: str, old_data: bytes, new_data: bytes) -> bool:
        return self.__dbbackend.set_if(ns, key, old_data, new_data)

    @func_arg_checker(SdlTypeError, 1, ns=str, key=str, data=bytes)
    def set_if_not_exists(self, ns: str, key: str, data: bytes) -> bool:
        return self.__dbbackend.set_if_not_exists(ns, key, data)

    @func_arg_checker(SdlTypeError, 1, ns=str, keys=(str, builtins.set))
    def get(self, ns: str, keys: Union[str, Set[str]]) -> Dict[str, bytes]:
        return self.__dbbackend.get(ns, list(keys))

    @func_arg_checker(SdlTypeError, 1, ns=str, key_prefix=str)
    def find_keys(self, ns: str, key_prefix: str) -> List[str]:
        return self.__dbbackend.find_keys(ns, key_prefix)

    @func_arg_checker(SdlTypeError, 1, ns=str, key_prefix=str, atomic=bool)
    def find_and_get(self, ns: str, key_prefix: str, atomic: bool) -> Dict[str, bytes]:
        return self.__dbbackend.find_and_get(ns, key_prefix, atomic)

    @func_arg_checker(SdlTypeError, 1, ns=str, keys=(str, builtins.set))
    def remove(self, ns: str, keys: Union[str, Set[str]]) -> None:
        self.__dbbackend.remove(ns, list(keys))

    @func_arg_checker(SdlTypeError, 1, ns=str, key=str, data=bytes)
    def remove_if(self, ns: str, key: str, data: bytes) -> bool:
        return self.__dbbackend.remove_if(ns, key, data)

    @func_arg_checker(SdlTypeError, 1, ns=str)
    def remove_all(self, ns: str) -> None:
        keys = self.__dbbackend.find_keys(ns, '')
        if keys:
            self.__dbbackend.remove(ns, keys)

    @func_arg_checker(SdlTypeError, 1, ns=str, group=str, members=(bytes, builtins.set))
    def add_member(self, ns: str, group: str, members: Union[bytes, Set[bytes]]) -> None:
        self.__dbbackend.add_member(ns, group, members)

    @func_arg_checker(SdlTypeError, 1, ns=str, group=str, members=(bytes, builtins.set))
    def remove_member(self, ns: str, group: str, members: Union[bytes, Set[bytes]]) -> None:
        self.__dbbackend.remove_member(ns, group, members)

    @func_arg_checker(SdlTypeError, 1, ns=str, group=str)
    def remove_group(self, ns: str, group: str) -> None:
        self.__dbbackend.remove_group(ns, group)

    @func_arg_checker(SdlTypeError, 1, ns=str, group=str)
    def get_members(self, ns: str, group: str) -> Set[bytes]:
        return self.__dbbackend.get_members(ns, group)

    @func_arg_checker(SdlTypeError, 1, ns=str, group=str, member=bytes)
    def is_member(self, ns: str, group: str, member: bytes) -> bool:
        return self.__dbbackend.is_member(ns, group, member)

    @func_arg_checker(SdlTypeError, 1, ns=str, group=str)
    def group_size(self, ns: str, group: str) -> int:
        return self.__dbbackend.group_size(ns, group)

    @func_arg_checker(SdlTypeError, 1, ns=str, resource=str, expiration=(int, float))
    def get_lock_resource(self, ns: str, resource: str, expiration: Union[int, float]) -> SyncLock:
        return SyncLock(ns, resource, expiration, self)

    def get_backend(self) -> DbBackendAbc:
        """Return backend instance."""
        return self.__dbbackend

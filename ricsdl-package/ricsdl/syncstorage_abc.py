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


"""The module provides synchronous Shared Data Layer (SDL) interface."""
from typing import (Dict, Set, List, Union)
from abc import ABC, abstractmethod
from ricsdl.exceptions import (
    RejectedByBackend
)

__all__ = [
    'SyncStorageAbc',
    'SyncLockAbc'
]


class SyncLockAbc(ABC):
    """
    An abstract synchronous Shared Data Layer (SDL) lock class providing a shared, distributed
    locking mechanism, which can be utilized by clients to be able to operate with a shared
    resource in a mutually exclusive way.

    A lock instance is created per namespace and it is identified by its `name` within a
    namespace.

    A concrete implementation subclass 'SyncLock' derives from this abstract class.

    Args:
        ns (str): Namespace under which this lock is targeted.
        name (str): Lock name, identifies the lock key in SDL storage.
        expiration (int, float): Lock expiration time after which the lock is removed if it hasn't
                                 been released earlier by a 'release' method.

    """
    def __init__(self, ns: str, name: str, expiration: Union[int, float]) -> None:
        super().__init__()
        self._ns = ns
        self._name = name
        self._expiration = expiration

    def __enter__(self, *args, **kwargs):
        if self.acquire(*args, **kwargs):
            return self
        raise RejectedByBackend("Unable to acquire lock within the time specified")

    def __exit__(self, exception_type, exception_value, traceback):
        self.release()

    def acquire(self, retry_interval: Union[int, float] = 0.1,
                retry_timeout: Union[int, float] = 10) -> bool:
        """
        Acquire a shared, distributed lock atomically.

        A lock can be used as a mutual exclusion locking entry for a shared resources.

        All the exceptions except SdlTypeError are derived from SdlException base class. Client
        can catch only that exception if separate handling for different SDL error situations is
        not needed. Exception SdlTypeError is derived from build-in TypeError and it indicates
        misuse of the SDL API.

        Args:
            retry_interval (int, float): Lock acquiring retry interval in seconds. Supports both
                                         integer and float numbers.
            retry_timeout (int, float): Lock acquiring timeout after which retries are stopped and
                                        error status is returned. Supports both integer and float
                                        numbers.

        Returns:
            bool: True for successful lock acquiring, false otherwise.

        Raises:
            SdlTypeError: If function's argument is of an inappropriate type.
            NotConnected: If SDL is not connected to the backend data storage.
            RejectedByBackend: If backend data storage rejects the request.
            BackendError: If the backend data storage fails to process the request.
        """
        pass

    def release(self) -> None:
        """
        Release a lock atomically.

        Release the already acquired lock.

        Exceptions thrown are all derived from SdlException base class. Client can catch only that
        exception if separate handling for different SDL error situations is not needed.

        Args:
            None

        Returns:
            None

        Raises:
            NotConnected: If SDL is not connected to the backend data storage.
            RejectedByBackend: If backend data storage rejects the request.
            BackendError: If the backend data storage fails to process the request.
        """
        pass

    def refresh(self) -> None:
        """
        Refresh the remaining validity time of the existing lock back to an initial value.

        Exceptions thrown are all derived from SdlException base class. Client can catch only that
        exception if separate handling for different SDL error situations is not needed.

        Args:
            None

        Returns:
            None

        Raises:
            NotConnected: If SDL is not connected to the backend data storage.
            RejectedByBackend: If backend data storage rejects the request.
            BackendError: If the backend data storage fails to process the request.
        """
        pass

    def get_validity_time(self) -> Union[int, float]:
        """
        Get atomically the remaining validity time of the lock in seconds.

        Return atomically time in seconds until the lock expires.

        Exceptions thrown are all derived from SdlException base class. Client can catch only that
        exception if separate handling for different SDL error situations is not needed.

        Args:
            None

        Returns:
            (int, float): Validity time of the lock in seconds.

        Raises:
            NotConnected: If SDL is not connected to the backend data storage.
            RejectedByBackend: If backend data storage rejects the request.
            BackendError: If the backend data storage fails to process the request.
        """
        pass


class SyncStorageAbc(ABC):
    """
    An abstract class providing synchronous access to Shared Data Layer (SDL) storage.

    This class provides synchronous access to all the namespaces in SDL storage.
    Data can be written, read and removed based on keys known to clients. Keys are unique within
    a namespace, namespace identifier is passed as a parameter to all the operations.

    A concrete implementation subclass 'SyncStorage' derives from this abstract class.
    """

    @abstractmethod
    def close(self):
        """
        Close the connection to SDL storage.

        Args:
            None

        Returns:
            None

        Raises:
            NotConnected: If SDL is not connected to the backend data storage.
            RejectedByBackend: If backend data storage rejects the request.
            BackendError: If the backend data storage fails to process the request.
        """
        pass

    @abstractmethod
    def set(self, ns: str, data_map: Dict[str, bytes]) -> None:
        """
        Write data to SDL storage.

        Writing is done atomically, i.e. either all succeeds, or all fails.
        All the exceptions except SdlTypeError are derived from SdlException base class. Client
        can catch only that exception if separate handling for different SDL error situations is
        not needed. Exception SdlTypeError is derived from build-in TypeError and it indicates
        misuse of the SDL API.

        Args:
            ns (str): Namespace under which this operation is targeted.
            data_map (dict of str: bytes): Data to be written.

        Returns:
            None

        Raises:
            SdlTypeError: If function's argument is of an inappropriate type.
            NotConnected: If SDL is not connected to the backend data storage.
            RejectedByBackend: If backend data storage rejects the request.
            BackendError: If the backend data storage fails to process the request.
        """
        pass

    @abstractmethod
    def set_if(self, ns: str, key: str, old_data: bytes, new_data: bytes) -> bool:
        """
        Conditionally modify the value of a key if the current value in data storage matches the
        user's last known value.

        All the exceptions except SdlTypeError are derived from SdlException base class. Client
        can catch only that exception if separate handling for different SDL error situations is
        not needed. Exception SdlTypeError is derived from build-in TypeError and it indicates
        misuse of the SDL API.

        Args:
            ns (str): Namespace under which this operation is targeted.
            key (str): Key for which data modification will be executed.
            old_data (bytes): Last known data.
            new_data (bytes): Data to be written.

        Returns:
            bool: True for successful modification, false if the user's last known data did not
                  match the current value in data storage.

        Raises:
            SdlTypeError: If function's argument is of an inappropriate type.
            NotConnected: If SDL is not connected to the backend data storage.
            RejectedByBackend: If backend data storage rejects the request.
            BackendError: If the backend data storage fails to process the request.
        """
        pass

    @abstractmethod
    def set_if_not_exists(self, ns: str, key: str, data: bytes) -> bool:
        """
        Write data to SDL storage if key does not exist.

        Conditionally set the value of a key. If key already exists, then its value is not
        modified. Checking the key existence and potential set operation is done as a one atomic
        operation.
        All the exceptions except SdlTypeError are derived from SdlException base class. Client
        can catch only that exception if separate handling for different SDL error situations is
        not needed. Exception SdlTypeError is derived from build-in TypeError and it indicates
        misuse of the SDL API.

        Args:
            ns (str): Namespace under which this operation is targeted.
            key (str): Key to be set.
            data (bytes): Data to be written.

        Returns:
            bool: True if key didn't exist yet and set operation was executed, false if key already
                  existed and thus its value was left untouched.

        Raises:
            SdlTypeError: If function's argument is of an inappropriate type.
            NotConnected: If SDL is not connected to the backend data storage.
            RejectedByBackend: If backend data storage rejects the request.
            BackendError: If the backend data storage fails to process the request.
        """
        pass

    @abstractmethod
    def get(self, ns: str, keys: Union[str, Set[str]]) -> Dict[str, bytes]:
        """
        Read data from SDL storage.

        Only those entries that are found will be returned.
        All the exceptions except SdlTypeError are derived from SdlException base class. Client
        can catch only that exception if separate handling for different SDL error situations is
        not needed. Exception SdlTypeError is derived from build-in TypeError and it indicates
        misuse of the SDL API.

        Args:
            ns (str): Namespace under which this operation is targeted.
            keys (str or set of str): One or multiple keys to be read.

        Returns:
            (dict of str: bytes): A dictionary mapping of a key to the read data from the storage.

        Raises:
            SdlTypeError: If function's argument is of an inappropriate type.
            NotConnected: If SDL is not connected to the backend data storage.
            RejectedByBackend: If backend data storage rejects the request.
            BackendError: If the backend data storage fails to process the request.
        """
        pass

    @abstractmethod
    def find_keys(self, ns: str, key_pattern: str) -> List[str]:
        r"""
        Find all keys matching search pattern under the namespace.

        Supported glob-style patterns:
            `?` matches any single character. For example `?at` matches Cat, cat, Bat or bat.
            `*` matches any number of any characters including none. For example `*Law*` matches
                Law, GrokLaw, or Lawyer.
            `[abc]` matches one character given in the bracket. For example `[CB]at` matches Cat or
                    Bat.
            `[a-z]` matches one character from the range given in the bracket. For example
                    `Letter[0-9]` matches Letter0 up to Letter9.
            `[^abc]` matches any single character what is not given in the bracket. For example
                     `h[^e]llo` matches hallo, hillo but not hello.

        If searched key itself contains a special character, use a backslash (\) character to
        escape the special character to match it verbatim.

        NOTE: `find_keys` function is not guaranteed to be atomic or isolated.

        All the exceptions except SdlTypeError are derived from SdlException base class. Client
        can catch only that exception if separate handling for different SDL error situations is
        not needed. Exception SdlTypeError is derived from build-in TypeError and it indicates
        misuse of the SDL API.

        Args:
            ns (str): Namespace under which this operation is targeted.
            key_pattern (str): Key search pattern.

        Returns:
            (list of str): A list of found keys.

        Raises:
            SdlTypeError: If function's argument is of an inappropriate type.
            NotConnected: If SDL is not connected to the backend data storage.
            RejectedByBackend: If backend data storage rejects the request.
            BackendError: If the backend data storage fails to process the request.
        """
        pass

    @abstractmethod
    def find_and_get(self, ns: str, key_pattern: str) -> Dict[str, bytes]:
        r"""
        Find keys and get their respective data from SDL storage.

        Supported glob-style patterns:
            `?` matches any single character. For example `?at` matches Cat, cat, Bat or bat.
            `*` matches any number of any characters including none. For example `*Law*` matches
                Law, GrokLaw, or Lawyer.
            `[abc]` matches one character given in the bracket. For example `[CB]at` matches Cat or
                    Bat.
            `[a-z]` matches one character from the range given in the bracket. For example
                    `Letter[0-9]` matches Letter0 up to Letter9.
            `[^abc]` matches any single character what is not given in the bracket. For example
                     `h[^e]llo` matches hallo, hillo but not hello.

        If searched key itself contains a special character, use a backslash (\) character to
        escape the special character to match it verbatim.

        NOTE: `find_and_get` function is not guaranteed to be atomic or isolated.

        All the exceptions except SdlTypeError are derived from SdlException base class. Client
        can catch only that exception if separate handling for different SDL error situations is
        not needed. Exception SdlTypeError is derived from build-in TypeError and it indicates
        misuse of the SDL API.

        Args:
            ns (str): Namespace under which this operation is targeted.
            key_pattern (str): Key search pattern.

        Returns:
            (dict of str: bytes): A dictionary mapping of a key to the read data from the storage.

        Raises:
            SdlTypeError: If function's argument is of an inappropriate type.
            NotConnected: If SDL is not connected to the backend data storage.
            RejectedByBackend: If backend data storage rejects the request.
            BackendError: If the backend data storage fails to process the request.
        """
        pass

    @abstractmethod
    def remove(self, ns: str, keys: Union[str, Set[str]]) -> None:
        """
        Remove data from SDL storage. Existing keys are removed.

        Removing is done atomically, i.e. either all succeeds, or all fails.
        All the exceptions except SdlTypeError are derived from SdlException base class. Client
        can catch only that exception if separate handling for different SDL error situations is
        not needed. Exception SdlTypeError is derived from build-in TypeError and it indicates
        misuse of the SDL API.

        Args:
            ns (str): Namespace under which this operation is targeted.
            keys (str or set of str): One key or multiple keys, which data is to be removed.

        Returns:
            None

        Raises:
            SdlTypeError: If function's argument is of an inappropriate type.
            NotConnected: If SDL is not connected to the backend data storage.
            RejectedByBackend: If backend data storage rejects the request.
            BackendError: If the backend data storage fails to process the request.
        """
        pass

    @abstractmethod
    def remove_if(self, ns: str, key: str, data: bytes) -> bool:
        """
        Conditionally remove data from SDL storage if the current data value matches the user's
        last known value.

        All the exceptions except SdlTypeError are derived from SdlException base class. Client
        can catch only that exception if separate handling for different SDL error situations is
        not needed. Exception SdlTypeError is derived from build-in TypeError and it indicates
        misuse of the SDL API.

        Args:
            ns (str): Namespace under which this operation is targeted.
            key (str): Key, which data is to be removed.
            data (bytes): Last known value of data

        Returns:
            bool: True if successful removal, false if the user's last known data did not match the
                  current value in data storage.

        Raises:
            SdlTypeError: If function's argument is of an inappropriate type.
            NotConnected: If SDL is not connected to the backend data storage.
            RejectedByBackend: If backend data storage rejects the request.
            BackendError: If the backend data storage fails to process the request.
        """
        pass

    @abstractmethod
    def remove_all(self, ns: str) -> None:
        """
        Remove all keys under the namespace.

        No prior knowledge about the keys in the given namespace exists, thus operation is not
        guaranteed to be atomic or isolated.
        All the exceptions except SdlTypeError are derived from SdlException base class. Client
        can catch only that exception if separate handling for different SDL error situations is
        not needed. Exception SdlTypeError is derived from build-in TypeError and it indicates
        misuse of the SDL API.

        Args:
            ns (str): Namespace under which this operation is targeted.

        Returns:
            None

        Raises:
            SdlTypeError: If function's argument is of an inappropriate type.
            NotConnected: If SDL is not connected to the backend data storage.
            RejectedByBackend: If backend data storage rejects the request.
            BackendError: If the backend data storage fails to process the request.
        """
        pass

    @abstractmethod
    def add_member(self, ns: str, group: str, members: Union[bytes, Set[bytes]]) -> None:
        """
        Add new members to a SDL group under the namespace.

        SDL groups are identified by their name, which is a key in storage. SDL groups are
        unordered collections of members where each member is unique. If a member to be added is
        already a member of the group, its addition is silently ignored. If the group does not
        exist, it is created, and specified members are added to the group.
        All the exceptions except SdlTypeError are derived from SdlException base class. Client
        can catch only that exception if separate handling for different SDL error situations is
        not needed. Exception SdlTypeError is derived from build-in TypeError and it indicates
        misuse of the SDL API.

        Args:
            ns (str): Namespace under which this operation is targeted.
            group (str): Group name.
            members (bytes or set of bytes): One or multiple members to be added.

        Returns:
            None

        Raises:
            SdlTypeError: If function's argument is of an inappropriate type.
            NotConnected: If SDL is not connected to the backend data storage.
            RejectedByBackend: If backend data storage rejects the request.
            BackendError: If the backend data storage fails to process the request.
        """
        pass

    @abstractmethod
    def remove_member(self, ns: str, group: str, members: Union[bytes, Set[bytes]]) -> None:
        """
        Remove members from a SDL group.

        SDL groups are unordered collections of members where each member is unique. If a member to
        be removed does not exist in the group, its removal is silently ignored. If a group does
        not exist, it is treated as an empty group and hence members removal is silently ignored.
        All the exceptions except SdlTypeError are derived from SdlException base class. Client
        can catch only that exception if separate handling for different SDL error situations is
        not needed. Exception SdlTypeError is derived from build-in TypeError and it indicates
        misuse of the SDL API.

        Args:
            ns (str): Namespace under which this operation is targeted.
            group (str): Group name.
            members (bytes or set of bytes): One or multiple members to be removed.

        Returns:
            None

        Raises:
            SdlTypeError: If function's argument is of an inappropriate type.
            NotConnected: If SDL is not connected to the backend data storage.
            RejectedByBackend: If backend data storage rejects the request.
            BackendError: If the backend data storage fails to process the request.
        """
        pass

    @abstractmethod
    def remove_group(self, ns: str, group: str) -> None:
        """
        Remove a SDL group along with its members.

        SDL groups are unordered collections of members where each member is unique. If a group to
        be removed does not exist, its removal is silently ignored.
        All the exceptions except SdlTypeError are derived from SdlException base class. Client
        can catch only that exception if separate handling for different SDL error situations is
        not needed. Exception SdlTypeError is derived from build-in TypeError and it indicates
        misuse of the SDL API.

        Args:
            ns (str): Namespace under which this operation is targeted.
            group (str): Group name to be removed.

        Returns:
            None

        Raises:
            SdlTypeError: If function's argument is of an inappropriate type.
            NotConnected: If SDL is not connected to the backend data storage.
            RejectedByBackend: If backend data storage rejects the request.
            BackendError: If the backend data storage fails to process the request.
        """
        pass

    @abstractmethod
    def get_members(self, ns: str, group: str) -> Set[bytes]:
        """
        Get all the members of a SDL group.

        SDL groups are unordered collections of members where each member is unique. If the group
        does not exist, empty set is returned.
        All the exceptions except SdlTypeError are derived from SdlException base class. Client
        can catch only that exception if separate handling for different SDL error situations is
        not needed. Exception SdlTypeError is derived from build-in TypeError and it indicates
        misuse of the SDL API.

        Args:
            ns (str): Namespace under which this operation is targeted.
            group (str): Group name of which members are to be returned.

        Returns:
            (set of bytes): A set of the members of the group.
            None

        Raises:
            SdlTypeError: If function's argument is of an inappropriate type.
            NotConnected: If SDL is not connected to the backend data storage.
            RejectedByBackend: If backend data storage rejects the request.
            BackendError: If the backend data storage fails to process the request.
        """
        pass

    @abstractmethod
    def is_member(self, ns: str, group: str, member: bytes) -> bool:
        """
        Validate if a given member is in the SDL group.

        SDL groups are unordered collections of members where each member is unique. If the group
        does not exist, false is returned.
        All the exceptions except SdlTypeError are derived from SdlException base class. Client
        can catch only that exception if separate handling for different SDL error situations is
        not needed. Exception SdlTypeError is derived from build-in TypeError and it indicates
        misuse of the SDL API.

        Args:
            ns (str): Namespace under which this operation is targeted.
            group (str): Group name of which member existence is to be validated.
            member (bytes): A member, which existence is to be validated.

        Returns:
            bool: True if member was in the group, false otherwise.

        Raises:
            SdlTypeError: If function's argument is of an inappropriate type.
            NotConnected: If SDL is not connected to the backend data storage.
            RejectedByBackend: If backend data storage rejects the request.
            BackendError: If the backend data storage fails to process the request.
        """
        pass

    @abstractmethod
    def group_size(self, ns: str, group: str) -> int:
        """
        Return the number of members in a group.

        SDL groups are unordered collections of members where each member is unique. If the group
        does not exist, value 0 is returned.
        All the exceptions except SdlTypeError are derived from SdlException base class. Client
        can catch only that exception if separate handling for different SDL error situations is
        not needed. Exception SdlTypeError is derived from build-in TypeError and it indicates
        misuse of the SDL API.

        Args:
            ns (str): Namespace under which this operation is targeted.
            group (str): Group name of which members count is queried.

        Returns:
            int: Number of members in a group.

        Raises:
            SdlTypeError: If function's argument is of an inappropriate type.
            NotConnected: If SDL is not connected to the backend data storage.
            RejectedByBackend: If backend data storage rejects the request.
            BackendError: If the backend data storage fails to process the request.
        """
        pass

    @abstractmethod
    def get_lock_resource(self, ns: str, resource: str,
                          expiration: Union[int, float]) -> SyncLockAbc:
        """
        Return a lock resource for SDL.

        A lock resource instance is created per namespace and it is identified by its `name` within
        a namespace. A `get_lock_resource` returns a lock resource instance, it does not acquire
        a lock. Lock resource provides lock handling methods such as acquiring a lock, extend
        expiration time and releasing a lock.
        All the exceptions except SdlTypeError are derived from SdlException base class. Client
        can catch only that exception if separate handling for different SDL error situations is
        not needed. Exception SdlTypeError is derived from build-in TypeError and it indicates
        misuse of the SDL API.

        Args:
            ns (str): Namespace under which this operation is targeted.
            resource (str): Resource is used within namespace as a key for a lock entry in SDL.
            expiration (int, float): Expiration time of a lock

        Returns:
            SyncLockAbc: Lock resource instance.

        Raises:
            SdlTypeError: If function's argument is of an inappropriate type.
            NotConnected: If SDL is not connected to the backend data storage.
            RejectedByBackend: If backend data storage rejects the request.
            BackendError: If the backend data storage fails to process the request.
        """
        pass

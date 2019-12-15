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


from unittest.mock import patch, Mock
import pytest
from ricsdl.syncstorage import SyncStorage
from ricsdl.syncstorage import SyncLock
from ricsdl.syncstorage import func_arg_checker
from ricsdl.exceptions import SdlTypeError


@pytest.fixture()
def sync_storage_fixture(request):
    request.cls.ns = 'some-ns'
    request.cls.key = 'a'
    request.cls.keys = {'a', 'b'}
    request.cls.dm = {'a': b'1', 'b': b'2'}
    request.cls.old_data = b'1'
    request.cls.new_data = b'3'
    request.cls.keyprefix = 'x'
    request.cls.matchedkeys = ['x1', 'x2', 'x3', 'x4', 'x5']
    request.cls.group = 'some-group'
    request.cls.groupmembers = set([b'm1', b'm2'])
    request.cls.groupmember = b'm1'
    request.cls.lock_name = 'some-lock-name'
    request.cls.lock_int_expiration = 10
    request.cls.lock_float_expiration = 1.1

    with patch('ricsdl.backend.get_backend_instance') as mock_db_backend:
        storage = SyncStorage()
        request.cls.mock_db_backend = mock_db_backend.return_value
    request.cls.storage = storage
    yield


@pytest.mark.usefixtures('sync_storage_fixture')
class TestSyncStorage:
    def test_set_function_success(self):
        self.storage.set(self.ns, self.dm)
        self.mock_db_backend.set.assert_called_once_with(self.ns, self.dm)

    def test_set_function_can_raise_exception_for_wrong_argument(self):
        with pytest.raises(SdlTypeError):
            self.storage.set(123, {'a': b'v1'})
        with pytest.raises(SdlTypeError):
            self.storage.set('ns', [1, 2])

    def test_set_if_function_success(self):
        self.mock_db_backend.set_if.return_value = True
        ret = self.storage.set_if(self.ns, self.key, self.old_data, self.new_data)
        self.mock_db_backend.set_if.assert_called_once_with(self.ns, self.key, self.old_data,
                                                            self.new_data)
        assert ret is True

    def test_set_if_function_can_return_false_if_same_data_already_exists(self):
        self.mock_db_backend.set_if.return_value = False
        ret = self.storage.set_if(self.ns, self.key, self.old_data, self.new_data)
        self.mock_db_backend.set_if.assert_called_once_with(self.ns, self.key, self.old_data,
                                                            self.new_data)
        assert ret is False

    def test_set_if_function_can_raise_exception_for_wrong_argument(self):
        with pytest.raises(SdlTypeError):
            self.storage.set_if(0xbad, 'key', b'v1', b'v2')
        with pytest.raises(SdlTypeError):
            self.storage.set_if('ns', 0xbad, b'v1', b'v2')
        with pytest.raises(SdlTypeError):
            self.storage.set_if('ns', 'key', 0xbad, b'v2')
        with pytest.raises(SdlTypeError):
            self.storage.set_if('ns', 'key', b'v1', 0xbad)

    def test_set_if_not_exists_function_success(self):
        self.mock_db_backend.set_if_not_exists.return_value = True
        ret = self.storage.set_if_not_exists(self.ns, self.key, self.new_data)
        self.mock_db_backend.set_if_not_exists.assert_called_once_with(self.ns, self.key,
                                                                       self.new_data)
        assert ret is True

    def test_set_if_not_exists_function_can_return_false_if_key_already_exists(self):
        self.mock_db_backend.set_if_not_exists.return_value = False
        ret = self.storage.set_if_not_exists(self.ns, self.key, self.new_data)
        self.mock_db_backend.set_if_not_exists.assert_called_once_with(self.ns, self.key,
                                                                       self.new_data)
        assert ret is False

    def test_set_if_not_exists_function_can_raise_exception_for_wrong_argument(self):
        with pytest.raises(SdlTypeError):
            self.storage.set_if_not_exists(0xbad, 'key', b'v1')
        with pytest.raises(SdlTypeError):
            self.storage.set_if_not_exists('ns', 0xbad, b'v1')
        with pytest.raises(SdlTypeError):
            self.storage.set_if_not_exists('ns', 'key', 0xbad)

    def test_get_function_success(self):
        self.mock_db_backend.get.return_value = self.dm
        ret = self.storage.get(self.ns, self.keys)
        self.mock_db_backend.get.assert_called_once()
        call_args, _ = self.mock_db_backend.get.call_args
        assert call_args[0] == self.ns
        assert len(call_args[1]) == len(self.keys)
        assert all(k in call_args[1] for k in self.keys)
        assert ret == self.dm

    def test_get_function_can_return_empty_dict_when_no_key_values_exist(self):
        self.mock_db_backend.get.return_value = dict()
        ret = self.storage.get(self.ns, self.keys)
        self.mock_db_backend.get.assert_called_once()
        call_args, _ = self.mock_db_backend.get.call_args
        assert call_args[0] == self.ns
        assert len(call_args[1]) == len(self.keys)
        assert all(k in call_args[1] for k in self.keys)
        assert ret == dict()

    def test_get_function_can_raise_exception_for_wrong_argument(self):
        with pytest.raises(SdlTypeError):
            self.storage.get(0xbad, self.key)
        with pytest.raises(SdlTypeError):
            self.storage.get(self.ns, 0xbad)

    def test_find_keys_function_success(self):
        self.mock_db_backend.find_keys.return_value = self.matchedkeys
        ret = self.storage.find_keys(self.ns, self.keyprefix)
        self.mock_db_backend.find_keys.assert_called_once_with(self.ns, self.keyprefix)
        assert ret == self.matchedkeys

    def test_find_keys_function_can_return_empty_list_when_no_keys_exist(self):
        self.mock_db_backend.find_keys.return_value = list()
        ret = self.storage.find_keys(self.ns, self.keyprefix)
        self.mock_db_backend.find_keys.assert_called_once_with(self.ns, self.keyprefix)
        assert ret == list()

    def test_find_keys_function_can_raise_exception_for_wrong_argument(self):
        with pytest.raises(SdlTypeError):
            self.storage.find_keys(0xbad, self.keyprefix)
        with pytest.raises(SdlTypeError):
            self.storage.find_keys(self.ns, 0xbad)

    def test_find_and_get_function_success(self):
        self.mock_db_backend.find_and_get.return_value = self.dm
        ret = self.storage.find_and_get(self.ns, self.keyprefix)
        self.mock_db_backend.find_and_get.assert_called_once_with(self.ns, self.keyprefix)
        assert ret == self.dm

    def test_find_and_get_function_can_return_empty_dict_when_no_keys_exist(self):
        self.mock_db_backend.find_and_get.return_value = dict()
        ret = self.storage.find_and_get(self.ns, self.keyprefix)
        self.mock_db_backend.find_and_get.assert_called_once_with(self.ns, self.keyprefix)
        assert ret == dict()

    def test_find_and_get_function_can_raise_exception_for_wrong_argument(self):
        with pytest.raises(SdlTypeError):
            self.storage.find_and_get(0xbad, self.keyprefix)
        with pytest.raises(SdlTypeError):
            self.storage.find_and_get(self.ns, 0xbad)

    def test_remove_function_success(self):
        self.storage.remove(self.ns, self.keys)
        self.mock_db_backend.remove.assert_called_once()
        call_args, _ = self.mock_db_backend.remove.call_args
        assert call_args[0] == self.ns
        assert isinstance(call_args[1], list)
        assert len(call_args[1]) == len(self.keys)
        assert all(k in call_args[1] for k in self.keys)

    def test_remove_function_can_raise_exception_for_wrong_argument(self):
        with pytest.raises(SdlTypeError):
            self.storage.remove(0xbad, self.keys)
        with pytest.raises(SdlTypeError):
            self.storage.remove(self.ns, 0xbad)

    def test_remove_if_function_success(self):
        self.mock_db_backend.remove_if.return_value = True
        ret = self.storage.remove_if(self.ns, self.key, self.new_data)
        self.mock_db_backend.remove_if.assert_called_once_with(self.ns, self.key, self.new_data)
        assert ret is True

    def test_remove_if_function_can_return_false_if_data_does_not_match(self):
        self.mock_db_backend.remove_if.return_value = False
        ret = self.storage.remove_if(self.ns, self.key, self.old_data)
        self.mock_db_backend.remove_if.assert_called_once_with(self.ns, self.key, self.old_data)
        assert ret is False

    def test_remove_if_function_can_raise_exception_for_wrong_argument(self):
        with pytest.raises(SdlTypeError):
            self.storage.remove_if(0xbad, self.keys, self.old_data)
        with pytest.raises(SdlTypeError):
            self.storage.remove_if(self.ns, 0xbad, self.old_data)
        with pytest.raises(SdlTypeError):
            self.storage.remove_if(self.ns, self.keys, 0xbad)

    def test_remove_all_function_success(self):
        self.mock_db_backend.find_keys.return_value = ['a1']
        self.storage.remove_all(self.ns)
        self.mock_db_backend.find_keys.assert_called_once_with(self.ns, '*')
        self.mock_db_backend.remove.assert_called_once_with(self.ns,
                                                            self.mock_db_backend.find_keys.return_value)

    def test_remove_all_function_can_raise_exception_for_wrong_argument(self):
        with pytest.raises(SdlTypeError):
            self.storage.remove_all(0xbad)

    def test_add_member_function_success(self):
        self.storage.add_member(self.ns, self.group, self.groupmembers)
        self.mock_db_backend.add_member.assert_called_once_with(self.ns,
                                                                self.group, self.groupmembers)

    def test_add_member_function_can_raise_exception_for_wrong_argument(self):
        with pytest.raises(SdlTypeError):
            self.storage.add_member(0xbad, self.group, self.groupmembers)
        with pytest.raises(SdlTypeError):
            self.storage.add_member(self.ns, 0xbad, self.groupmembers)
        with pytest.raises(SdlTypeError):
            self.storage.add_member(self.ns, self.group, 0xbad)

    def test_remove_member_function_success(self):
        self.storage.remove_member(self.ns, self.group, self.groupmembers)
        self.mock_db_backend.remove_member.assert_called_once_with(self.ns, self.group,
                                                                   self.groupmembers)

    def test_remove_member_function_can_raise_exception_for_wrong_argument(self):
        with pytest.raises(SdlTypeError):
            self.storage.remove_member(0xbad, self.group, self.groupmembers)
        with pytest.raises(SdlTypeError):
            self.storage.remove_member(self.ns, 0xbad, self.groupmembers)
        with pytest.raises(SdlTypeError):
            self.storage.remove_member(self.ns, self.group, 0xbad)

    def test_remove_group_function_success(self):
        self.storage.remove_group(self.ns, self.group)
        self.mock_db_backend.remove_group.assert_called_once_with(self.ns, self.group)

    def test_remove_group_function_can_raise_exception_for_wrong_argument(self):
        with pytest.raises(SdlTypeError):
            self.storage.remove_group(0xbad, self.group)
        with pytest.raises(SdlTypeError):
            self.storage.remove_group(self.ns, 0xbad)

    def test_get_members_function_success(self):
        self.mock_db_backend.get_members.return_value = self.groupmembers
        ret = self.storage.get_members(self.ns, self.group)
        self.mock_db_backend.get_members.assert_called_once_with(self.ns, self.group)
        assert ret == self.groupmembers

    def test_get_members_function_can_raise_exception_for_wrong_argument(self):
        with pytest.raises(SdlTypeError):
            self.storage.get_members(0xbad, self.group)
        with pytest.raises(SdlTypeError):
            self.storage.get_members(self.ns, 0xbad)

    def test_is_member_function_success(self):
        self.mock_db_backend.is_member.return_value = True
        ret = self.storage.is_member(self.ns, self.group, self.groupmember)
        self.mock_db_backend.is_member.assert_called_once_with(self.ns, self.group,
                                                               self.groupmember)
        assert ret is True

    def test_is_member_function_can_raise_exception_for_wrong_argument(self):
        with pytest.raises(SdlTypeError):
            self.storage.is_member(0xbad, self.group, self.groupmember)
        with pytest.raises(SdlTypeError):
            self.storage.is_member(self.ns, 0xbad, self.groupmember)
        with pytest.raises(SdlTypeError):
            self.storage.is_member(self.ns, self.group, 0xbad)

    def test_group_size_function_success(self):
        self.mock_db_backend.group_size.return_value = 100
        ret = self.storage.group_size(self.ns, self.group)
        self.mock_db_backend.group_size.assert_called_once_with(self.ns, self.group)
        assert ret == 100

    def test_group_size_function_can_raise_exception_for_wrong_argument(self):
        with pytest.raises(SdlTypeError):
            self.storage.group_size(0xbad, self.group)
        with pytest.raises(SdlTypeError):
            self.storage.group_size(self.ns, 0xbad)

    @patch('ricsdl.syncstorage.SyncLock')
    def test_get_lock_resource_function_success_when_expiration_time_is_integer(self, mock_db_lock):
        ret = self.storage.get_lock_resource(self.ns, self.lock_name, self.lock_int_expiration)
        mock_db_lock.assert_called_once_with(self.ns, self.lock_name, self.lock_int_expiration,
                                             self.storage)
        assert ret == mock_db_lock.return_value

    @patch('ricsdl.syncstorage.SyncLock')
    def test_get_lock_resource_function_success_when_expiration_time_is_float_number(self,
                                                                                     mock_db_lock):
        ret = self.storage.get_lock_resource(self.ns, self.lock_name, self.lock_float_expiration)
        mock_db_lock.assert_called_once_with(self.ns, self.lock_name, self.lock_float_expiration,
                                             self.storage)
        assert ret == mock_db_lock.return_value

    def test_get_lock_resource_function_can_raise_exception_for_wrong_argument(self):
        with pytest.raises(SdlTypeError):
            self.storage.get_lock_resource(0xbad, self.lock_name, self.lock_int_expiration)
        with pytest.raises(SdlTypeError):
            self.storage.get_lock_resource(self.ns, 0xbad, self.lock_int_expiration)
        with pytest.raises(SdlTypeError):
            self.storage.get_lock_resource(self.ns, self.lock_name, 'bad')

    def test_get_backend_function_success(self):
        ret = self.storage.get_backend()
        assert ret == self.mock_db_backend

    def test_storage_object_string_representation(self):
        str_out = str(self.storage)
        assert str_out is not None


@pytest.fixture()
def lock_fixture(request):
    request.cls.ns = 'some-ns'
    request.cls.lockname = 'some-lock-name'
    request.cls.expiration = 10
    request.cls.retry_interval = 0.1
    request.cls.retry_timeout = 1

    with patch('ricsdl.backend.get_backend_lock_instance') as mock_db_backend_lock:
        lock = SyncLock('test-ns', 'test-lock-name', request.cls.expiration, Mock())
        request.cls.mock_db_backend_lock = mock_db_backend_lock.return_value
    request.cls.lock = lock
    yield


@pytest.mark.usefixtures('lock_fixture')
class TestSyncLock:
    def test_acquire_function_success_when_timeout_and_interval_are_integers(self):
        self.lock.acquire(self.retry_interval, self.retry_timeout)
        self.mock_db_backend_lock.acquire.assert_called_once_with(self.retry_interval,
                                                                  self.retry_timeout)

    def test_acquire_function_success_when_timeout_and_interval_are_float_numbers(self):
        self.lock.acquire(float(self.retry_interval), float(self.retry_timeout))
        self.mock_db_backend_lock.acquire.assert_called_once_with(float(self.retry_interval),
                                                                  float(self.retry_timeout))

    def test_acquire_function_can_raise_exception_for_wrong_argument(self):
        with pytest.raises(SdlTypeError):
            self.lock.acquire('bad', self.retry_timeout)
        with pytest.raises(SdlTypeError):
            self.lock.acquire(self.retry_interval, 'bad')

    def test_release_function_success(self):
        self.lock.release()
        self.mock_db_backend_lock.release.assert_called_once()

    def test_refresh_function_success(self):
        self.lock.refresh()
        self.mock_db_backend_lock.refresh.assert_called_once()

    def test_get_validity_time_function_success(self):
        self.mock_db_backend_lock.get_validity_time.return_value = self.expiration
        ret = self.lock.get_validity_time()
        self.mock_db_backend_lock.get_validity_time.assert_called_once()
        assert ret == self.expiration

    def test_get_validity_time_function_success_when_returned_time_is_float(self):
        self.mock_db_backend_lock.get_validity_time.return_value = float(self.expiration)
        ret = self.lock.get_validity_time()
        self.mock_db_backend_lock.get_validity_time.assert_called_once()
        assert ret == float(self.expiration)

    def test_lock_object_string_representation(self):
        str_out = str(self.lock)
        assert str_out is not None


def test_function_arg_validator():
    @func_arg_checker(SdlTypeError, 0, a=str, b=(int, float), c=set, d=(dict, type(None)))
    def _my_func(a='abc', b=1, c={'x', 'y'}, d={'x': b'1'}):
        pass
    with pytest.raises(SdlTypeError, match=r"Wrong argument type: 'a'=<class 'NoneType'>. "
                                           r"Must be: <class 'str'>"):
        _my_func(None)

    with pytest.raises(SdlTypeError, match=r"Wrong argument type: 'b'=<class 'str'>. "):
        _my_func('abc', 'wrong type')

    with pytest.raises(SdlTypeError, match=r"Wrong argument type: 'c'=<class 'str'>. "
                                           r"Must be: <class 'set'>"):
        _my_func('abc', 1.0, 'wrong type')

    with pytest.raises(SdlTypeError, match=r"Wrong argument type: 'd'=<class 'str'>. "):
        _my_func('abc', 1.0, {'x', 'y'}, 'wrong type')


def test_function_kwarg_validator():
    @func_arg_checker(SdlTypeError, 0, a=str, b=(int, float), c=set, d=(dict, type(None)))
    def _my_func(a='abc', b=1, c={'x', 'y'}, d={'x': b'1'}):
        pass
    with pytest.raises(SdlTypeError, match=r"Wrong argument type: 'a'=<class 'NoneType'>. "
                                           r"Must be: <class 'str'>"):
        _my_func(a=None)

    with pytest.raises(SdlTypeError, match=r"Wrong argument type: 'b'=<class 'str'>. "):
        _my_func(b='wrong type')

    with pytest.raises(SdlTypeError, match=r"Wrong argument type: 'c'=<class 'str'>. "
                                           r"Must be: <class 'set'>"):
        _my_func(c='wrong type')

    with pytest.raises(SdlTypeError, match=r"Wrong argument type: 'd'=<class 'str'>. "):
        _my_func(d='wrong type')

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
from redis import exceptions as redis_exceptions
import sdl.backend
from sdl.backend.redis import (RedisBackendLock, _map_to_sdl_exception)
from sdl.configuration import _Configuration
import sdl.exceptions


@pytest.fixture()
def redis_backend_fixture(request):
    request.cls.ns = 'some-ns'
    request.cls.dl_redis = [b'1', b'2']
    request.cls.dm = {'a': b'1', 'b': b'2'}
    request.cls.dm_redis = {'{some-ns},a': b'1', '{some-ns},b': b'2'}
    request.cls.key = 'a'
    request.cls.key_redis = '{some-ns},a'
    request.cls.keys = ['a', 'b']
    request.cls.keys_redis = ['{some-ns},a', '{some-ns},b']
    request.cls.data = b'123'
    request.cls.old_data = b'1'
    request.cls.new_data = b'3'
    request.cls.keyprefix = 'x?'
    request.cls.keyprefix_redis = r'{some-ns},x\?*'
    request.cls.matchedkeys = ['x1', 'x2', 'x3', 'x4', 'x5']
    request.cls.matchedkeys_redis = [b'{some-ns},x1', b'{some-ns},x2', b'{some-ns},x3',
                                     b'{some-ns},x4', b'{some-ns},x5']
    request.cls.matcheddata_dl_redis = [b'10', b'11', b'12', b'13', b'14']
    request.cls.matcheddata_dm = {'x1': b'10', 'x2': b'11', 'x3': b'12',
                                  'x4': b'13', 'x5': b'14'}
    request.cls.group = 'some-group'
    request.cls.group_redis = '{some-ns},some-group'
    request.cls.groupmembers = set([b'm1', b'm2'])
    request.cls.groupmember = b'm1'
    request.cls.is_atomic = True

    request.cls.configuration = Mock()
    mock_conf_params = _Configuration.Params(db_host=None,
                                             db_port=None,
                                             db_sentinel_port=None,
                                             db_sentinel_master_name=None)
    request.cls.configuration.get_params.return_value = mock_conf_params
    with patch('sdl.backend.redis.Redis') as mock_redis:
        db = sdl.backend.get_backend_instance(request.cls.configuration)
        request.cls.mock_redis = mock_redis.return_value
    request.cls.db = db

    yield

@pytest.mark.usefixtures('redis_backend_fixture')
class TestRedisBackend:
    def test_set_function_success(self):
        self.db.set(self.ns, self.dm)
        self.mock_redis.mset.assert_called_once_with(self.dm_redis)

    def test_set_function_can_map_redis_exception_to_sdl_exception(self):
        self.mock_redis.mset.side_effect = redis_exceptions.ResponseError('redis error!')
        with pytest.raises(sdl.exceptions.RejectedByBackend):
            self.db.set(self.ns, self.dm)

    def test_set_if_function_success(self):
        self.mock_redis.execute_command.return_value = True
        ret = self.db.set_if(self.ns, self.key, self.old_data, self.new_data)
        self.mock_redis.execute_command.assert_called_once_with('SETIE', self.key_redis,
                                                                self.new_data, self.old_data)
        assert ret is True

    def test_set_if_function_returns_false_if_same_data_already_exists(self):
        self.mock_redis.execute_command.return_value = False
        ret = self.db.set_if(self.ns, self.key, self.old_data, self.new_data)
        self.mock_redis.execute_command.assert_called_once_with('SETIE', self.key_redis,
                                                                self.new_data, self.old_data)
        assert ret is False

    def test_set_if_function_can_map_redis_exception_to_sdl_exception(self):
        self.mock_redis.execute_command.side_effect = redis_exceptions.ResponseError('redis error!')
        with pytest.raises(sdl.exceptions.RejectedByBackend):
            self.db.set_if(self.ns, self.key, self.old_data, self.new_data)

    def test_set_if_not_exists_function_success(self):
        self.mock_redis.setnx.return_value = True
        ret = self.db.set_if_not_exists(self.ns, self.key, self.new_data)
        self.mock_redis.setnx.assert_called_once_with(self.key_redis, self.new_data)
        assert ret is True

    def test_set_if_not_exists_function_returns_false_if_key_already_exists(self):
        self.mock_redis.setnx.return_value = False
        ret = self.db.set_if_not_exists(self.ns, self.key, self.new_data)
        self.mock_redis.setnx.assert_called_once_with(self.key_redis, self.new_data)
        assert ret is False

    def test_set_if_not_exists_function_can_map_redis_exception_to_sdl_exception(self):
        self.mock_redis.setnx.side_effect = redis_exceptions.ResponseError('redis error!')
        with pytest.raises(sdl.exceptions.RejectedByBackend):
            self.db.set_if_not_exists(self.ns, self.key, self.new_data)

    def test_get_function_success(self):
        self.mock_redis.mget.return_value = self.dl_redis
        ret = self.db.get(self.ns, self.keys)
        self.mock_redis.mget.assert_called_once_with(self.keys_redis)
        assert ret == self.dm

    def test_get_function_returns_empty_dict_when_no_key_values_exist(self):
        self.mock_redis.mget.return_value = [None, None]
        ret = self.db.get(self.ns, self.keys)
        self.mock_redis.mget.assert_called_once_with(self.keys_redis)
        assert ret == dict()

    def test_get_function_returns_dict_only_with_found_key_values_when_some_keys_exist(self):
        self.mock_redis.mget.return_value = [self.data, None]
        ret = self.db.get(self.ns, self.keys)
        self.mock_redis.mget.assert_called_once_with(self.keys_redis)
        assert ret == {self.key: self.data}

    def test_get_function_can_map_redis_exception_to_sdl_exception(self):
        self.mock_redis.mget.side_effect = redis_exceptions.ResponseError('redis error!')
        with pytest.raises(sdl.exceptions.RejectedByBackend):
            self.db.get(self.ns, self.keys)

    def test_find_keys_function_success(self):
        self.mock_redis.keys.return_value = self.matchedkeys_redis
        ret = self.db.find_keys(self.ns, self.keyprefix)
        self.mock_redis.keys.assert_called_once_with(self.keyprefix_redis)
        assert ret == self.matchedkeys

    def test_find_keys_function_returns_empty_list_when_no_matching_keys_found(self):
        self.mock_redis.keys.return_value = []
        ret = self.db.find_keys(self.ns, self.keyprefix)
        self.mock_redis.keys.assert_called_once_with(self.keyprefix_redis)
        assert ret == []

    def test_find_keys_function_can_map_redis_exception_to_sdl_exception(self):
        self.mock_redis.keys.side_effect = redis_exceptions.ResponseError('redis error!')
        with pytest.raises(sdl.exceptions.RejectedByBackend):
            self.db.find_keys(self.ns, self.keyprefix)

    def test_find_and_get_function_success(self):
        self.mock_redis.keys.return_value = self.matchedkeys_redis
        self.mock_redis.mget.return_value = self.matcheddata_dl_redis
        ret = self.db.find_and_get(self.ns, self.keyprefix, self.is_atomic)
        self.mock_redis.keys.assert_called_once_with(self.keyprefix_redis)
        self.mock_redis.mget.assert_called_once_with([i.decode() for i in self.matchedkeys_redis])
        assert ret == self.matcheddata_dm

    def test_find_and_get_function_returns_empty_dict_when_no_matching_keys_exist(self):
        self.mock_redis.keys.return_value = list()
        ret = self.db.find_and_get(self.ns, self.keyprefix, self.is_atomic)
        self.mock_redis.keys.assert_called_once_with(self.keyprefix_redis)
        assert not self.mock_redis.mget.called
        assert ret == dict()

    def test_remove_function_success(self):
        self.db.remove(self.ns, self.keys)
        self.mock_redis.delete.assert_called_once_with(*self.keys_redis)

    def test_remove_function_can_map_redis_exception_to_sdl_exception(self):
        self.mock_redis.delete.side_effect = redis_exceptions.ResponseError('redis error!')
        with pytest.raises(sdl.exceptions.RejectedByBackend):
            self.db.remove(self.ns, self.keys)

    def test_remove_if_function_success(self):
        self.mock_redis.execute_command.return_value = True
        ret = self.db.remove_if(self.ns, self.key, self.new_data)
        self.mock_redis.execute_command.assert_called_once_with('DELIE', self.key_redis,
                                                                self.new_data)
        assert ret is True

    def test_remove_if_function_returns_false_if_data_does_not_match(self):
        self.mock_redis.execute_command.return_value = False
        ret = self.db.remove_if(self.ns, self.key, self.new_data)
        self.mock_redis.execute_command.assert_called_once_with('DELIE', self.key_redis,
                                                                self.new_data)
        assert ret is False

    def test_remove_if_function_can_map_redis_exception_to_sdl_exception(self):
        self.mock_redis.execute_command.side_effect = redis_exceptions.ResponseError('redis error!')
        with pytest.raises(sdl.exceptions.RejectedByBackend):
            self.db.remove_if(self.ns, self.key, self.new_data)

    def test_add_member_function_success(self):
        self.db.add_member(self.ns, self.group, self.groupmembers)
        self.mock_redis.sadd.assert_called_once_with(self.group_redis, *self.groupmembers)

    def test_add_member_function_can_map_redis_exception_to_sdl_exception(self):
        self.mock_redis.sadd.side_effect = redis_exceptions.ResponseError('redis error!')
        with pytest.raises(sdl.exceptions.RejectedByBackend):
            self.db.add_member(self.ns, self.group, self.groupmembers)

    def test_remove_member_function_success(self):
        self.db.remove_member(self.ns, self.group, self.groupmembers)
        self.mock_redis.srem.assert_called_once_with(self.group_redis, *self.groupmembers)

    def test_remove_member_function_can_map_redis_exception_to_sdl_exception(self):
        self.mock_redis.srem.side_effect = redis_exceptions.ResponseError('redis error!')
        with pytest.raises(sdl.exceptions.RejectedByBackend):
            self.db.remove_member(self.ns, self.group, self.groupmembers)

    def test_remove_group_function_success(self):
        self.db.remove_group(self.ns, self.group)
        self.mock_redis.delete.assert_called_once_with(self.group_redis)

    def test_remove_group_function_can_map_redis_exception_to_sdl_exception(self):
        self.mock_redis.delete.side_effect = redis_exceptions.ResponseError('redis error!')
        with pytest.raises(sdl.exceptions.RejectedByBackend):
            self.db.remove_group(self.ns, self.group)

    def test_get_members_function_success(self):
        self.mock_redis.smembers.return_value = self.groupmembers
        ret = self.db.get_members(self.ns, self.group)
        self.mock_redis.smembers.assert_called_once_with(self.group_redis)
        assert ret is self.groupmembers

    def test_get_members_function_can_map_redis_exception_to_sdl_exception(self):
        self.mock_redis.smembers.side_effect = redis_exceptions.ResponseError('redis error!')
        with pytest.raises(sdl.exceptions.RejectedByBackend):
            self.db.get_members(self.ns, self.group)

    def test_is_member_function_success(self):
        self.mock_redis.sismember.return_value = True
        ret = self.db.is_member(self.ns, self.group, self.groupmember)
        self.mock_redis.sismember.assert_called_once_with(self.group_redis, self.groupmember)
        assert ret is True

    def test_is_member_function_can_map_redis_exception_to_sdl_exception(self):
        self.mock_redis.sismember.side_effect = redis_exceptions.ResponseError('redis error!')
        with pytest.raises(sdl.exceptions.RejectedByBackend):
            self.db.is_member(self.ns, self.group, self.groupmember)

    def test_group_size_function_success(self):
        self.mock_redis.scard.return_value = 100
        ret = self.db.group_size(self.ns, self.group)
        self.mock_redis.scard.assert_called_once_with(self.group_redis)
        assert ret == 100

    def test_group_size_function_can_map_redis_exception_to_sdl_exception(self):
        self.mock_redis.scard.side_effect = redis_exceptions.ResponseError('Some redis error!')
        with pytest.raises(sdl.exceptions.RejectedByBackend):
            self.db.group_size(self.ns, self.group)

    def test_get_redis_connection_function_success(self):
        ret = self.db.get_redis_connection()
        assert ret is self.mock_redis

    def test_redis_backend_object_string_representation(self):
        str_out = str(self.db)
        assert str_out is not None


class MockRedisLock:
    def __init__(self, redis, name, timeout=None, sleep=0.1,
                 blocking=True, blocking_timeout=None, thread_local=True):
        self.redis = redis
        self.name = name
        self.timeout = timeout
        self.sleep = sleep
        self.blocking = blocking
        self.blocking_timeout = blocking_timeout
        self.thread_local = bool(thread_local)


@pytest.fixture(scope="module")
def mock_redis_lock():
    def _mock_redis_lock(name, timeout=None, sleep=0.1,
                         blocking=True, blocking_timeout=None, thread_local=True):
        return MockRedisLock(name, timeout, sleep, blocking, blocking_timeout, thread_local)
    return _mock_redis_lock

@pytest.fixture()
def redis_backend_lock_fixture(request, mock_redis_lock):
    request.cls.ns = 'some-ns'
    request.cls.lockname = 'some-lock-name'
    request.cls.lockname_redis = '{some-ns},some-lock-name'
    request.cls.expiration = 10
    request.cls.retry_interval = 0.1
    request.cls.retry_timeout = 1

    request.cls.mock_lua_get_validity_time = Mock()
    request.cls.mock_lua_get_validity_time.return_value = 2000

    request.cls.mock_redis = Mock()
    request.cls.mock_redis.register_script = Mock()
    request.cls.mock_redis.register_script.return_value = request.cls.mock_lua_get_validity_time

    mocked_dbbackend = Mock()
    mocked_dbbackend.get_redis_connection.return_value = request.cls.mock_redis
    with patch('sdl.backend.redis.Lock') as mock_redis_lock:
        lock = sdl.backend.get_backend_lock_instance(request.cls.ns, request.cls.lockname,
                                                     request.cls.expiration, mocked_dbbackend)
        request.cls.mock_redis_lock = mock_redis_lock.return_value
        request.cls.lock = lock
    yield
    RedisBackendLock.lua_get_validity_time = None


@pytest.mark.usefixtures('redis_backend_lock_fixture')
class TestRedisBackendLock:
    def test_acquire_function_success(self):
        self.lock.acquire(self.retry_interval, self.retry_timeout)
        self.mock_redis_lock.acquire.assert_called_once_with(blocking_timeout=self.retry_timeout)

    def test_acquire_function_can_map_redis_exception_to_sdl_exception(self):
        self.mock_redis_lock.acquire.side_effect = redis_exceptions.LockError('redis lock error!')
        with pytest.raises(sdl.exceptions.BackendError):
            self.lock.acquire(self.retry_interval, self.retry_timeout)

    def test_release_function_success(self):
        self.lock.release()
        self.mock_redis_lock.release.assert_called_once()

    def test_release_function_can_map_redis_exception_to_sdl_exception(self):
        self.mock_redis_lock.release.side_effect = redis_exceptions.LockError('redis lock error!')
        with pytest.raises(sdl.exceptions.BackendError):
            self.lock.release()

    def test_refresh_function_success(self):
        self.lock.refresh()
        self.mock_redis_lock.reacquire.assert_called_once()

    def test_refresh_function_can_map_redis_exception_to_sdl_exception(self):
        self.mock_redis_lock.reacquire.side_effect = redis_exceptions.LockError('redis lock error!')
        with pytest.raises(sdl.exceptions.BackendError):
            self.lock.refresh()

    def test_get_validity_time_function_success(self):
        self.mock_redis_lock.name = self.lockname_redis
        self.mock_redis_lock.local.token = 123

        ret = self.lock.get_validity_time()
        self.mock_lua_get_validity_time.assert_called_once_with(
            keys=[self.lockname_redis], args=[123], client=self.mock_redis)
        assert ret == 2

    def test_get_validity_time_function_can_raise_exception_if_lock_is_unlocked(self):
        self.mock_redis_lock.name = self.lockname_redis
        self.mock_redis_lock.local.token = None

        with pytest.raises(sdl.exceptions.RejectedByBackend) as excinfo:
            self.lock.get_validity_time()
        assert f"Cannot get validity time of an unlocked lock {self.lockname}" in str(excinfo.value)

    def test_get_validity_time_function_can_raise_exception_if_lua_script_fails(self):
        self.mock_redis_lock.name = self.lockname_redis
        self.mock_redis_lock.local.token = 123
        self.mock_lua_get_validity_time.return_value = -10

        with pytest.raises(sdl.exceptions.RejectedByBackend) as excinfo:
            self.lock.get_validity_time()
        assert f"Getting validity time of a lock {self.lockname} failed with error code: -10" in str(excinfo.value)

    def test_redis_backend_lock_object_string_representation(self):
        str_out = str(self.lock)
        assert str_out is not None


def test_redis_response_error_exception_is_mapped_to_rejected_by_backend_sdl_exception():
    with pytest.raises(sdl.exceptions.RejectedByBackend) as excinfo:
        with _map_to_sdl_exception():
            raise redis_exceptions.ResponseError('Some redis error!')
    assert "shareddatalayer backend rejected the request: Some redis error!" in str(excinfo.value)

def test_redis_connection_error_exception_is_mapped_to_not_connected_sdl_exception():
    with pytest.raises(sdl.exceptions.NotConnected) as excinfo:
        with _map_to_sdl_exception():
            raise redis_exceptions.ConnectionError('Some redis error!')
    assert "shareddatalayer not connected to backend: Some redis error!" in str(excinfo.value)

def test_rest_redis_exceptions_are_mapped_to_backend_error_sdl_exception():
    with pytest.raises(sdl.exceptions.BackendError) as excinfo:
        with _map_to_sdl_exception():
            raise redis_exceptions.RedisError('Some redis error!')
    assert "shareddatalayer backend failed to process the request: Some redis error!" in str(excinfo.value)

def test_system_error_exceptions_are_not_mapped_to_any_sdl_exception():
    with pytest.raises(SystemExit):
        with _map_to_sdl_exception():
            raise SystemExit('Fatal error')

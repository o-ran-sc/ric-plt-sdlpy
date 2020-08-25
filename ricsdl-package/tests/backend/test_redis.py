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
import ricsdl.backend
from ricsdl.backend.redis import (RedisBackendLock, _map_to_sdl_exception)
from ricsdl.configuration import _Configuration
from ricsdl.configuration import DbBackendType
import ricsdl.exceptions


@pytest.fixture()
def redis_backend_fixture(request):
    request.cls.ns = 'some-ns'
    request.cls.dl_redis = [b'1', b'2']
    request.cls.dm = {'a': b'1', 'b': b'2'}
    request.cls.dm_redis = {'{some-ns},a': b'1', '{some-ns},b': b'2'}
    request.cls.dm_redis_flat = ['{some-ns},a', b'1', '{some-ns},b', b'2']
    request.cls.key = 'a'
    request.cls.key_redis = '{some-ns},a'
    request.cls.keys = ['a', 'b']
    request.cls.keys_redis = ['{some-ns},a', '{some-ns},b']
    request.cls.data = b'123'
    request.cls.old_data = b'1'
    request.cls.new_data = b'3'
    request.cls.keypattern = r'[Aa]bc-\[1\].?-*'
    request.cls.keypattern_redis = r'{some-ns},[Aa]bc-\[1\].?-*'
    request.cls.matchedkeys = ['Abc-[1].0-def', 'abc-[1].1-ghi']
    request.cls.matchedkeys_redis = [b'{some-ns},Abc-[1].0-def',
                                     b'{some-ns},abc-[1].1-ghi']
    request.cls.matcheddata_redis = [b'10', b'11']
    request.cls.matchedkeydata = {'Abc-[1].0-def': b'10',
                                  'abc-[1].1-ghi': b'11'}
    request.cls.group = 'some-group'
    request.cls.group_redis = '{some-ns},some-group'
    request.cls.groupmembers = set([b'm1', b'm2'])
    request.cls.groupmember = b'm1'
    request.cls.channels = ['abs', 'gma']
    request.cls.channels_and_events = {'abs': ['cbn']}
    request.cls.channels_and_events_redis = ['{some-ns},abs', 'cbn']

    request.cls.configuration = Mock()
    mock_conf_params = _Configuration.Params(db_host=None,
                                             db_port=None,
                                             db_sentinel_port=None,
                                             db_sentinel_master_name=None,
                                             db_type=DbBackendType.REDIS)
    request.cls.configuration.get_params.return_value = mock_conf_params
    with patch('ricsdl.backend.redis.Redis') as mock_redis, patch(
            'ricsdl.backend.redis.PubSub') as mock_pubsub:
        db = ricsdl.backend.get_backend_instance(request.cls.configuration)
        request.cls.mock_redis = mock_redis.return_value
        request.cls.mock_pubsub = mock_pubsub.return_value
    request.cls.db = db

    yield


@pytest.mark.usefixtures('redis_backend_fixture')
class TestRedisBackend:
    def test_is_connected_function_success(self):
        self.mock_redis.ping.return_value = True
        ret = self.db.is_connected()
        self.mock_redis.ping.assert_called_once()
        assert ret is True

    def test_is_connected_function_returns_false_if_ping_fails(self):
        self.mock_redis.ping.return_value = False
        ret = self.db.is_connected()
        self.mock_redis.ping.assert_called_once()
        assert ret is False

    def test_is_connected_function_can_map_redis_exception_to_sdl_exception(self):
        self.mock_redis.ping.side_effect = redis_exceptions.ResponseError('redis error!')
        with pytest.raises(ricsdl.exceptions.RejectedByBackend):
            self.db.is_connected()

    def test_set_function_success(self):
        self.db.set(self.ns, self.dm)
        self.mock_redis.mset.assert_called_once_with(self.dm_redis)

    def test_set_function_can_map_redis_exception_to_sdl_exception(self):
        self.mock_redis.mset.side_effect = redis_exceptions.ResponseError('redis error!')
        with pytest.raises(ricsdl.exceptions.RejectedByBackend):
            self.db.set(self.ns, self.dm)

    def test_set_if_function_success(self):
        self.mock_redis.execute_command.return_value = True
        ret = self.db.set_if(self.ns, self.key, self.old_data, self.new_data)
        self.mock_redis.execute_command.assert_called_once_with('SETIE', self.key_redis,
                                                                self.new_data, self.old_data)
        assert ret is True

    def test_set_if_function_returns_false_if_existing_key_value_not_expected(self):
        self.mock_redis.execute_command.return_value = False
        ret = self.db.set_if(self.ns, self.key, self.old_data, self.new_data)
        self.mock_redis.execute_command.assert_called_once_with('SETIE', self.key_redis,
                                                                self.new_data, self.old_data)
        assert ret is False

    def test_set_if_function_can_map_redis_exception_to_sdl_exception(self):
        self.mock_redis.execute_command.side_effect = redis_exceptions.ResponseError('redis error!')
        with pytest.raises(ricsdl.exceptions.RejectedByBackend):
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
        with pytest.raises(ricsdl.exceptions.RejectedByBackend):
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
        with pytest.raises(ricsdl.exceptions.RejectedByBackend):
            self.db.get(self.ns, self.keys)

    def test_find_keys_function_success(self):
        self.mock_redis.keys.return_value = self.matchedkeys_redis
        ret = self.db.find_keys(self.ns, self.keypattern)
        self.mock_redis.keys.assert_called_once_with(self.keypattern_redis)
        assert ret == self.matchedkeys

    def test_find_keys_function_returns_empty_list_when_no_matching_keys_found(self):
        self.mock_redis.keys.return_value = []
        ret = self.db.find_keys(self.ns, self.keypattern)
        self.mock_redis.keys.assert_called_once_with(self.keypattern_redis)
        assert ret == []

    def test_find_keys_function_can_map_redis_exception_to_sdl_exception(self):
        self.mock_redis.keys.side_effect = redis_exceptions.ResponseError('redis error!')
        with pytest.raises(ricsdl.exceptions.RejectedByBackend):
            self.db.find_keys(self.ns, self.keypattern)

    def test_find_keys_function_can_raise_exception_when_redis_key_convert_to_string_fails(self):
        # Redis returns an illegal key, which conversion to string fails
        corrupt_redis_key = b'\x81'
        self.mock_redis.keys.return_value = [corrupt_redis_key]
        with pytest.raises(ricsdl.exceptions.RejectedByBackend) as excinfo:
            self.db.find_keys(self.ns, self.keypattern)
        assert f"Namespace {self.ns} key:{corrupt_redis_key} "
        "has no namespace prefix" in str(excinfo.value)

    def test_find_keys_function_can_raise_exception_when_redis_key_is_without_prefix(self):
        # Redis returns an illegal key, which doesn't have comma separated namespace prefix
        corrupt_redis_key = 'some-corrupt-key'
        self.mock_redis.keys.return_value = [f'{corrupt_redis_key}'.encode()]
        with pytest.raises(ricsdl.exceptions.RejectedByBackend) as excinfo:
            self.db.find_keys(self.ns, self.keypattern)
        assert f"Namespace {self.ns} key:{corrupt_redis_key} "
        "has no namespace prefix" in str(excinfo.value)

    def test_find_and_get_function_success(self):
        self.mock_redis.keys.return_value = self.matchedkeys_redis
        self.mock_redis.mget.return_value = self.matcheddata_redis
        ret = self.db.find_and_get(self.ns, self.keypattern)
        self.mock_redis.keys.assert_called_once_with(self.keypattern_redis)
        self.mock_redis.mget.assert_called_once_with([i.decode() for i in self.matchedkeys_redis])
        assert ret == self.matchedkeydata

    def test_find_and_get_function_returns_empty_dict_when_no_matching_keys_exist(self):
        self.mock_redis.keys.return_value = list()
        ret = self.db.find_and_get(self.ns, self.keypattern)
        self.mock_redis.keys.assert_called_once_with(self.keypattern_redis)
        assert not self.mock_redis.mget.called
        assert ret == dict()

    def test_find_and_get_function_can_map_redis_exception_to_sdl_exception(self):
        self.mock_redis.keys.side_effect = redis_exceptions.ResponseError('redis error!')
        with pytest.raises(ricsdl.exceptions.RejectedByBackend):
            self.db.find_and_get(self.ns, self.keypattern)

    def test_find_and_get_function_can_raise_exception_when_redis_key_convert_to_string_fails(self):
        # Redis returns an illegal key, which conversion to string fails
        corrupt_redis_key = b'\x81'
        self.mock_redis.keys.return_value = [corrupt_redis_key]
        with pytest.raises(ricsdl.exceptions.RejectedByBackend) as excinfo:
            self.db.find_and_get(self.ns, self.keypattern)
        assert f"Namespace {self.ns} key:{corrupt_redis_key} "
        "has no namespace prefix" in str(excinfo.value)

    def test_find_and_get_function_can_raise_exception_when_redis_key_is_without_prefix(self):
        # Redis returns an illegal key, which doesn't have comma separated namespace prefix
        corrupt_redis_key = 'some-corrupt-key'
        self.mock_redis.keys.return_value = [f'{corrupt_redis_key}'.encode()]
        with pytest.raises(ricsdl.exceptions.RejectedByBackend) as excinfo:
            self.db.find_and_get(self.ns, self.keypattern)
        assert f"Namespace {self.ns} key:{corrupt_redis_key} "
        "has no namespace prefix" in str(excinfo.value)

    def test_remove_function_success(self):
        self.db.remove(self.ns, self.keys)
        self.mock_redis.delete.assert_called_once_with(*self.keys_redis)

    def test_remove_function_can_map_redis_exception_to_sdl_exception(self):
        self.mock_redis.delete.side_effect = redis_exceptions.ResponseError('redis error!')
        with pytest.raises(ricsdl.exceptions.RejectedByBackend):
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
        with pytest.raises(ricsdl.exceptions.RejectedByBackend):
            self.db.remove_if(self.ns, self.key, self.new_data)

    def test_add_member_function_success(self):
        self.db.add_member(self.ns, self.group, self.groupmembers)
        self.mock_redis.sadd.assert_called_once_with(self.group_redis, *self.groupmembers)

    def test_add_member_function_can_map_redis_exception_to_sdl_exception(self):
        self.mock_redis.sadd.side_effect = redis_exceptions.ResponseError('redis error!')
        with pytest.raises(ricsdl.exceptions.RejectedByBackend):
            self.db.add_member(self.ns, self.group, self.groupmembers)

    def test_remove_member_function_success(self):
        self.db.remove_member(self.ns, self.group, self.groupmembers)
        self.mock_redis.srem.assert_called_once_with(self.group_redis, *self.groupmembers)

    def test_remove_member_function_can_map_redis_exception_to_sdl_exception(self):
        self.mock_redis.srem.side_effect = redis_exceptions.ResponseError('redis error!')
        with pytest.raises(ricsdl.exceptions.RejectedByBackend):
            self.db.remove_member(self.ns, self.group, self.groupmembers)

    def test_remove_group_function_success(self):
        self.db.remove_group(self.ns, self.group)
        self.mock_redis.delete.assert_called_once_with(self.group_redis)

    def test_remove_group_function_can_map_redis_exception_to_sdl_exception(self):
        self.mock_redis.delete.side_effect = redis_exceptions.ResponseError('redis error!')
        with pytest.raises(ricsdl.exceptions.RejectedByBackend):
            self.db.remove_group(self.ns, self.group)

    def test_get_members_function_success(self):
        self.mock_redis.smembers.return_value = self.groupmembers
        ret = self.db.get_members(self.ns, self.group)
        self.mock_redis.smembers.assert_called_once_with(self.group_redis)
        assert ret is self.groupmembers

    def test_get_members_function_can_map_redis_exception_to_sdl_exception(self):
        self.mock_redis.smembers.side_effect = redis_exceptions.ResponseError('redis error!')
        with pytest.raises(ricsdl.exceptions.RejectedByBackend):
            self.db.get_members(self.ns, self.group)

    def test_is_member_function_success(self):
        self.mock_redis.sismember.return_value = True
        ret = self.db.is_member(self.ns, self.group, self.groupmember)
        self.mock_redis.sismember.assert_called_once_with(self.group_redis, self.groupmember)
        assert ret is True

    def test_is_member_function_can_map_redis_exception_to_sdl_exception(self):
        self.mock_redis.sismember.side_effect = redis_exceptions.ResponseError('redis error!')
        with pytest.raises(ricsdl.exceptions.RejectedByBackend):
            self.db.is_member(self.ns, self.group, self.groupmember)

    def test_group_size_function_success(self):
        self.mock_redis.scard.return_value = 100
        ret = self.db.group_size(self.ns, self.group)
        self.mock_redis.scard.assert_called_once_with(self.group_redis)
        assert ret == 100

    def test_group_size_function_can_map_redis_exception_to_sdl_exception(self):
        self.mock_redis.scard.side_effect = redis_exceptions.ResponseError('Some redis error!')
        with pytest.raises(ricsdl.exceptions.RejectedByBackend):
            self.db.group_size(self.ns, self.group)

    def test_set_and_publish_success(self):
        self.db.set_and_publish(self.ns, self.channels_and_events, self.dm)
        self.mock_redis.execute_command.assert_called_once_with('MSETMPUB', len(self.dm),
                                                                len(self.channels_and_events),
                                                                *self.dm_redis_flat,
                                                                *self.channels_and_events_redis)

    def test_set_and_publish_can_map_redis_exception_to_sdl_exception(self):
        self.mock_redis.execute_command.side_effect = redis_exceptions.ResponseError('redis error!')
        with pytest.raises(ricsdl.exceptions.RejectedByBackend):
            self.db.set_and_publish(self.ns, self.channels_and_events, self.dm)

    def test_set_if_and_publish_success(self):
        self.mock_redis.execute_command.return_value = b"OK"
        ret = self.db.set_if_and_publish(self.ns, self.channels_and_events, self.key, self.old_data,
                                         self.new_data)
        self.mock_redis.execute_command.assert_called_once_with('SETIEPUB', self.key_redis,
                                                                self.new_data, self.old_data,
                                                                *self.channels_and_events_redis)
        assert ret is True

    def test_set_if_and_publish_returns_false_if_existing_key_value_not_expected(self):
        self.mock_redis.execute_command.return_value = None
        ret = self.db.set_if_and_publish(self.ns, self.channels_and_events, self.key, self.old_data,
                                         self.new_data)
        self.mock_redis.execute_command.assert_called_once_with('SETIEPUB', self.key_redis,
                                                                self.new_data, self.old_data,
                                                                *self.channels_and_events_redis)
        assert ret is False

    def test_set_if_and_publish_can_map_redis_exception_to_sdl_exception(self):
        self.mock_redis.execute_command.side_effect = redis_exceptions.ResponseError('redis error!')
        with pytest.raises(ricsdl.exceptions.RejectedByBackend):
            self.db.set_if_and_publish(self.ns, self.channels_and_events, self.key, self.old_data,
                                       self.new_data)

    def test_set_if_not_exists_and_publish_success(self):
        self.mock_redis.execute_command.return_value = b"OK"
        ret = self.db.set_if_not_exists_and_publish(self.ns, self.channels_and_events, self.key,
                                                    self.new_data)
        self.mock_redis.execute_command.assert_called_once_with('SETNXPUB', self.key_redis,
                                                                self.new_data,
                                                                *self.channels_and_events_redis)
        assert ret is True

    def test_set_if_not_exists_and_publish_returns_false_if_key_already_exists(self):
        self.mock_redis.execute_command.return_value = None
        ret = self.db.set_if_not_exists_and_publish(self.ns, self.channels_and_events, self.key,
                                                    self.new_data)
        self.mock_redis.execute_command.assert_called_once_with('SETNXPUB', self.key_redis,
                                                                self.new_data,
                                                                *self.channels_and_events_redis)
        assert ret is False

    def set_if_not_exists_and_publish_can_map_redis_exception_to_sdl_exception(self):
        self.mock_redis.execute_command.side_effect = redis_exceptions.ResponseError('redis error!')
        with pytest.raises(ricsdl.exceptions.RejectedByBackend):
            self.db.set_if_not_exists_and_publish(self.ns, self.channels_and_events, self.key,
                                                  self.new_data)

    def test_remove_and_publish_success(self):
        self.db.remove_and_publish(self.ns, self.channels_and_events, self.key)
        self.mock_redis.execute_command.assert_called_once_with('DELMPUB', len(self.key),
                                                                len(self.channels_and_events),
                                                                self.key_redis,
                                                                *self.channels_and_events_redis)

    def test_remove_if_and_publish_success(self):
        self.mock_redis.execute_command.return_value = 1
        ret = self.db.remove_if_and_publish(self.ns, self.channels_and_events, self.key,
                                            self.new_data)
        self.mock_redis.execute_command.assert_called_once_with('DELIEPUB', self.key_redis,
                                                                self.new_data,
                                                                *self.channels_and_events_redis)
        assert ret is True

    def test_remove_if_and_publish_returns_false_if_data_does_not_match(self):
        self.mock_redis.execute_command.return_value = 0
        ret = self.db.remove_if_and_publish(self.ns, self.channels_and_events, self.key,
                                            self.new_data)
        self.mock_redis.execute_command.assert_called_once_with('DELIEPUB', self.key_redis,
                                                                self.new_data,
                                                                *self.channels_and_events_redis)
        assert ret is False

    def test_remove_if_and_publish_can_map_redis_exception_to_sdl_exception(self):
        self.mock_redis.execute_command.side_effect = redis_exceptions.ResponseError('redis error!')
        with pytest.raises(ricsdl.exceptions.RejectedByBackend):
            self.db.remove_if_and_publish(self.ns, self.channels_and_events, self.key,
                                          self.new_data)

    def test_remove_all_and_publish_success(self):
        self.mock_redis.keys.return_value = ['{some-ns},a']
        self.db.remove_all_and_publish(self.ns, self.channels_and_events)
        self.mock_redis.keys.assert_called_once()
        self.mock_redis.execute_command.assert_called_once_with('DELMPUB', len(self.key),
                                                                len(self.channels_and_events),
                                                                self.key_redis,
                                                                *self.channels_and_events_redis)

    def test_remove_all_and_publish_can_map_redis_exception_to_sdl_exception(self):
        self.mock_redis.execute_command.side_effect = redis_exceptions.ResponseError('redis error!')
        with pytest.raises(ricsdl.exceptions.RejectedByBackend):
            self.db.remove_all_and_publish(self.ns, self.channels_and_events)

    def test_subscribe_channel_success(self):
        cb = Mock()
        self.db.subscribe_channel(self.ns, cb, self.channels)
        for channel in self.channels:
            self.mock_pubsub.subscribe.assert_any_call(**{f'{{some-ns}},{channel}': cb})

    def test_subscribe_channel_with_thread_success(self):
        cb = Mock()
        self.db.pubsub_thread.is_alive = Mock()
        self.db.pubsub_thread.is_alive.return_value = False
        self.db._run_in_thread = True
        self.db.subscribe_channel(self.ns, cb, self.channels)
        self.mock_pubsub.run_in_thread.assert_called_once_with(daemon=True, sleep_time=0.001)

    def test_subscribe_can_map_redis_exception_to_sdl_exeception(self):
        self.mock_pubsub.subscribe.side_effect = redis_exceptions.ResponseError('redis error!')
        with pytest.raises(ricsdl.exceptions.RejectedByBackend):
            self.db.subscribe_channel(self.ns, Mock(), self.channels)

    def test_unsubscribe_channel_success(self):
        self.db.unsubscribe_channel(self.ns, [self.channels[0]])
        self.mock_pubsub.unsubscribe.assert_called_with('{some-ns},abs')

    def test_unsubscribe_channel_can_map_redis_exception_to_sdl_exeception(self):
        self.mock_pubsub.unsubscribe.side_effect = redis_exceptions.ResponseError('redis error!')
        with pytest.raises(ricsdl.exceptions.RejectedByBackend):
            self.db.unsubscribe_channel(self.ns, [self.channels[0]])

    def test_start_event_listener_success(self):
        self.db.start_event_listener()
        assert self.db._run_in_thread

    def test_start_event_listener_subscribe_first(self):
        self.mock_pubsub.run_in_thread.return_value = Mock()
        self.mock_redis.pubsub_channels.return_value = [b'{some-ns},abs']
        self.db.subscribe_channel(self.ns, Mock(), self.channels)
        self.db.start_event_listener()
        self.mock_pubsub.run_in_thread.assert_called_once_with(daemon=True, sleep_time=0.001)

    def test_start_event_listener_fail(self):
        self.db.pubsub_thread.is_alive = Mock()
        self.db.pubsub_thread.is_alive.return_value = True
        with pytest.raises(ricsdl.exceptions.RejectedByBackend):
            self.db.start_event_listener()

    def test_handle_events_success(self):
        self.db.handle_events()
        self.mock_pubsub.get_message.assert_called_once_with(ignore_subscribe_messages=True)

    def test_handle_events_fail_already_started(self):
        self.db.pubsub_thread.is_alive = Mock()
        self.db.pubsub_thread.is_alive.return_value = True
        with pytest.raises(ricsdl.exceptions.RejectedByBackend):
            self.db.handle_events()

    def test_handle_events_fail_already_set(self):
        self.db._run_in_thread = True
        with pytest.raises(ricsdl.exceptions.RejectedByBackend):
            self.db.handle_events()

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

    request.cls.configuration = Mock()
    mock_conf_params = _Configuration.Params(db_host=None,
                                             db_port=None,
                                             db_sentinel_port=None,
                                             db_sentinel_master_name=None,
                                             db_type=DbBackendType.REDIS)
    request.cls.configuration.get_params.return_value = mock_conf_params

    with patch('ricsdl.backend.redis.Lock') as mock_redis_lock:
        lock = ricsdl.backend.get_backend_lock_instance(request.cls.configuration,
                                                        request.cls.ns, request.cls.lockname,
                                                        request.cls.expiration, mocked_dbbackend)
        request.cls.mock_redis_lock = mock_redis_lock.return_value
        request.cls.lock = lock
    yield
    RedisBackendLock.lua_get_validity_time = None


@pytest.mark.usefixtures('redis_backend_lock_fixture')
class TestRedisBackendLock:
    def test_acquire_function_success(self):
        self.mock_redis_lock.acquire.return_value = True
        ret = self.lock.acquire(self.retry_interval, self.retry_timeout)
        self.mock_redis_lock.acquire.assert_called_once_with(blocking_timeout=self.retry_timeout)
        assert ret is True

    def test_acquire_function_returns_false_if_lock_is_not_acquired(self):
        self.mock_redis_lock.acquire.return_value = False
        ret = self.lock.acquire(self.retry_interval, self.retry_timeout)
        self.mock_redis_lock.acquire.assert_called_once_with(blocking_timeout=self.retry_timeout)
        assert ret is False

    def test_acquire_function_can_map_redis_exception_to_sdl_exception(self):
        self.mock_redis_lock.acquire.side_effect = redis_exceptions.LockError('redis lock error!')
        with pytest.raises(ricsdl.exceptions.BackendError):
            self.lock.acquire(self.retry_interval, self.retry_timeout)

    def test_release_function_success(self):
        self.lock.release()
        self.mock_redis_lock.release.assert_called_once()

    def test_release_function_can_map_redis_exception_to_sdl_exception(self):
        self.mock_redis_lock.release.side_effect = redis_exceptions.LockError('redis lock error!')
        with pytest.raises(ricsdl.exceptions.BackendError):
            self.lock.release()

    def test_refresh_function_success(self):
        self.lock.refresh()
        self.mock_redis_lock.reacquire.assert_called_once()

    def test_refresh_function_can_map_redis_exception_to_sdl_exception(self):
        self.mock_redis_lock.reacquire.side_effect = redis_exceptions.LockError('redis lock error!')
        with pytest.raises(ricsdl.exceptions.BackendError):
            self.lock.refresh()

    def test_get_validity_time_function_success(self):
        self.mock_redis_lock.name = self.lockname_redis
        self.mock_redis_lock.local.token = 123

        ret = self.lock.get_validity_time()
        self.mock_lua_get_validity_time.assert_called_once_with(
            keys=[self.lockname_redis], args=[123], client=self.mock_redis)
        assert ret == 2

    def test_get_validity_time_function_second_fraction_success(self):
        self.mock_redis_lock.name = self.lockname_redis
        self.mock_redis_lock.local.token = 123
        self.mock_lua_get_validity_time.return_value = 234

        ret = self.lock.get_validity_time()
        self.mock_lua_get_validity_time.assert_called_once_with(
            keys=[self.lockname_redis], args=[123], client=self.mock_redis)
        assert ret == 0.234

    def test_get_validity_time_function_can_raise_exception_if_lock_is_unlocked(self):
        self.mock_redis_lock.name = self.lockname_redis
        self.mock_redis_lock.local.token = None

        with pytest.raises(ricsdl.exceptions.RejectedByBackend) as excinfo:
            self.lock.get_validity_time()
        assert f"Cannot get validity time of an unlocked lock {self.lockname}" in str(excinfo.value)

    def test_get_validity_time_function_can_raise_exception_if_lua_script_fails(self):
        self.mock_redis_lock.name = self.lockname_redis
        self.mock_redis_lock.local.token = 123
        self.mock_lua_get_validity_time.return_value = -10

        with pytest.raises(ricsdl.exceptions.RejectedByBackend) as excinfo:
            self.lock.get_validity_time()
        assert f"Getting validity time of a lock {self.lockname} failed with error code: -10" in str(excinfo.value)

    def test_redis_backend_lock_object_string_representation(self):
        expected_lock_info = {'lock DB type': 'Redis',
                              'lock namespace': 'some-ns',
                              'lock name': 'some-lock-name',
                              'lock status': 'locked'}
        assert str(self.lock) == str(expected_lock_info)

    def test_redis_backend_lock_object_string_representation_can_catch_redis_exception(self):
        self.mock_redis_lock.owned.side_effect = redis_exceptions.LockError('redis lock error!')
        expected_lock_info = {'lock DB type': 'Redis',
                              'lock namespace': 'some-ns',
                              'lock name': 'some-lock-name',
                              'lock status': 'Error: redis lock error!'}
        assert str(self.lock) == str(expected_lock_info)


def test_redis_response_error_exception_is_mapped_to_rejected_by_backend_sdl_exception():
    with pytest.raises(ricsdl.exceptions.RejectedByBackend) as excinfo:
        with _map_to_sdl_exception():
            raise redis_exceptions.ResponseError('Some redis error!')
    assert "SDL backend rejected the request: Some redis error!" in str(excinfo.value)


def test_redis_connection_error_exception_is_mapped_to_not_connected_sdl_exception():
    with pytest.raises(ricsdl.exceptions.NotConnected) as excinfo:
        with _map_to_sdl_exception():
            raise redis_exceptions.ConnectionError('Some redis error!')
    assert "SDL not connected to backend: Some redis error!" in str(excinfo.value)


def test_rest_redis_exceptions_are_mapped_to_backend_error_sdl_exception():
    with pytest.raises(ricsdl.exceptions.BackendError) as excinfo:
        with _map_to_sdl_exception():
            raise redis_exceptions.RedisError('Some redis error!')
    assert "SDL backend failed to process the request: Some redis error!" in str(excinfo.value)


def test_system_error_exceptions_are_not_mapped_to_any_sdl_exception():
    with pytest.raises(SystemExit):
        with _map_to_sdl_exception():
            raise SystemExit('Fatal error')


class TestRedisClient:
    @classmethod
    def setup_class(cls):
        cls.pubsub = ricsdl.backend.redis.PubSub(Mock())
        cls.pubsub.channels = {b'{some-ns},abs': Mock()}

    def test_handle_pubsub_message(self):
        assert self.pubsub.handle_message([b'message', b'{some-ns},abs', b'cbn']) == ('abs', 'cbn')
        self.pubsub.channels.get(b'{some-ns},abs').assert_called_once_with('abs', 'cbn')

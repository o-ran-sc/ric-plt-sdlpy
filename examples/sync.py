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

"""
Examples how to use synchronous API functions of the Shareddatalayer.
Execution of  these examples requires:
 * Following Redis extension commands have been installed to runtime environment:
   - MSETPUB
   - SETIE
   - SETIEPUB
   - SETNXPUB
   - DELPUB
   - DELIE
   - DELIEPUB
   Redis v4.0 or greater is required. Older versions do not support extension modules.
   Implementation of above commands is produced by RIC DBaaS:
   https://gerrit.o-ran-sc.org/r/admin/repos/ric-plt/dbaas
   In official RIC deployments these commands are installed by `dbaas` service to Redis
   container(s).
   In development environment you may want install commands manually to pod/container, which is
   running Redis.
 * Following environment variables are needed to set to the pod/container where the application
   utilizing SDL is going to be run.
     DBAAS_SERVICE_HOST = [redis server address]
     DBAAS_SERVICE_PORT= [redis server port]
     DBAAS_MASTER_NAME = [master Redis sentinel name]. Needed to set only if sentinel is in use.
     DBAAS_SERVICE_SENTINEL_PORT = [Redis sentinel port number]. Needed to set only if sentinel
     is in use.
"""
from sdl.syncstorage import SyncStorage
from sdl.exceptions import RejectedByBackend, NotConnected, BackendError


"""
Constants used in the examples below.
"""
MY_NS = 'my_ns'
MY_GRP_NS = 'my_group_ns'
MY_LOCK_NS = 'my_group_ns'


# Creates SDL instance. The call creates connection to the SDL database backend.
try:
    mysdl = SyncStorage()
except RejectedByBackend as e:
    print(f'SDL instance creation failed: {str(e)}')
    #Permanent failure, just forward the exception
    raise
except (NotConnected, BackendError) as e:
    print(f'SDL instance creation failed for a temporal error: {str(e)}')
    #Here we could have a retry logic


# Sets a value 'my_value' for a key 'my_key' under given namespace. Note that value
# type must be bytes and multiple key values can be set in one set function call.
try:
    mysdl.set(MY_NS, {'my_key': b'my_value'})
except RejectedByBackend as e:
    print(f'SDL operation failed: {str(e)}')
    #Permanent failure, just forward the exception
    raise
except (NotConnected, BackendError) as e:
    print(f'SDL operation failed for a temporal error: {str(e)}')
    #Here we could have a retry logic


# Gets the value of 'my_value' under given namespace.
# Note that the type of returned value is bytes.
try:
    my_ret_dict = mysdl.get(MY_NS, {'my_key', 'someting not existing'})
    for key, val in my_ret_dict.items():
        assert val.decode("utf-8") == u'my_value'
except RejectedByBackend as e:
    print(f'SDL operation failed: {str(e)}')
    #Permanent failure, just forward the exception
    raise
except (NotConnected, BackendError) as e:
    print(f'SDL operation failed for a temporal error: {str(e)}')
    #Here we could have a retry logic


# Sets a value 'my_value2' for a key 'my_key' under given namespace only if the old value is
# 'my_value'.
# Note that value types must be bytes.
try:
    was_set = mysdl.set_if(MY_NS, 'my_key', b'my_value', b'my_value2')
    assert was_set == True
    was_set = mysdl.set_if(MY_NS, 'my_key', b'my_value', b'my_value2')
    assert was_set == False
except RejectedByBackend as e:
    print(f'SDL operation failed: {str(e)}')
    #Permanent failure, just forward the exception
    raise
except (NotConnected, BackendError) as e:
    print(f'SDL operation failed for a temporal error: {str(e)}')
    #Here we could have a retry logic


# Sets a value 'my_value' for a key 'my_key2' under given namespace only if the key does not exists.
# Note that value types must be bytes.
try:
    was_set = mysdl.set_if_not_exists(MY_NS, 'my_key2', b'my_value')
    assert was_set == True
    was_set = mysdl.set_if_not_exists(MY_NS, 'my_key2', b'my_value')
    assert was_set == False
except RejectedByBackend as e:
    print(f'SDL operation failed: {str(e)}')
    #Permanent failure, just forward the exception
    raise
except (NotConnected, BackendError) as e:
    print(f'SDL operation failed for a temporal error: {str(e)}')
    #Here we could have a retry logic


# Removes a key 'my_key' under given namespace.
try:
    mysdl.remove(MY_NS, 'my_key')
    my_ret_dict = mysdl.get(MY_NS, 'my_key')
    assert my_ret_dict == dict()
except RejectedByBackend as e:
    print(f'SDL operation failed: {str(e)}')
    #Permanent failure, just forward the exception
    raise
except (NotConnected, BackendError) as e:
    print(f'SDL operation failed for a temporal error: {str(e)}')
    #Here we could have a retry logic


# Removes a key 'my_key' under given namespace only if the old value is 'my_value'.
try:
    was_removed = mysdl.remove_if(MY_NS, 'my_key2', b'my_value')
    assert was_removed == True
    was_removed = mysdl.remove_if(MY_NS, 'my_key2', b'my_value')
    assert was_removed == False
except RejectedByBackend as e:
    print(f'SDL operation failed: {str(e)}')
    #Permanent failure, just forward the exception
    raise
except (NotConnected, BackendError) as e:
    print(f'SDL operation failed for a temporal error: {str(e)}')
    #Here we could have a retry logic


# Removes all the keys under given namespace.
try:
    mysdl.set(MY_NS, {'my_key': b'something'})
    my_ret_dict = mysdl.get(MY_NS, {'my_key'})
    assert my_ret_dict != dict()
    mysdl.remove_all(MY_NS)
    my_ret_dict = mysdl.get(MY_NS, {'my_key'})
    assert my_ret_dict == dict()
except RejectedByBackend as e:
    print(f'SDL operation failed: {str(e)}')
    #Permanent failure, just forward the exception
    raise
except (NotConnected, BackendError) as e:
    print(f'SDL operation failed for a temporal error: {str(e)}')
    #Here we could have a retry logic


# Finds keys under given namespace that are matching to given key prefix 'my_k'.
try:
    mysdl.set(MY_NS, {'my_key': b'my_value'})
    ret_keys = mysdl.find_keys(MY_NS, '')
    assert ret_keys == ['my_key']
except RejectedByBackend as e:
    print(f'SDL operation failed: {str(e)}')
    #Permanent failure, just forward the exception
    raise
except (NotConnected, BackendError) as e:
    print(f'SDL operation failed for a temporal error: {str(e)}')
    #Here we could have a retry logic


# Finds keys and their values under given namespace that are matching to given key prefix 'my_k'.
# Note that the type of returned value is bytes.
try:
    ret_key_values = mysdl.find_and_get(MY_NS, '', atomic=True)
    assert ret_key_values == {'my_key': b'my_value'}
    mysdl.remove_all(MY_NS)
except RejectedByBackend as e:
    print(f'SDL operation failed: {str(e)}')
    #Permanent failure, just forward the exception
    raise
except (NotConnected, BackendError) as e:
    print(f'SDL operation failed for a temporal error: {str(e)}')
    #Here we could have a retry logic


# Adds a member 'a' to group 'my_group' under given namespace.
# Note that member type must be bytes and multiple members can be set in one set function call.
try:
    mysdl.add_member(MY_GRP_NS, 'my_group', {b'a'})
except RejectedByBackend as e:
    print(f'SDL operation failed: {str(e)}')
    #Permanent failure, just forward the exception
    raise
except (NotConnected, BackendError) as e:
    print(f'SDL operation failed for a temporal error: {str(e)}')
    #Here we could have a retry logic


# Gets group 'my_group' members under given namespace.
# Note that the type of returned member is bytes.
try:
    ret_members = mysdl.get_members(MY_GRP_NS, 'my_group')
    assert ret_members == {b'a'}
except RejectedByBackend as e:
    print(f'SDL operation failed: {str(e)}')
    #Permanent failure, just forward the exception
    raise
except (NotConnected, BackendError) as e:
    print(f'SDL operation failed for a temporal error: {str(e)}')
    #Here we could have a retry logic


# Checks if 'a' is a member of the group 'my_group' under given namespace.
try:
    was_member = mysdl.is_member(MY_GRP_NS, 'my_group', b'a')
    assert was_member == True
    was_member = mysdl.is_member(MY_GRP_NS, 'my_group', b'not a member')
    assert was_member == False
except RejectedByBackend as e:
    print(f'SDL operation failed: {str(e)}')
    #Permanent failure, just forward the exception
    raise
except (NotConnected, BackendError) as e:
    print(f'SDL operation failed for a temporal error: {str(e)}')
    #Here we could have a retry logic


# Returns the count of members of a group 'my_group' under given namespace.
try:
    ret_count = mysdl.group_size(MY_GRP_NS, 'my_group')
    assert ret_count == 1
except RejectedByBackend as e:
    print(f'SDL operation failed: {str(e)}')
    #Permanent failure, just forward the exception
    raise
except (NotConnected, BackendError) as e:
    print(f'SDL operation failed for a temporal error: {str(e)}')
    #Here we could have a retry logic


# Removes the member 'a' of the group 'my_group' under given namespace.
try:
    mysdl.remove_member(MY_GRP_NS, 'my_group', {b'a', b'not a member'})
    assert mysdl.group_size(MY_GRP_NS, 'my_group') == 0
except RejectedByBackend as e:
    print(f'SDL operation failed: {str(e)}')
    #Permanent failure, just forward the exception
    raise
except (NotConnected, BackendError) as e:
    print(f'SDL operation failed for a temporal error: {str(e)}')
    #Here we could have a retry logic


# Removes the group 'my_group' under given namespace.
try:
    mysdl.add_member(MY_GRP_NS, 'my_group', {b'a', b'b', b'c'})
    assert mysdl.group_size(MY_GRP_NS, 'my_group') == 3
    mysdl.remove_group(MY_GRP_NS, 'my_group')
    assert mysdl.get_members(MY_GRP_NS, 'my_group') == set()
    assert mysdl.group_size(MY_GRP_NS, 'my_group') == 0
except RejectedByBackend as e:
    print(f'SDL operation failed: {str(e)}')
    #Permanent failure, just forward the exception
    raise
except (NotConnected, BackendError) as e:
    print(f'SDL operation failed for a temporal error: {str(e)}')
    #Here we could have a retry logic


# Gets a lock 'my_lock' resource under given namespace.
# Note that this function does not take a lock, you need to call 'acquire' function to take
# the lock to yourself.
try:
    my_lock = mysdl.get_lock_resource(MY_LOCK_NS, "my_lock", expiration=5.5)
    assert my_lock != None
except RejectedByBackend as e:
    print(f'SDL operation failed: {str(e)}')
    #Permanent failure, just forward the exception
    raise
except (NotConnected, BackendError) as e:
    print(f'SDL operation failed for a temporal error: {str(e)}')
    #Here we could have a retry logic


# Acquires a lock from the lock resource. Return True if lock was taken within given retry limits.
try:
    was_acquired = my_lock.acquire(retry_interval=0.5, retry_timeout=2)
    assert was_acquired == True
    was_acquired = my_lock.acquire(retry_interval=0.1, retry_timeout=0.2)
    assert was_acquired == False
except RejectedByBackend as e:
    print(f'SDL operation failed: {str(e)}')
    #Permanent failure, just forward the exception
    raise
except (NotConnected, BackendError) as e:
    print(f'SDL operation failed for a temporal error: {str(e)}')
    #Here we could have a retry logic


# Refreshs the remaining validity time of the existing lock back to an initial value.
try:
    my_lock.refresh()
except RejectedByBackend as e:
    print(f'SDL operation failed: {str(e)}')
    #Permanent failure, just forward the exception
    raise
except (NotConnected, BackendError) as e:
    print(f'SDL operation failed for a temporal error: {str(e)}')
    #Here we could have a retry logic


# Gets the remaining validity time of the lock.
try:
    ret_time = my_lock.get_validity_time()
    assert ret_time != 0
except RejectedByBackend as e:
    print(f'SDL operation failed: {str(e)}')
    #Permanent failure, just forward the exception
    raise
except (NotConnected, BackendError) as e:
    print(f'SDL operation failed for a temporal error: {str(e)}')
    #Here we could have a retry logic


# Releases the lock.
try:
    my_lock.release()
except RejectedByBackend as e:
    print(f'SDL operation failed: {str(e)}')
    #Permanent failure, just forward the exception
    raise
except (NotConnected, BackendError) as e:
    print(f'SDL operation failed for a temporal error: {str(e)}')
    #Here we could have a retry logic


# Locking example what utilizes python 'with' statement with SDL lock.
# The lock is released automatically when we are out of the scope of
# 'the with my_lock' statement.
try:
    my_lock = mysdl.get_lock_resource(MY_LOCK_NS, "my_lock", 2.5)
    with my_lock:
        #Just an example how to use lock API
        time_left = my_lock.get_validity_time()

        #Add here operations what needs to be done under a lock, for example some
        #operations with a shared resources what needs to be done in a mutually
        #exclusive way.

    #Lock is not anymore hold here

except RejectedByBackend as e:
    print(f'SDL operation failed: {str(e)}')
    #Permanent failure, just forward the exception
    raise
except (NotConnected, BackendError) as e:
    print(f'SDL operation failed for a temporal error: {str(e)}')
    #Here we could have a retry logic


# Closes the SDL connection.
mysdl.close()

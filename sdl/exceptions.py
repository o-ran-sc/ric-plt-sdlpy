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

"Exceptions raised by the shareddatalayer."

class SdlTypeError(TypeError):
    """Exception for passing a function argument of wrong type.
       It is likely that the same request will fail repeatedly. It is advised to investigate the
       exact reason for the failure from the logs."""
    pass

class SdlException(Exception):
    """Base exception class for shareddatalayer exceptions."""
    pass

class NotConnected(SdlException):
    """Exception for not being connected to the database backend.
       Shareddatalayer is not connected to the backend data storage and therefore could not deliver
       the request to the backend data storage. Data in the backend data storage has not been
       altered. Client is advised to try the operation again later."""
    pass

class BackendError(SdlException):
    """Exception for request processing failure.
       In case of a write type request, data in the backend data storage may or may not have been
       altered. Client is advised to try the operation again later."""
    pass

class RejectedBySdl(SdlException):
    """Exception for shareddatalayer rejecting the request.
       Either shareddatalayer or backend data storage rejected the request. In case of a write type
       request, data in the backend data storage may or may not have been altered. It is likely that
       the same request will fail repeatedly. It is advised to investigate the exact reason for the
       failure from the logs."""
    pass

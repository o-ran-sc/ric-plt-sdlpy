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
    """Exception for passing a function argument of wrong type."""
    pass

class SdlException(Exception):
    """Base exception class for shareddatalayer exceptions."""
    pass

class BackendError(SdlException):
    """Exception for request processing failure in the database backend."""
    pass

class InvalidNamespace(SdlException):
    """Exception for passing invalid namespace string."""
    pass

class NotConnected(SdlException):
    """Exception for not being connected to the database backend."""
    pass

class OperationInterrupted(SdlException):
    """Exception for not receiving response from the database backend."""
    pass

class RejectedByBackend(SdlException):
    """Exception for database backend rejecting the request."""
    pass

class RejectedBySdl(SdlException):
    """Exception for shareddatalayer rejecting the request."""
    pass

class LockAcquireFailed(SdlException):
    """Exception for shareddatalayer locking failure."""
    pass

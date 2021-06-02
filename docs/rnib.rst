..
..  Copyright (c) 2021 Samsung Electronics.
..
..  Licensed under the Creative Commons Attribution 4.0 International
..  Public License (the "License"); you may not use this file except
..  in compliance with the License. You may obtain a copy of the License at
..
..    https://creativecommons.org/licenses/by/4.0/
..
..  Unless required by applicable law or agreed to in writing, documentation
..  distributed under the License is distributed on an "AS IS" BASIS,
..  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
..
..  See the License for the specific language governing permissions and
..  limitations under the License.
..

RNIB(Radio network information base)
====================================

The .proto files that defines the message format is located in the rnib repo.
The rnib repo is set to submodule.

**Prerequisite**

* protoc (v3.6.1)

**Compile .proto files**

.. code-block:: console

    $ pwd
    ~/ric-plt-sdlpy
    $ git pull --recurse-submodules
    $ PYTHON_OUT="ricsdl-package/ricsdl/entities"
    $ RNIB_PROTO="nodeb-rnib/entities"
    $ protoc --python_out="${PYTHON_OUT}" \
             --proto_path="${RNIB_PROTO}" \
             $(find "${RNIB_PROTO}" -iname "*.proto" -printf "%f ")
    $ sed -i -E 's/^import.*_pb2/from . \0/' ${PYTHON_OUT}/*_pb2.py

**The reason why sed is needed**

*use relative imports in generated modules* : `protobuf issue
<https://github.com/protocolbuffers/protobuf/issues/1491>`_

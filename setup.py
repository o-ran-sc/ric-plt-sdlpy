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


from setuptools import setup, find_packages

setup(
    name="sdlpy",
    version="0.0.1",
    packages=find_packages(exclude=["tests.*", "tests"]),
    author="Timo Tietavainen",
    author_email='timo.tietavainen@nokia.com',
    license='Apache 2.0',
    description="Shared Data Layer provides a high-speed interface for accessing shared data storage",
    url="https://gerrit.o-ran-sc.org/r/admin/repos/ric-plt/sdlpy",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Telecommunications Industry",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires=">=3.7",
    keywords="RIC SDL",
    data_files=[("", ["LICENSES.txt"])],
    install_requires=[
        'setuptools',
        'redis>=3.3.11'
    ],
)

..
..  Copyright (c) 2019 AT&T Intellectual Property.
..  Copyright (c) 2019 Nokia.
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


Release Notes
=============


This document provides the release notes of the ricsdl library.

.. contents::
   :depth: 3
   :local:




Version history
---------------

[2.0.3] - 2020-01-22

* Add a new SDL storage API function `is_active()` to check healthiness of SDL instance.

[2.0.2] - 2020-01-14

* Version bump.

[2.0.1] - 2020-01-13

* Add a fake database backend implementation to be used only for testing
  purposes when the real DBAAS database service is not available.

[2.0.0] - 2020-01-03

* Change find_keys() and find_and_get() API functions to support glob-style
  regular expression in a key search pattern. API backward incompatible change.
* Remove 'atomic' parameter of find_and_get() API function. API backward
  incompatible change.

[1.0.2] - 2019-12-18

* Take Hiredis package into use in Redis database backend.
* Add unit tests for configuration handling.

[1.0.1] - 2019-12-06

* Version bump.

[1.0.0] - 2019-12-05

* First version.




Summary
-------

This is the first version of this package.
It implements RIC Shared Data Layer (SDL) library.




Release Data
------------
This is the first version of this package.





Feature Additions
^^^^^^^^^^^^^^^^^


Bug Corrections
^^^^^^^^^^^^^^^


Deliverables
^^^^^^^^^^^^

Software Deliverables
+++++++++++++++++++++

This version provides Python package ricsdl.
It can be retrieved from pypi.org.



Documentation Deliverables
++++++++++++++++++++++++++





Known Limitations, Issues and Workarounds
-----------------------------------------

System Limitations
^^^^^^^^^^^^^^^^^^



Known Issues
^^^^^^^^^^^^

Workarounds
^^^^^^^^^^^





References
----------



RIC SDL
=======

Shared Data Layer in the RAN Intelligent Controller

Shared Data Layer (SDL) provides a lightweight, high-speed interface for
accessing shared data storage. The purpose is to enable utilizing clients to
become stateless, conforming with, e.g., the requirements of the fifth
generation mobile networks.


Concepts
--------

Namespace

Namespaces provide data isolation within SDL data storage. That is, data in
certain namespace is isolated from the data in other namespaces. Each SDL
client uses one or more namespaces. Namespaces can be used, for example, to
isolate data belonging to different use cases.

Keys and Data

Clients save key-data pairs. Data is passed as a `bytes` type. SDL stores the
data as it is. Any structure that this data may have (e.g. a data structure
serialized by `pickle`) is meaningful only to the client itself. Clients are
responsible for managing the keys. As namespaces provide data isolation,
keys in different namespaces always access different data.

Backend Data Storage

Backend data storage refers to data storage technology behind SDL API, which
handles the actual data storing. SDL API hides the backend data storage
implementation from SDL API clients, and therefore backend data storage
technology can be changed without affecting SDL API clients. Currently, Redis
database is used as a backend data storage solution.

Notifications

Notifications functionality provide SDL clients the possibility to receive
notifications about data changes in SDL namespaces. SDL client receiving
notifications about data changes is referred to as "subscriber", while the SDL
client modifying data and publishing notifications is referred to as
"publisher".

Install
-------

Install from PyPi

```
python3 -m pip install ricsdl
```

Install using the source

```
python3 setup.py install
```


Usage
-----

Instructions how to use SDL can be found from O-RAN Software Community (SC)
Documentation under Near Realtime RAN Intelligent Controller (RIC) section:
[O-RAN SC Documentation Home](https://docs.o-ran-sc.org/projects/o-ran-sc-ric-plt-sdl/en/latest/)


Unit Testing
------------

To run the unit tests run the following command in the package directory:
`
python3 -m pytest
`


Examples
--------

See the ``examples`` directory.



CI
--

The ci is done with the `tox` tool. See `tox.ini` file for details.

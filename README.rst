reqpi
=====

The build-friendly PyPI fake.

Introduction
------------
reqpi is a server that can pretend to be a PyPI clone,
but is optimized to be friendy to be a build system.
It creates ad-hoc end-points which serve an extremely
limited subset of PyPI.

Usage
-----

.. code::

   $ twistd reqpi --http $PORT
   $ url=`python -m reqpi gethash --url http://localhost:2000/ requirements.txt`
   $ pip install --index-url $url requirements.txt

This will make sure that if :code:`requirements.txt` is incomplete,
the build will fail, rather than getting the latest version of the dependency
that is missing.

The URL should also work with other things that access PyPI, like PEX
or Pants. For appropriate ways to get those systems to access the ad-hoc
URL, refer to the package documentation.

Contributing
------------

If you would like to contribute code to this project you can do so through GitHub by
forking the repository and sending a pull request.

When submitting code, please make every effort to follow existing conventions
and style in order to keep the code as readable as possible. Please also make
sure your code is correct by running :code:`tox`.

Before your code can be accepted into the project you must also sign the
`Individual Contributor License Agreement (CLA)`_

.. _Individual Contributor License Agreement (CLA): https://spreadsheets.google.com/spreadsheet/viewform?formkey=dDViT2xzUHAwRkI3X3k5Z0lQM091OGc6MQ&ndplr=1

Credits
-------

Thanks to our employer, Square, for sponsoring the time for us to write this.

License
-------

Copyright 2015 Square Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

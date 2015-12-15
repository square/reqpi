Running
=======

Server
------

The server is a twisted_ plugin. After installing :code:`reqpi`,
:code:`twistd reqpi` should just work. Refer to :code:`twistd`
documentation for details on how to use it.

.. code::

    $ twistd reqpi [--http PORT] [--url URL]

The port is the port that :code:`reqpi` will listen on.
While it will try to make a good guess as to what is the
URL through which it should be accesses, enough layers
of reverse proxies, with interesting enough configuration,
can confuse it. In that case, :code:`--baseurl` should be passed
to tell it where it is accessed from.

Client
------

.. code::

    $ PYPI=$(python -m reqpi gethash --url URL REQUIREMENTS_FILE)

This command will initialize PYPI with a URL that points to a
PyPI-compatible server, but only allowing the packages in the requirements
file. For example, this can be used with pip as follows:

Note that the requirements file only supports the :code:`PACKAGE==VERSION`
syntax. This is intentional: this is the only syntax which is properly
hermetic (it is also what :code:`pip freeze` will output).

.. code::

    $ pip install --index-url $PYPI Twisted[tls]

.. _twisted: https://twistedmatrix.com/

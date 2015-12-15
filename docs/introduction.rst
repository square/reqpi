Introduction
============

Usually, Python projects are installed with :code:`pip install -r requirements.txt`,
with a frozen :code:`requirements.txt` file. However, alternative build systems
(such as Pants_, Pex_ or hand-coded Dockerfiles_) sometimes specify "floaters":
packages that allow more than one version number (for example, "any greater than
1.2"). In addition, if :code:`requirements.txt` is missing a requirement, most
of these tools will recover gracefully by getting the highest compatible version.

While these are features sometimes, they undercut the concept of a "deterministic build"
or "hermetic build": a build whose output depend only on the inputs, and not on the
state of the world, such as what packages have been uploaded to PyPI.

ReqPI is a PyPI-compatible server which will generate ad-hoc end-points where "pre-commitment"
is made to which packages will be requested. It will reject requests for any other packages,
and will only offer the versions specified in a :code:`requirements.txt` file. All Python
package-fetching systems allow specifying an alternate URL for package source. 

.. _Pants: https://pantsbuild.github.io/
.. _Pex: https://pex.readthedocs.org/en/stable/
.. _Dockerfiles: http://docs.docker.com/engine/reference/builder/

Contribute
==========

Overall guidance on contributing to a PyAnsys repository appears in the
`Contributing <dev_guide_contributing_>`_ topic
in the *PyAnsys Developer's Guide*. Ensure that you are thoroughly familiar
with this guide before attempting to contribute to PyTurboGrid.

The following contribution information is specific to PyTurboGrid.

Clone the repository
--------------------

To clone the PyTurboGrid repository and install the latest PyTurboGrid release
in development mode, run these commands:

.. code::

    git clone https://github.com/ansys/pyturbogrid
    cd pyturbogrid
    python -m pip install --upgrade pip
    pip install -e .

Post issues
-----------

Use the `PyTurboGrid Issues <https://github.com/ansys/pyturbogrid/issues>`_ page
to submit questions, report bugs, and request new features. When possible, use
these issue templates:

* Bug, problem, error: For filing a bug report
* Documentation error: For requesting modifications to the documentation
* Adding an example: For proposing a new example
* New feature: For requesting enhancements to the code

If your issue does not fit into one of these template categories, you can click
the link for opening a blank issue.

To reach the project support team, email `pyansys.core@ansys.com <pyansys.core@ansys.com>`_.

View documentation
------------------

Documentation for the latest stable release of PyTurboGrid is hosted at
`PyTurboGrid documentation <https://turbogrid.docs.pyansys.com>`_.

In the upper right corner of the documentation's title bar, there is an option
for switching from viewing the documentation for the latest stable release
to viewing the documentation for the development version or previously
released versions.

Adhere to code style
--------------------

PyTurboGrid follows the PEP8 standard as outlined in
`PEP 8 <https://dev.docs.pyansys.com/coding-style/pep8.html>`_ in
the *PyAnsys Developer's Guide* and implements style checking using
`pre-commit <precommit_>`_.

To ensure your code meets minimum code styling standards, run these
commands::

  pip install pre-commit
  pre-commit run --all-files

You can also install this as a pre-commit hook by running this command::

  pre-commit install

This way, it is not possible for you to push code that fails the style checks::

  $ pre-commit install
  $ git commit -am "added my cool feature"
  isort....................................................................Passed
  black....................................................................Passed
  blacken-docs.............................................................Passed
  flake8...................................................................Passed
  codespell................................................................Passed
  check for merge conflicts................................................Passed
  debug statements (python)................................................Passed
  Validate GitHub Workflows................................................Passed

.. _dev_guide_contributing: https://dev.docs.pyansys.com/how-to/contributing.html
.. _precommit: https://pre-commit.com/

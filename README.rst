PyTurboGrid
================
|pyansys| |python| |pypi| |GH-CI| |codecov| |MIT| |black|

.. |pyansys| image:: https://img.shields.io/badge/Py-Ansys-ffc107.svg?logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAIAAACQkWg2AAABDklEQVQ4jWNgoDfg5mD8vE7q/3bpVyskbW0sMRUwofHD7Dh5OBkZGBgW7/3W2tZpa2tLQEOyOzeEsfumlK2tbVpaGj4N6jIs1lpsDAwMJ278sveMY2BgCA0NFRISwqkhyQ1q/Nyd3zg4OBgYGNjZ2ePi4rB5loGBhZnhxTLJ/9ulv26Q4uVk1NXV/f///////69du4Zdg78lx//t0v+3S88rFISInD59GqIH2esIJ8G9O2/XVwhjzpw5EAam1xkkBJn/bJX+v1365hxxuCAfH9+3b9/+////48cPuNehNsS7cDEzMTAwMMzb+Q2u4dOnT2vWrMHu9ZtzxP9vl/69RVpCkBlZ3N7enoDXBwEAAA+YYitOilMVAAAAAElFTkSuQmCC
   :target: https://docs.pyansys.com/
   :alt: PyAnsys

.. |python| image:: https://img.shields.io/pypi/pyversions/pyturbogrid?logo=pypi
   :target: https://pypi.org/project/pyturbogrid/
   :alt: Python

.. |pypi| image:: https://img.shields.io/pypi/v/pyturbogrid.svg?logo=python&logoColor=white
   :target: https://pypi.org/project/pyturbogrid
   :alt: PyPI

.. |codecov| image:: https://codecov.io/gh/pyansys/pyturbogrid/branch/main/graph/badge.svg
   :target: https://codecov.io/gh/pyansys/pyturbogrid
   :alt: Codecov

.. |GH-CI| image:: https://github.com/pyansys/pyturbogrid/actions/workflows/ci.yml/badge.svg
   :target: https://github.com/pyansys/pyturbogrid/actions/workflows/ci.yml
   :alt: GH-CI

.. |MIT| image:: https://img.shields.io/badge/License-MIT-yellow.svg
   :target: https://opensource.org/licenses/MIT
   :alt: MIT

.. |black| image:: https://img.shields.io/badge/code%20style-black-000000.svg?style=flat
   :target: https://github.com/psf/black
   :alt: Black

.. |intro| image:: https://github.com/pyansys/pyturbogrid/raw/main/doc/source/_static/turbine_blade_squealer_tip_conformal_white_rounded.png
   :alt: TurboGrid
   :width: 600 

A Python wrapper for `Ansys TurboGrid`_ software to generate high quality turbomachinery meshes.

|intro| 

.. inclusion-marker-do-not-remove

How to install
--------------

The name of the package from this repository available on `PyPI`_ is ``ansys-turbogrid-core``. It has been tested for use with python 3.10 on Windows and Linux.

In order to install PyTurboGrid, make sure you have the latest version of `pip`_. To do so, run:

.. code:: bash

    python -m pip install -U pip

Then, you can simply execute:

.. code:: bash

    python -m pip install ansys-turbogrid-core


Installing PyTurboGrid from source code allows you to modify the source and enhance it. Before contributing to the project, please refer to the `PyAnsys Developer's guide`_. You will need to follow these steps:

1. Start by cloning this repository:

   .. code:: bash

      git clone https://github.com/ansys/pyturbogrid.git
      
It is recommended to use a python virtual environment for the steps below and for PyTurbogrid development in general. Please refer to PyAnsys documentation on `virtual environment`_ for the steps to create and activate one. 

Assuming a suitable python environment is active, and the current working directory is the top level directory of the pyturbogrid repository cloned locally, following steps will install the package from the local repository.
      
2. Make sure you have the latest required build system and doc, testing, and CI tools:

   .. code:: bash

      python -m pip install -r requirements/requirements_build.txt
      python -m pip install -r requirements/requirements_doc.txt
      python -m pip install -r requirements/requirements_tests.txt

3. Install the project in editable mode:

   .. code:: bash
    
      python -m pip install -e . 

Requirements
------------

You must have a licensed copy of Ansys TurboGrid software installed locally. PyTurboGrid supports Ansys TurboGrid release 2023 R2. The Windows installation of Ansys automatically sets the required environment variables for PyTurboGrid to find the locall TurboGrid installation. Using Ansys TurboGrid 2023 R2 installed in the default directory for example, the installer automatically sets an environment variable ``AWP_ROOT232`` to point to ``C:\Program Files\ANSYS Inc\v232``.

On Linux, the required environment variable is not set automatically. Using Ansys 2023 R2 in the default installation directory as an example, this can be set for the current user in the current shell session before running PyTurboGrid, with:

.. code:: console

    export AWP_ROOT232=/usr/ansys_inc/v232

For this setting to persist between different shell sessions for the current user, the same export command can instead be added to the user's ``~/.profile`` file.


.. LINKS AND REFERENCES
.. _Ansys TurboGrid: https://www.ansys.com/products/fluids/ansys-turbogrid
.. _black: https://github.com/psf/black
.. _flake8: https://flake8.pycqa.org/en/latest/
.. _isort: https://github.com/PyCQA/isort
.. _pip: https://pypi.org/project/pip/
.. _pre-commit: https://pre-commit.com/
.. _PyAnsys Developer's guide: https://dev.docs.pyansys.com/
.. _pytest: https://docs.pytest.org/en/stable/
.. _PyPI: https://pypi.org/
.. _Sphinx: https://www.sphinx-doc.org/en/master/
.. _tox: https://tox.wiki/
.. _virtual environment: https://dev.docs.pyansys.com/how-to/setting-up.html#virtual-environments

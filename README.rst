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

A Python wrapper for the `Ansys TurboGrid`_ software to generate high-quality turbomachinery meshes.

|intro| 

.. inclusion-marker-do-not-remove

How to install
--------------

To use PyTurboGrid, the ``ansys-turbogrid-core`` package must be installed from `PyPI`_. This 
package is supported with Python 3.10 on Windows and Linux.

1. In order to install PyTurboGrid, ensure you have the latest version of `pip`_. To update pip, run:

.. code:: bash

    python -m pip install -U pip

2. Then, you can simply execute:

.. code:: bash

    python -m pip install ansys-turbogrid-core


Installing PyTurboGrid from source code allows you to modify the source and enhance it. Before 
contributing to the project, please refer to the `PyAnsys Developer's guide`_. You will need to 
follow these additional steps:

3. Clone the ``pyturbogrid`` repository:

.. code:: bash

   git clone https://github.com/ansys/pyturbogrid.git
      
It is recommended to use a Python virtual environment for the steps below, and whenever you
run PyTurbogrid from the source code. Please refer to the PyAnsys documentation on 
`virtual environment`_ for the steps to create and activate a virtual environment. 

Assuming that a suitable Python environment is active, pip has been updated, and the current 
working directory is the top-level directory of the pyturbogrid repository cloned locally, 
the following step will install the package from the local repository.
      
4. Install the project in editable mode:

.. code:: bash
   
   python -m pip install -e . 

Requirements
------------

You must have a licensed local installaton of Ansys TurboGrid. PyTurboGrid supports Ansys 
TurboGrid Release 2023 R2. The Windows installation of Ansys automatically sets the required 
environment variable for PyTurboGrid to find the local TurboGrid installation. For example, if
Ansys Release 2023 R2 is installed in the default directory, the installer automatically 
sets an environment variable ``AWP_ROOT232`` to point to ``C:\Program Files\ANSYS Inc\v232``.

On Linux, the required environment variable is not set automatically and you must set this 
manually. For example, if Ansys Release 2023 R2 is installed in the default directory, the
``AWP_ROOT232`` environment variable must be set to ``/usr/ansys_inc/v232``.

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

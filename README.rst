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

.. |codecov| image:: https://codecov.io/gh/ansys/pyturbogrid/branch/main/graph/badge.svg
   :target: https://codecov.io/gh/ansys/pyturbogrid
   :alt: Codecov

.. |GH-CI| image:: https://github.com/ansys/pyturbogrid/actions/workflows/ci.yml/badge.svg
   :target: https://github.com/ansys/pyturbogrid/actions/workflows/ci.yml
   :alt: GH-CI

.. |MIT| image:: https://img.shields.io/badge/License-MIT-yellow.svg
   :target: https://opensource.org/licenses/MIT
   :alt: MIT

.. |black| image:: https://img.shields.io/badge/code%20style-black-000000.svg?style=flat
   :target: https://github.com/psf/black
   :alt: Black

.. |intro| image:: https://github.com/ansys/pyturbogrid/raw/main/doc/source/_static/turbine_blade_squealer_tip_conformal_white_rounded.png
   :alt: TurboGrid
   :width: 600 

PyTurboGrid is a Python wrapper for `Ansys TurboGrid`_, a high-quality turbomachinery
meshing software app. To run PyTurboGrid, you must have access to a licensed local copy
of TurboGrid. PyTurboGrid supports Ansys TurboGrid 2023 R2 and later.


|intro| 

.. inclusion-marker-do-not-remove

Installation
------------
The ``ansys-turbogrid-core`` package supports Python 3.10 on Windows and Linux. Two modes
of installation are available:

- User installation
- Developer installation

User installation
~~~~~~~~~~~~~~~~~
To use PyTurboGrid, you must install the ``ansys-turbogrid-core`` package from `PyPI`_. 

#. To ensure that you have the latest version of `pip`_, run this command:

   .. code:: bash

       python -m pip install -U pip

#. To install PyTurboGrid, run this command:

   .. code:: bash

       python -m pip install ansys-turbogrid-core


Developer installation
~~~~~~~~~~~~~~~~~~~~~~
A developer installation consists of cloning the ``pyturbogrid`` repository
and installing the project in editable mode. When you install PyTurboGrid from
source code, you can modify and enhance the code.

Overall guidance on contributing to a PyAnsys library appears in the
`Contributing < https://dev.docs.pyansys.com/how-to/contributing.html>`_ topic
in the *PyAnsys Developer's Guide*. Ensure that you are thoroughly familiar
with this `guide <https://dev.docs.pyansys.com/>_` before attempting to
contribute to PyTurboGrid.

#. Clone the ``pyturbogrid`` repository:

   .. code:: bash

       git clone https://github.com/ansys/pyturbogrid.git
      

#. To avoid incompatibilites in requirements when working in multiple
   Python projects, create and activate a virtual environment. For
   more information, see `Virtual environments`_ in the *PyAnsys
   Developer's Guide*.

#. To ensure that you have the latest version of `pip`_, run this command:

   .. code:: bash

       python -m pip install -U pip

#. Assuming that your current working directory is the top-level directory
   of your locally cloned ``pyturbogrid`` repository, install PyTurboGrid
   from this local repository in editable mode by running this command:
      
   .. code:: bash
   
       python -m pip install -e . 

Requirements
------------
You must have a licensed local installation of Ansys TurboGrid 2023 R2 or later.

The ``AWP_ROOTxxx`` environment variable, where ``xxx`` is the three-digit
Ansys version, allows PyTurboGrid to find your local TurboGrid installation.

A Windows installation automatically sets this root environment variable.
For example, if you install Ansys 2023 R2 in the default directory,
the installer sets the ``AWP_ROOT232`` environment variable to
``C:\Program Files\ANSYS Inc\v232``.

A Linux installation does not automatically set this root environment
variable. For example, if you install Ansys 2023 R2 in the default
directory, you must manually set the ``AWP_ROOT232`` environment
variable to ``/usr/ansys_inc/v232``.

License and acknowledgments
---------------------------

PyTurboGrid is licensed under the MIT license.

PyTurboGrid makes no commercial claim over Ansys whatsoever. This library extends the
functionality of Ansys TurboGrid by adding a Python interface to TurboGrid without
changing the core behavior or license of the original software. The use of the
interactive control of PyTurboGrid requires a legally licensed local copy of TurboGrid.

For more information on TurboGrid, see the `Ansys TurboGrid`_ page on the Ansys website.

.. LINKS AND REFERENCES
.. _Ansys TurboGrid: https://www.ansys.com/products/fluids/ansys-turbogrid
.. _black: https://github.com/psf/black
.. _flake8: https://flake8.pycqa.org/en/latest/
.. _isort: https://github.com/PyCQA/isort
.. _pip: https://pypi.org/project/pip/
.. _pre-commit: https://pre-commit.com/
.. _PyAnsys Developer's Guide: https://dev.docs.pyansys.com/
.. _pytest: https://docs.pytest.org/en/stable/
.. _PyPI: https://pypi.org/
.. _Sphinx: https://www.sphinx-doc.org/en/master/
.. _tox: https://tox.wiki/
.. _Virtual environments: https://dev.docs.pyansys.com/how-to/setting-up.html#virtual-environments

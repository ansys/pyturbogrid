PyTurboGrid documentation |version|
===================================

Introduction
------------
Ansys TurboGrid is a high-quality turbomachinery meshing software app. It features 
novel automated mesh generation capabilities in a simple-to-use, streamlined
workspace. You can apply the tools in TurboGrid to a wide variety of turbomachinery
equipment to help produce accurate simulation results.

What is PyTurboGrid?
--------------------
PyTurboGrid is part of the larger `PyAnsys <https://docs.pyansys.com>`_
effort to facilitate the use of Ansys technologies directly from Python.
PyTurboGrid implements a client-server architecture. Communication between
PyTurboGrid (client) and the running TurboGrid process (server) is based on
the plain TCP/IP technology. However, you need to interact only with the
Python interface.

You can use PyTurboGrid to programmatically launch an instance of TurboGrid,
load a model, read in a session file, generate a mesh, and query statistics
for this mesh.

PyTurboGrid lets you use TurboGrid within a Python environment of your choice
in conjunction with other PyAnsys libraries and external Python libraries.


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   getting_started/index
   api_reference/index
   examples/index
   contributing

Project index
=============

* :ref:`genindex`

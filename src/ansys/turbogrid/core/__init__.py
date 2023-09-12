# Copyright (c) 2023 ANSYS, Inc. All rights reserved
"""PyTurboGrid is a Python wrapper for Ansys TurboGrid."""

from ansys.turbogrid.core.launcher.launcher import launch_turbogrid

try:
    import importlib.metadata as importlib_metadata
except ModuleNotFoundError:  # pragma: no cover
    import importlib_metadata

# Read from the pyproject.toml
# major, minor, patch
__version__ = importlib_metadata.version("ansys-turbogrid-core")

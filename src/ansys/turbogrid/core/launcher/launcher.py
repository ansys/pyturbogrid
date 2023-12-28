# Copyright (c) 2023 ANSYS, Inc. All rights reserved
"""Module for launching a local instance of Ansys TurboGrid."""

from enum import Enum
import os
from pathlib import Path
import platform
from typing import Optional

from ansys.turbogrid.api import pyturbogrid_core


def _is_windows():
    """Check if Windows is the current operating system."""
    return platform.system() == "Windows"


class TurboGridVersion(Enum):
    """Provide an enumeration over supported TurboGrid versions."""

    # Versions must be listed here with the most recent first
    version_24R1 = "24.1.0"
    version_23R2 = "23.2.0"

    @classmethod
    def _missing_(cls, version):
        if isinstance(version, (float, str)):
            version = str(version) + ".0"
            for v in TurboGridVersion:
                if version == v.value:
                    return TurboGridVersion(version)
            else:
                raise RuntimeError(
                    f"The passed version '{version[:-2]}' does not exist. "
                    f"Available version strings are: "
                    f"{[ver.value for ver in TurboGridVersion]} "
                )

    def __str__(self):
        return str(self.value)


def get_latest_ansys_version() -> str:
    """Get the latest installed Ansys version from ``AWP_ROOTxxx`` environment variables.

    .. note::
       The ``xxx`` is the three-digit Ansys version. For example, the ``AWP_ROOT232``
       environment variable specifies the path to the directory where Ansys 2023 R2
       is installed. If Ansys 2023 R2 is installed in the default directory on Windows,
       the value for this environment variable is ``C:\\Program Files\\ANSYS Inc\\v232``.

    Returns
    -------
    str
        Latest installed Ansys version in this format: ``"23.2.0"``.
    """

    for v in TurboGridVersion:
        if "AWP_ROOT" + "".join(str(v).split("."))[:-1] in os.environ:
            return str(v)

    raise RuntimeError("No Ansys version can be found.")


def get_turbogrid_exe_path(**launch_argvals) -> Path:
    """Get the path to a local installation of TurboGrid.

    The path is obtained by searching in this order:

    1. The path specified by the ``turbogrid_path`` parameter from ``launch_argvals``.
    2. The path specified by the ``PYTURBOGRID_TURBOGRID_ROOT`` environment variable.
    3. The path of the TurboGrid installation specified by the ``product_version`` parameter
       from ``launch_argvals``, using the corresponding ``AWP_ROOTxxx`` environment variable.
    4. The path of the TurboGrid installation from the ``AWP_ROOTxxx`` environment variable for
       the latest installed Ansys version.


    Returns
    -------
    Path
        Path of a local TurboGrid installation.
    """

    def get_turbogrid_root(version: TurboGridVersion) -> Path:
        awp_root = os.environ["AWP_ROOT" + "".join(str(version).split("."))[:-1]]
        return Path(awp_root) / "TurboGrid"

    def get_exe_path(turbogrid_root: Path) -> Path:
        if _is_windows():
            return (
                turbogrid_root / "bin" / "cfxtg.exe"
            )  # pragma no cover (operating system dependent)
        else:
            return turbogrid_root / "bin" / "cfxtg"  # pragma no cover (operating system dependent)

    # Look for TurboGrid exe path in the following order:
    # 1. turbogrid_path parameter passed with launch_turbogrid
    turbogrid_path = launch_argvals.get("turbogrid_path")
    if turbogrid_path:
        return Path(turbogrid_path)

    # 2. "PYTURBOGRID_TURBOGRID_ROOT" environment variable
    turbogrid_root = os.getenv("PYTURBOGRID_TURBOGRID_ROOT")
    if turbogrid_root:
        return get_exe_path(Path(turbogrid_root))

    # 3. product_version parameter passed with launch_turbogrid
    product_version = launch_argvals.get("product_version")
    if product_version:
        return get_exe_path(get_turbogrid_root(TurboGridVersion(product_version)))

    # 4. the latest Ansys version from AWP_ROOT environment variables
    ansys_version = get_latest_ansys_version()
    return get_exe_path(get_turbogrid_root(TurboGridVersion(ansys_version)))


def launch_turbogrid(
    product_version: str = None,
    turbogrid_path: str = None,
    log_level: pyturbogrid_core.PyTurboGrid.TurboGridLogLevel = pyturbogrid_core.PyTurboGrid.TurboGridLogLevel.INFO,
    additional_args_str: str = None,
    additional_kw_args: dict = None,
    port: Optional[int] = None,
    host: str = "127.0.0.1",
    log_filename_suffix: str = "",
    **kwargs,
) -> pyturbogrid_core.PyTurboGrid:
    """Launch TurboGrid locally in server mode.

    Parameters
    ----------
    product_version : str, default: ``None``
        Version of TurboGrid to use in the numeric format. For example, ``"23.2.0"``
        for 2023 R2. The default is ``None``, in which case the latest installed
        version is used.
    turbogrid_path : str, default: ``None``
        Path to the ``cfxtg`` command for starting TurboGrid. The default is ``None``,
        in which case the value for the ``product_version`` parameter is used.
    log_level : pyturbogrid_core.PyTurboGrid.TurboGridLogLevel, default: ``INFO``
        Level of logging information written to the terminal. The default is ``INFO``.
        Options are ``INFO``, ``WARNING``, ``ERROR``, ``CRITICAL``, and ``DEBUG``.
        This setting also affects the level of output that is written to the log files.
    additional_args_str : str, default: ``None``
        Additional arguments to send to TurboGrid.
    additional_kw_args : dict, default: ``None``
        Additional arguments to send to TurboGrid.
    port : int, default: ``None``
        Port for TurboGrid communications. The default is ``None``, in which case
        an available port is automatically selected.
    host : str, default: ``127.0.0.1 (this is the local host IP for windows and linux)``
        host for TurboGrid communications. The default is ``127.0.0.1, or the local Host``
    log_filename_suffix : str, default: ""
        suffix for name of the log files written out.

    Returns
    -------
    pyturbogrid_core.PyTurboGrid
        TurboGrid session.
    """
    if kwargs:
        raise TypeError(
            f"launch_turbogrid() got an unexpected keyword argument {next(iter(kwargs))}"
        )

    argVals = locals()
    pathToCFXTG = get_turbogrid_exe_path(**argVals)

    return pyturbogrid_core.PyTurboGrid(
        socket_port=port,
        turbogrid_location_type=pyturbogrid_core.PyTurboGrid.TurboGridLocationType.TURBOGRID_INSTALL,
        cfxtg_location=pathToCFXTG,
        additional_args_str=additional_args_str,
        additional_kw_args=additional_kw_args,
        log_level=log_level,
        host_ip=host,
        log_filename_suffix=log_filename_suffix
    )


def launch_turbogrid_ansys_labs(
    product_version: str = "latest",
    log_level: pyturbogrid_core.PyTurboGrid.TurboGridLogLevel = pyturbogrid_core.PyTurboGrid.TurboGridLogLevel.INFO,
) -> pyturbogrid_core.PyTurboGrid:
    """Launch TurboGrid from within the Ansys Labs environment.

    Parameters
    ----------
    product_version : str, default: ``latest``
        Version of TurboGrid to launch in the Ansys Labs environment. Only certain versions are supported.
    log_level : pyturbogrid_core.PyTurboGrid.TurboGridLogLevel, default: ``INFO``
        Level of logging information written to the terminal. The default is ``INFO``.
        Options are ``INFO``, ``WARNING``, ``ERROR``, ``CRITICAL``, and ``DEBUG``.
        This setting also affects the level of output that is written to the log files.

    Returns
    -------
    pyturbogrid_core.PyTurboGrid
        TurboGrid session.
    """
    return pyturbogrid_core.PyTurboGrid(
        socket_port=0,
        turbogrid_location_type=pyturbogrid_core.PyTurboGrid.TurboGridLocationType.TURBOGRID_ANSYS_LABS,
        cfxtg_location="",
        additional_args_str=None,
        additional_kw_args=None,
        log_level=log_level,
        host_ip="",
        pim_app_name="turbogrid",
        pim_app_ver=product_version,
    )

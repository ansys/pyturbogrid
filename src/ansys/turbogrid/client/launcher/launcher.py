"""Provides a module for launching Ansys TurboGrid.

This module supports starting Ansys TurboGrid locally.
"""
from enum import Enum
import os
from pathlib import Path
import platform

from ansys.turbogrid.api import pyturbogrid_core


def _is_windows():
    """Check if the current operating system is windows."""
    return platform.system() == "Windows"


class TurboGridVersion(Enum):
    """Contains the standard Ansys TurboGrid release."""

    # Versions must be listed here with the most recent first
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
                    f"The passed version '{version[:-2]}' does not exist."
                    f" Available version strings are: "
                    f"{[ver.value for ver in TurboGridVersion]} "
                )

    def __str__(self):
        return str(self.value)


def get_latest_ansys_version() -> str:
    """Get the latest Ansys version from AWP_ROOT environment variables."""

    for v in TurboGridVersion:
        if "AWP_ROOT" + "".join(str(v).split("."))[:-1] in os.environ:
            return str(v)

    raise RuntimeError("No Ansys version can be found.")


def get_turbogrid_exe_path(**launch_argvals) -> Path:
    def get_turbogrid_root(version: TurboGridVersion) -> Path:
        awp_root = os.environ["AWP_ROOT" + "".join(str(version).split("."))[:-1]]
        return Path(awp_root) / "TurboGrid"

    def get_exe_path(turbogrid_root: Path) -> Path:
        if _is_windows():
            return turbogrid_root / "bin" / "cfxtg.exe"
        else:
            return turbogrid_root / "bin" / "cfxtg"

    # Look for TurboGrid exe path in the following order:
    # 1. turbogrid_path parameter passed with launch_turbogrid
    turbogrid_path = launch_argvals.get("turbogrid_path")
    if turbogrid_path:
        return turbogrid_path

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
    additional_args_str: str = None,
    additional_kw_args: dict = None,
    port: int | None = None,
    **kwargs,
) -> pyturbogrid_core.PyTurboGrid:
    """Launch TurboGrid locally in server mode.

    Parameters
    ----------
    product_version : str, optional
        Version of TurboGrid to use in the numeric format (such as ``"23.2.0"``
        for 2023 R2). The default is ``None``, in which case the active version
        or latest installed version is used.
    turbogrid_path : str, optional
        Path to the "cfxtg" command used to start TurboGrid. The default is ``None``.
        in which case the product_version is used instead.
    port : int, optional
        Port to use for TurboGrid communications. The default is ``5000``.
    additional_args_str : str, optional
        Additional arguments to send to TurboGrid. The default is ``None``.
    additional_kw_args : dict, optional
        Additional arguments to send to TurboGrid. The default is ``None``.

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
        port,
        pyturbogrid_core.PyTurboGrid.TurboGridLocationType.TURBOGRID_INSTALL,
        pathToCFXTG,
        additional_args_str,
        additional_kw_args,
    )

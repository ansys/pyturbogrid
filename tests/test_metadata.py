from ansys.turbogrid.client import __version__


def test_pkg_version():
    assert __version__ == "0.0.2"

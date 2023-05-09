# import ansys.api.turbogrid as pytg


class LocalMeshStatistics:
    """
    Class for local mesh statistics analysis based on the current mesh in a running session of TurboGrid.
    """

    def __init__(self, domain: str = "ALL"):
        """
        Initialize the class using a connection to a running session of TurboGrid.

        Parameters
        ----------
        domain : str, optional
            Domain name to get the initial statistics for. If not specified, statistics for all
            domains are read.
        """
        # self.interface = pytg.pyturbogrid_core.PyTurboGrid
        self.mesh_vars = dict()
        self.current_domain = str()
        self._read_mesh_statistics(domain)

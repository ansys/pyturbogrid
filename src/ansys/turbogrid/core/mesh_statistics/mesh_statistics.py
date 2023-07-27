# Copyright (c) 2023 ANSYS, Inc. All rights reserved
"""Module for facilitating analysis of mesh statistics."""
import ansys.turbogrid.api as pytg


class MeshStatistics:
    """
    Facilitates analysis of mesh statistics for the current mesh in a running session of
    TurboGrid.
    """

    #: Interface to a running session of TurboGrid.
    interface: pytg.pyturbogrid_core.PyTurboGrid = 0

    #: Cache of the basic mesh statistics obtained by the last call to the
    #: :func: `update_mesh_statistics` method or from the initialization of
    #: the object if this method has not been called. The name of the domain
    #: these statistics relate to is stored as the :attr:`current_domain`
    #: attribute.
    mesh_vars: dict = dict()

    #: Domain that was used for the last update of the mesh statistics. See the :attr:`mesh_vars`
    #: attribute.
    current_domain: str = ""

    def __init__(self, turbogrid_instance: pytg.pyturbogrid_core.PyTurboGrid, domain: str = "ALL"):
        """
        Initialize the class using a connection to a running session of TurboGrid.

        Parameters
        ----------
        turbogrid_instance : pytg.pyturbogrid_core.PyTurboGrid
            Running session of TurboGrid.
        domain : str, default: "ALL"
            Name of the domain to get the initial statistics from. The default is ``"All"``,
            in which case statistics are read for all domains.
        """
        self.interface = turbogrid_instance
        self.mesh_vars = dict()
        self.current_domain = str()
        self._read_mesh_statistics(domain)

    def _read_mesh_statistics(self, domain: str = "ALL") -> None:
        self.mesh_vars.clear()
        if "query_mesh_statistics" not in dir(self.interface):
            raise self.interface.InvalidQuery(
                "query_mesh_statistics"
            )  # pragma no cover (won't occur with current TurboGrid data)
        self.mesh_vars = self.interface.query_mesh_statistics(domain)
        self.current_domain = domain

    def get_mesh_statistics(self, variable: str = "ALL") -> dict:
        """Get the basic mesh statistics from the cached mesh statistics.

        Parameters
        ----------
        variable : str, default: "ALL"
            Mesh statistics variable to get statistics for. The default is
            ``"ALL"``, in which case a dictionary of all variables is returned.

        Returns
        -------
        dict
            Dictionary of all variables if the default value of ``"ALL"``
            is used for the ``variable`` parameter or a dictionary of the
            current mesh statistics values if a single variable is specified.
        """
        if variable == "ALL":
            return self.mesh_vars
        else:
            return self.mesh_vars[variable]

    def update_mesh_statistics(self, domain: str = "ALL") -> None:
        """Re-read the mesh statistics from TurboGrid.

        This method can be used either to update the cached mesh statistics after TurboGrid
        has remeshed or update the cached mesh statistics to use a different domain or domains.

        Parameters
        ----------
        domain : str, default: ``ALL``
            Name of the domain to get the statistics from. The default is ``"ALL"``, in which
            case statistics are read for all domains.
        """
        self._read_mesh_statistics(domain)

    def get_domain_label(self, domain: str) -> str:
        """Get suitable label text for a domain.
        
        Parameters
        ----------
        domain : str
            Name of the domain to generate the label frorm.

        Returns
        -------
        str
            ``"All Domains"`` is returned if ``"ALL"`` is the value
            value specifed for the ``domain`` parameter or ``"Domain: <name>"``
            is returned if a name of a single domain is specified.
        
        """
        if domain == "ALL":
            domain_label = "All Domains"
        else:
            domain_label = "Domain: " + domain
        return domain_label

    def _draw_histogram(
        self,
        variable: str,
        bin_limits: list,
        bin_values: list,
        xlabel: str,
        ylabel: str,
        domain_label: str,
        image_file: str,
        show: bool,
    ) -> None:
        import matplotlib.pyplot as plt

        fig, axs = plt.subplots(1, 1, num="PyTurboGrid Mesh Statistics")
        axs.stairs(bin_values, bin_limits, fill=True)
        axs.set_title(variable + "\n" + domain_label)
        axs.set_xlabel(xlabel)
        axs.set_ylabel(ylabel)
        plt.grid(linestyle="--")
        if image_file:
            plt.savefig(image_file)
        if show:
            plt.show()  # pragma no cover (can't open a separate window in unit_tests)
        else:
            plt.close(fig)

    def create_histogram(
        self,
        variable: str,
        domain: str = "ALL",
        use_percentages: bool = True,
        bin_units: str = "",
        image_file: str = "",
        show: bool = True,
    ) -> None:
        """Create a histogram of mesh statistics using `Matplotlib <https://matplotlib.org/>`_.

        Parameters
        ----------
        variable : str
            Mesh statistics variable to use for the histogram.
        domain : str, default: "ALL"
            Domain name to get statistics for. The default is ``"ALL"``, in which
            case statistics for all domains are read. Cached mesh statistics are
            not used or affected.
        use_percentages : bool, default: False
            Whether to display the percentage values of the bin counts for
            the histogram. The default is ``False``, in which case the actual bin
            counts are shown.
        bin_units : str, default: ""
            Units for the mesh statistics values (x-axis labels). The default is
            ``""``, in which case the provided units are used.
        image_file : str, default: ""
            File format to write the histogram image to. The default is ``""``, in
            which case the format is determined by the file extension (such as ``.png``).
            Available formats are those provided by Matplotlib, including ``".png"``,
            ``".pdf"``, and ``".svg"``.
        show : bool, default: True
            Whether to display the image on the screen. If ``False``, the image is not
            displayed on the screen, which is only useful if the image is
            being written to a file.
        """
        if "query_mesh_statistics_histogram_data" not in dir(self.interface):
            raise self.interface.InvalidQuery(
                "query_mesh_statistics_histogram_data"
            )  # pragma no cover (won't occur with current TurboGrid data)

        histogram_stats = self.interface.query_mesh_statistics_histogram_data(
            domain=domain, variable=variable, bin_units=bin_units
        )

        if use_percentages:
            bin_values = histogram_stats["Bin Percentages"]
            ylabel = "Percentage"
        else:
            bin_values = histogram_stats["Bin Totals"]
            ylabel = "Count"

        if histogram_stats["Bin Limits Units"]:
            xlabel = variable + r" [" + histogram_stats["Bin Limits Units"] + r"]"
        else:
            xlabel = variable  # pragma no cover (won't occur with current TurboGrid data)

        self._draw_histogram(
            variable=variable,
            bin_limits=histogram_stats["Bin Limits"],
            bin_values=bin_values,
            xlabel=xlabel,
            ylabel=ylabel,
            domain_label=self.get_domain_label(domain),
            image_file=image_file,
            show=show,
        )

    def get_table_rows(self) -> list:
        """
        Get the mesh statistics table data from the cached mesh statistics.

        Returns
        -------
        list
            List of row data. Each list item represents one table row. The list
            item contains a list of the cell contents for each cell in the row.
        """
        row_data = list()
        row_data.append(["Mesh Measure", "Value", "% Bad", "% ok", "%OK"])
        for var_name, var_data in self.mesh_vars.items():
            # Exclude variables which only have 'Count' set (e.g. 'Elements')
            if "Maximum" in var_data:
                data = list()
                data.append(var_name)
                if var_data["Limits Type"] == "Maximum":
                    value = str(var_data["Maximum"])
                elif var_data["Limits Type"] == "Minimum":
                    value = str(var_data["Minimum"])
                else:
                    value = ""  # pragma no cover (won't occur with current TurboGrid data)
                if value and var_data["Units"]:
                    value += " [" + var_data["Units"] + "]"
                data.append(value)
                data.append(str(var_data["Percent Bad"]))
                data.append(str(var_data["Percent ok"]))
                data.append(str(var_data["Percent OK"]))
                row_data.append(data)
        return row_data

    def write_table_to_csv(self, file_name: str) -> None:
        """
        Write the mesh statistics table to a CSV file.
        
        The values in the mesh statistics table are obtained from the cached
        mesh statistics.

        Parameters
        ----------
        file_name : str
            File name to write the mesh statistics table to.
        """
        import csv

        with open(file_name, "w", newline="") as f:
            writer = csv.writer(f)
            row_data = self.get_table_rows()
            writer.writerow([self.get_domain_label(self.current_domain)])
            for row in row_data:
                writer.writerow(row)

    def get_table_as_text(self) -> str:
        """Get a text version of the mesh statistics table from the cached mesh statistics."""
        table = "\n" + self.get_domain_label(self.current_domain) + "\n\n"
        row_data = self.get_table_rows()
        row_lengths = [9] * 5
        for row in row_data:
            for index, value in enumerate(row):
                row_lengths[index] = max(row_lengths[index], len(value))
        for row in row_data:
            row_string = ""
            for index, value in enumerate(row):
                row_string += str(value).ljust(row_lengths[index]) + " "
            table += row_string
            table += "\n"
        return table

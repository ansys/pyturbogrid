# Copyright (c) 2023 ANSYS, Inc. All rights reserved
"""Provides the ``MeshStatistics`` class."""
import ansys.turbogrid.api as pytg


class MeshStatistics:
    """
    Class to facilitate analysis of mesh statistics for the current mesh in a running session of
    TurboGrid.
    """

    #: Interface to a running session of TurboGrid.
    interface: pytg.pyturbogrid_core.PyTurboGrid = 0

    #: Cache of the basic mesh statistics obtained by the last call to update_mesh_statistics or
    #: from the initialization of the object if update_mesh_statistics has not been called. The
    #: name of the domain to which these statistics relate is stored as the current_domain
    #: attribute.
    mesh_vars: dict = dict()

    #: The domain that was used for the last update of the mesh statistics. See the documentation
    #: for the mesh_vars attribute.
    current_domain: str = ""

    def __init__(self, turbogrid_instance: pytg.pyturbogrid_core.PyTurboGrid, domain: str = "ALL"):
        """
        Initialize the class using a connection to a running session of TurboGrid.

        Parameters
        ----------
        turbogrid_instance : pytg.pyturbogrid_core.PyTurboGrid
            Running session of TurboGrid.
        domain : str, optional
            Name of the domain from which to get the initial statistics. If not specified, statistics
            are read for all domains.
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
        variable : str, optional
            Mesh statistics variable to get statistics for. If not specified, a dictionary of all
            variables is returned.

        Returns
        -------
        dict
            A dictionary of the current mesh statistics values for a single variable, or a dictionary
            of all variable dictionaries if no variable is specified.
        """
        if variable == "ALL":
            return self.mesh_vars
        else:
            return self.mesh_vars[variable]

    def update_mesh_statistics(self, domain: str = "ALL") -> None:
        """Re-read the mesh statistics from TurboGrid.

        This can be used either to update the cached mesh statistics after TurboGrid has remeshed,
        or to update the cached mesh statistics to use a different domain or domains.

        Parameters
        ----------
        domain : str, optional
            Name of the domain from which to get the statistics. If not specified, statistics are
            read for all domains.
        """
        self._read_mesh_statistics(domain)

    def get_domain_label(self, domain: str) -> str:
        """Get suitable label text for the specified domain name. This returns either
        "Domain: <name>" or "All Domains" (if "ALL" is specified as the input parameter).


        Parameters
        ----------
        domain : str
            The domain name from which to generate the label.

        Returns
        -------
        str
            The domain label.
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
        """Create a histogram of mesh statistics using the matplotlib library.

        Parameters
        ----------
        variable : str
            Mesh statistics variable to use for the histogram.
        domain : str, optional
            Domain name to get statistics for. If not specified, statistics for all domains are
            read. Note: The cached mesh statistics are not used or affected.
        use_percentages : bool, optional
            If not specified or set to true, display the percentage values of the bin counts for
            the histogram. If false, display the actual bin counts.
        bin_units : str, optional
            Use the provided units for the mesh statistics values (x-axis labels).
        image_file : str, optional
            If set, write the histogram image to the specified file. The image format is
            determined by the file extension e.g. ".png". The available formats are those
            provided by matplotlib, including ".png", ".pdf", and ".svg".
        show : bool, optional
            If set to false, do not display the image on screen. Only useful if the image is
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
        Get the mesh statistics table data as a list of row data, from the cached mesh
        statistics.

        Returns
        -------
        list
            Each list item represents one table row, and contains a list of the cell
            contents for each cell in the row.
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
        Write a csv file containing a table of the mesh statistics values, from the cached mesh
        statistics.

        Parameters
        ----------
        file_name : str
            File name for writing the statistics table.
        """
        import csv

        with open(file_name, "w", newline="") as f:
            writer = csv.writer(f)
            row_data = self.get_table_rows()
            writer.writerow([self.get_domain_label(self.current_domain)])
            for row in row_data:
                writer.writerow(row)

    def get_table_as_text(self) -> str:
        """Get a text version of the mesh statistics table, from the cached mesh statistics."""
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

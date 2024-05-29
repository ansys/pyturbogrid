from fabric import Connection
import socket
import time


@staticmethod
def get_open_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # using '0' will tell the OS to pick a random port that is available.
        s.bind(("", 0))
        s.listen(1)
        port = s.getsockname()[1]
        # Shutdown is not needed because the socket is not connected.
        # Also, this will throw and error in windows
        # s.shutdown(socket.SHUT_RDWR)
        s.close()
    # Wait a second to let the OS do things
    time.sleep(1)
    return port


class container_helpers:
    pytestconfig: None

    def __init__(self, pytcfg):
        self.pytestconfig = pytcfg

    @staticmethod
    def get_container_connection(ftp_port: int, ssh_key_filename: str, host_name="localhost"):
        container_connection = Connection(
            host=host_name,
            user="root",
            port=ftp_port,
            connect_kwargs={"key_filename": ssh_key_filename},
        )
        return container_connection

    @staticmethod
    def transfer_file_to_container(container_connection: Connection, local_filepath: str):
        print(f"To container-> {local_filepath}")
        container_connection.put(
            remote="/",
            local=local_filepath,
        )

    @staticmethod
    def transfer_files_to_container(
        container_connection: Connection, local_folder_path: str, local_filenames: list
    ):
        for filename in local_filenames:
            container_helpers.transfer_file_to_container(
                container_connection, f"{local_folder_path}/{filename}"
            )

    @staticmethod
    def transfer_file_from_container(
        container_connection: Connection, remote_filename: str, local_path_only: str
    ):
        print(f"From container-> {local_path_only}/{remote_filename}")
        container_connection.get(
            remote=f"/{remote_filename}",
            local=f"{local_path_only}/{remote_filename}",
        )

    @staticmethod
    def transfer_files_from_container(
        container_connection: Connection, local_folder_path: str, remote_filenames: list
    ):
        for filename in remote_filenames:
            container_helpers.transfer_file_from_container(
                container_connection, filename, local_folder_path
            )

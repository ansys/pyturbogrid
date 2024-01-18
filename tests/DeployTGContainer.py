import platform
import subprocess
import time


class deployed_tg_container:
    image_name: str
    socket_port: int
    ftp_port: int
    cfxtg_command: str
    license_server: str
    container_name: str
    is_linux: bool
    prepend_command: str
    keep_stopped_container: bool

    def __init__(
        self,
        image_name: str,
        socket_port: int,
        ftp_port: int,
        cfxtg_command: str,
        license_server: str,
        container_name: str = "TG_CONTAINER",
        keep_stopped_container=False,
        additional_env_vars={},
    ):
        self.image_name = image_name
        self.socket_port = socket_port
        self.ftp_port = ftp_port
        self.cfxtg_command = cfxtg_command
        self.license_server = license_server
        self.container_name = container_name
        self.keep_stopped_container = keep_stopped_container
        self.is_linux = platform.system() == "Linux"
        additional_env_string: str = ""
        for key, val in additional_env_vars.items():
            additional_env_string += f" -e {key}={val} "
        print("\n")
        print(f"######### Launching Container #########")
        print(f"       tg_container_name = {self.container_name}")
        print(f"       tg_image_name = {self.image_name}")
        print(f"       socketPort = {self.socket_port}")
        print(f"       ftpPort = {self.ftp_port}")
        print(f"       cfxtg_command = {self.cfxtg_command}")
        print(f"       license_server = {self.license_server}")
        print(f"       platform = {platform.system()}")
        print(f"       is_linux = {self.is_linux}")
        print(f"       additional_env_vars = {additional_env_vars}")
        print(f"       additional_env_string = {additional_env_string}")
        print("\n")

        # subprocess.run(
        #     "env"
        #     if self.is_linux
        #     else '"C:/Program Files/PowerShell/7/pwsh.exe" -Command gci env:',
        #     shell=True,
        # )
        self.prepend_command = (
            "sudo" if self.is_linux else '"C:/Program Files/PowerShell/7/pwsh.exe" -Command'
        )
        logical_and = "&&" if self.is_linux else "^&^&"
        print("######### Spin up docker image #########")
        print(f"Remove any existing containers: {self.container_name}")
        subprocess.run(
            f"{self.prepend_command} docker container rm -fv {self.container_name}", shell=True
        )
        docker_command = (
            f"{self.prepend_command} docker run --name {self.container_name} "
            f"-e ANSYSLMD_LICENSE_FILE={self.license_server} {additional_env_string}"
            f"-p {self.socket_port}:{self.socket_port} "
            f"-p {self.ftp_port}:{self.ftp_port} "
            f"-d {self.image_name} /bin/bash -c '/usr/local/bin/start_sshd.sh {self.ftp_port} {logical_and} {self.cfxtg_command}'"
        )
        print(f"docker_command: {docker_command}")
        print(f"start tg...")
        subprocess.run(f"{docker_command}", shell=True)
        print(f"sleep...")
        # Wait 2 seconds for the container to actually be responsive
        time.sleep(2)
        print(f"TG container ready")

    def __del__(self):
        print("\n######### Dispose of container #########")
        subprocess.run(
            f"{self.prepend_command} docker container stop {self.container_name}", shell=True
        )
        if self.keep_stopped_container == False:
            subprocess.run(
                f"{self.prepend_command} docker container rm -fv {self.container_name}", shell=True
            )
        print("######### All done #########")


class remote_tg_instance:
    socket_port: int
    cfxtg_command: str
    # license_server: str
    is_linux: bool
    tg_proc: subprocess.Popen

    def __init__(
        self,
        socket_port: int,
        cfxtg_command_noargs: str,
        # license_server: str,
    ):
        self.socket_port = socket_port
        self.cfxtg_command = f'"{cfxtg_command_noargs}" -py -control-port {self.socket_port}'
        # self.license_server = license_server
        self.is_linux = platform.system() == "Linux"
        print("\n")
        print(f"######### Launching Remote Instance #########")
        print(f"       socketPort = {self.socket_port}")
        print(f"       cfxtg_command = {self.cfxtg_command}")
        # print(f"       license_server = {self.license_server}")
        print(f"       platform = {platform.system()}")
        print(f"       is_linux = {self.is_linux}")
        print("\n")
        subprocess.run(
            "env"
            if self.is_linux
            else '"C:/Program Files/PowerShell/7/pwsh.exe" -Command gci env:',
            shell=True,
        )
        print("######### Spin up remote process #########")
        self.tg_proc = subprocess.Popen(
            f"{self.cfxtg_command}",
            shell=True,
        )
        print(f"pid: {self.tg_proc.pid}")
        print(f"sleep...")
        # Wait 2 seconds for the container to actually be responsive
        time.sleep(2)
        print(f"TG instance ready")

    def __del__(self):
        print("\n######### Dispose of process #########")
        self.tg_proc.kill()
        print("######### All done #########")

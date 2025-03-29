import datetime
import os
import socket
import subprocess
import traceback

from colorama import Fore, Style

import check
import storage
from config import ConfigManager

running_locally = False


def print_error(message):
    """Prints an error message in red."""
    print(f"{Fore.RED}{message}{Style.RESET_ALL}")


def main():
    global running_locally

    banner = f"""{Fore.RED}
    ██████╗  ██████╗     ███╗   ██╗ ██████╗ ████████╗                           
    ██╔══██╗██╔═══██╗    ████╗  ██║██╔═══██╗╚══██╔══╝                           
    ██║  ██║██║   ██║    ██╔██╗ ██║██║   ██║   ██║                              
    ██║  ██║██║   ██║    ██║╚██╗██║██║   ██║   ██║                              
    ██████╔╝╚██████╔╝    ██║ ╚████║╚██████╔╝   ██║                              
    ╚═════╝  ╚═════╝     ╚═╝  ╚═══╝ ╚═════╝    ╚═╝                              

     ██████╗██╗      ██████╗ ███████╗███████╗    ████████╗██╗  ██╗██╗███████╗██╗
    ██╔════╝██║     ██╔═══██╗██╔════╝██╔════╝    ╚══██╔══╝██║  ██║██║██╔════╝██║
    ██║     ██║     ██║   ██║███████╗█████╗         ██║   ███████║██║███████╗██║
    ██║     ██║     ██║   ██║╚════██║██╔══╝         ██║   ██╔══██║██║╚════██║╚═╝
    ╚██████╗███████╗╚██████╔╝███████║███████╗       ██║   ██║  ██║██║███████║██╗
     ╚═════╝╚══════╝ ╚═════╝ ╚══════╝╚══════╝       ╚═╝   ╚═╝  ╚═╝╚═╝╚══════╝╚═╝
    {Style.RESET_ALL}"""

    zip_file_main = "server.zip"
    server_folder = os.path.join("server")

    config_manager = ConfigManager("config.ini")
    config_manager.initialize_credentials()
    if not config_manager.check_option_exists("Settings", "allocated_ram"):
        config_manager.set_value("Settings", "allocated_ram", "2")
    missing = config_manager.check_missing_credentials()
    if len(missing) > 0:
        print_error("Missing credentials.")
        return

    print(banner)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    if os.path.exists(server_folder):
        storage.zip_server_folder(f"backup_{timestamp}.zip", server_folder)

    secret = check.get_secret_text()
    if secret != "ver2":
        print_error("Imi e lene sa fac update automat.")
        return

    current_status = check.get_running_status()
    if current_status:
        print_error("Server is already running.")
        host = check.get_host_name()
        print_error(f"Host name: {host}")
        return

    drive = storage.authenticate_drive()
    storage.download_and_setup_server(drive, storage.MAIN_FOLDER_ID)

    check.update_running_status(True)
    running_locally = True
    check.update_host_name(socket.gethostname())

    print(banner)
    print("Starting server...")

    allocated_ram = config_manager.get_value("Settings", "allocated_ram")
    allocated_ram_mb = int(allocated_ram) * 1024  # Convert GB to MB
    server_command = [
        os.path.join("", "jdk-21.0.5+11", "bin", "java.exe"),
        f"-Xmx{allocated_ram_mb}M",
        f"-Xms{allocated_ram_mb}M",
        "-jar",
        os.path.join("server.jar"),
        "nogui",
    ]
    subprocess.run(
        server_command, cwd=server_folder, creationflags=subprocess.CREATE_NEW_CONSOLE
    )

    print("Server stopped. Uploading file...")
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    storage.zip_server_folder(f"backup_{timestamp}.zip", server_folder)

    drive = storage.authenticate_drive()

    storage.delete_old_server_zip(drive, storage.MAIN_FOLDER_ID)

    storage.zip_server_folder(zip_file_main, server_folder)

    storage.upload_to_personal_drive(
        drive, zip_file_main, "server.zip", storage.MAIN_FOLDER_ID
    )
    storage.upload_to_personal_drive(
        drive,
        zip_file_main,
        f"server_{timestamp}_{socket.gethostname()}.zip",
        storage.BACKUP_FOLDER_ID,
    )

    check.update_running_status(False)
    running_locally = False


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print_error(f"An error occurred: {e}")
        print(traceback.format_exc())
        if running_locally:
            check.update_running_status(False)
            running_locally = False

    input(f"{Fore.GREEN}Press Enter to exit...{Style.RESET_ALL}")

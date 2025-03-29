import json
import os
import shutil
import tempfile
import zipfile

from pydrive2.auth import GoogleAuth, ServiceAccountCredentials
from pydrive2.drive import GoogleDrive

from config import ConfigManager

config_manager = ConfigManager("config.ini")

MAIN_FOLDER_ID = config_manager.get_value("Credentials", "main_folder_id")
BACKUP_FOLDER_ID = config_manager.get_value("Credentials", "backup_folder_id")

private_key = config_manager.get_value("Credentials", "private_key").replace(
    "\\n", "\n"
)

SERVICE_ACCOUNT_JSON = {
    "type": config_manager.get_value("Credentials", "type"),
    "project_id": config_manager.get_value("Credentials", "project_id"),
    "private_key_id": config_manager.get_value("Credentials", "private_key_id"),
    "private_key": private_key,
    "client_email": config_manager.get_value("Credentials", "client_email"),
    "client_id": config_manager.get_value("Credentials", "client_id"),
    "auth_uri": config_manager.get_value("Credentials", "auth_uri"),
    "token_uri": config_manager.get_value("Credentials", "token_uri"),
    "auth_provider_x509_cert_url": config_manager.get_value(
        "Credentials", "auth_provider_x509_cert_url"
    ),
    "client_x509_cert_url": config_manager.get_value(
        "Credentials", "client_x509_cert_url"
    ),
    "universe_domain": config_manager.get_value("Credentials", "universe_domain"),
}


def authenticate_drive():
    print("Authenticating Google Drive...")

    gauth = GoogleAuth()
    gauth.credentials = ServiceAccountCredentials.from_json_keyfile_dict(
        SERVICE_ACCOUNT_JSON, ["https://www.googleapis.com/auth/drive"]
    )

    print("Google Drive authenticated.")

    return GoogleDrive(gauth)


def delete_old_server_zip(drive, folder_id, filename="server.zip"):
    file_list = drive.ListFile(
        {"q": f"'{folder_id}' in parents and title = '{filename}' and trashed = false"}
    ).GetList()

    for file in file_list:
        print(f"Deleting old {filename} from Drive...")
        file.Delete()
        print(f"{filename} deleted successfully.")


def upload_to_personal_drive(drive, file_path, title, folder_id):
    print(f"Uploading {title} to Google Drive...")

    file = drive.CreateFile({"title": title, "parents": [{"id": folder_id}]})
    file.SetContentFile(file_path)
    file.Upload()

    print(f'File uploaded successfully to folder {folder_id}: {file["title"]}')


def zip_server_folder(output_zip, server_folder):
    print("Zipping server folder...")

    if os.path.exists(output_zip):
        os.remove(output_zip)
        print(f"Old {output_zip} deleted locally.")

    with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(server_folder):
            for file in files:
                if file == "server.jar":
                    continue  # Skip server.jar
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, server_folder)
                zipf.write(file_path, arcname)

    print(f"Server folder zipped as {output_zip}")

    return output_zip


def download_and_setup_server(drive, folder_id):
    temp_dir = tempfile.mkdtemp()
    print(f"Using temporary directory: {temp_dir}")

    files_to_download = {
        "server.zip": "server.zip",
        "server.jar": "server.jar",
        "jdk-21.0.5+11.zip": "jdk-21.0.5+11.zip",
    }

    server_folder = "server"
    jdk_folder = "jdk-21.0.5+11"
    temp_server_jar = os.path.join(temp_dir, "server.jar")

    # Check if JDK exists, skip download if it does
    if os.path.exists(jdk_folder):
        print(f"{jdk_folder} already exists. Skipping JDK download.")
        del files_to_download["jdk-21.0.5+11.zip"]

    # Check if server.jar exists in server folder, skip download and copy it instead
    if os.path.exists(os.path.join(server_folder, "server.jar")):
        print(f"{server_folder}/server.jar already exists. Skipping download.")
        shutil.copy(os.path.join(server_folder, "server.jar"), temp_server_jar)
        del files_to_download["server.jar"]

    # Download files that need to be downloaded
    for file_title, local_filename in files_to_download.items():
        print(f"Searching for {file_title} in Drive...")
        file_list = drive.ListFile(
            {
                "q": f"'{folder_id}' in parents and title = '{file_title}' and trashed = false"
            }
        ).GetList()

        if not file_list:
            print(f"Error: {file_title} not found in Google Drive.")
            continue

        print(f"Downloading {file_title}...")
        file = file_list[0]
        file.GetContentFile(os.path.join(temp_dir, local_filename))
        print(f"{file_title} downloaded successfully to {temp_dir}")

    # Unzip server.zip
    if "server.zip" in files_to_download:
        if os.path.exists(server_folder):
            print(f"Removing existing {server_folder} directory...")
            shutil.rmtree(server_folder)

        print(f"Extracting server.zip...")
        with zipfile.ZipFile(os.path.join(temp_dir, "server.zip"), "r") as zip_ref:
            zip_ref.extractall(server_folder)
        print(f"server.zip extracted to {server_folder}")

    # Move or copy server.jar to the server folder
    if os.path.exists(temp_server_jar):
        shutil.move(temp_server_jar, os.path.join(server_folder, "server.jar"))
        print(f"server.jar moved to {server_folder}/server.jar")

    # Unzip JDK if it was downloaded
    if "jdk-21.0.5+11.zip" in files_to_download:
        print(f"Extracting jdk-21.0.5+11.zip...")
        with zipfile.ZipFile(
            os.path.join(temp_dir, "jdk-21.0.5+11.zip"), "r"
        ) as zip_ref:
            zip_ref.extractall(jdk_folder)
        print(f"jdk-21.0.5+11.zip extracted to {jdk_folder}")

    # Cleanup temp directory
    shutil.rmtree(temp_dir)
    print("Temporary directory cleaned up.")


def upload_server_zip(drive, folder_id):
    print("Uploading server.zip to Google Drive...")

    file = drive.CreateFile({"title": "server.zip", "parents": [{"id": folder_id}]})
    file.SetContentFile("server.zip")
    file.Upload()

    print("server.zip uploaded successfully.")


if __name__ == "__main__":
    drive = authenticate_drive()
    upload_server_zip(drive, MAIN_FOLDER_ID)

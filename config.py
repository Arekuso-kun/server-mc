import configparser
import os


class ConfigManager:
    def __init__(self, file_path):
        """Initializes the ConfigManager with a given config file path."""
        self.file_path = file_path
        self.config = configparser.ConfigParser(interpolation=None)
        self._create_config()

    def _create_config(self):
        """Creates a new config file if it does not exist."""
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w") as configfile:
                self.config.write(configfile)

    def add_section(self, section):
        """Adds a new section to the config file."""
        self.config.read(self.file_path)
        if not self.config.has_section(section):
            self.config.add_section(section)
            self._save_config()

    def set_value(self, section, key, value):
        """Sets a key-value pair in a given section with an optional comment."""
        self.config.read(self.file_path)
        if not self.config.has_section(section):
            self.config.add_section(section)

        self.config.set(section, key, value)
        self._save_config()

    def get_value(self, section, key):
        """Gets the value of a key in a given section."""
        self.config.read(self.file_path)
        if self.config.has_section(section) and self.config.has_option(section, key):
            return self.config.get(section, key)
        return None

    def remove_option(self, section, key):
        """Removes a specific key from a section."""
        self.config.read(self.file_path)
        if self.config.has_section(section) and self.config.has_option(section, key):
            self.config.remove_option(section, key)
            self._save_config()

    def remove_section(self, section):
        """Removes an entire section from the config file."""
        self.config.read(self.file_path)
        if self.config.has_section(section):
            self.config.remove_section(section)
            self._save_config()

    def initialize_credentials(self):
        """Adds placeholder keys with no values."""
        section = "Credentials"
        self.config.read(self.file_path)
        if not self.config.has_section(section):
            self.config.add_section(section)

        credentials = [
            "USER",
            "PASSWORD",
            "HOST",
            "PORT",
            "DBNAME",
            "MAIN_FOLDER_ID",
            "BACKUP_FOLDER_ID",
            "TYPE",
            "PROJECT_ID",
            "PRIVATE_KEY_ID",
            "PRIVATE_KEY",
            "CLIENT_EMAIL",
            "CLIENT_ID",
            "AUTH_URI",
            "TOKEN_URI",
            "AUTH_PROVIDER_X509_CERT_URL",
            "CLIENT_X509_CERT_URL",
            "UNIVERSE_DOMAIN",
        ]

        for key in credentials:
            if not self.config.has_option(section, key):
                self.config.set(section, key, "")

        self._save_config()

    def check_missing_credentials(self):
        """Checks if any credential values are missing."""
        self.config.read(self.file_path)
        missing_keys = []
        if self.config.has_section("Credentials"):
            for key in self.config.options("Credentials"):
                if not self.config.get("Credentials", key).strip():
                    missing_keys.append(key)
        return missing_keys

    def check_option_exists(self, section, key):
        """Checks if a specific key exists in a given section."""
        self.config.read(self.file_path)
        return self.config.has_section(section) and self.config.has_option(section, key)

    def _save_config(self):
        """Writes the current state of the config to the file."""
        with open(self.file_path, "w") as configfile:
            self.config.write(configfile)

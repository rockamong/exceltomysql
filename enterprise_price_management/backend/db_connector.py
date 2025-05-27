import mysql.connector
import json
import os
import shutil

# Define the paths for configuration files
CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')
DEFAULT_CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.json.default')

def get_db_config():
    """
    Reads the database configuration from config.json.
    If config.json does not exist, it copies config.json.default to config.json.
    Returns a dictionary with database configuration values.
    """
    if not os.path.exists(CONFIG_PATH):
        try:
            shutil.copy(DEFAULT_CONFIG_PATH, CONFIG_PATH)
        except IOError as e:
            print(f"Error copying default config file: {e}")
            # Fallback to default values if copy fails
            return {
                "DB_HOST": "localhost",
                "DB_PORT": 3306,
                "DB_USER": "root",
                "DB_PASSWORD": "",
                "DB_NAME": "EntPrice"
            }

    try:
        with open(CONFIG_PATH, 'r') as f:
            config = json.load(f)
        # Ensure all necessary keys are present, falling back to defaults if not
        return {
            "DB_HOST": config.get("DB_HOST", "localhost"),
            "DB_PORT": config.get("DB_PORT", 3306),
            "DB_USER": config.get("DB_USER", "root"),
            "DB_PASSWORD": config.get("DB_PASSWORD", ""),
            "DB_NAME": config.get("DB_NAME", "EntPrice")
        }
    except (IOError, json.JSONDecodeError) as e:
        print(f"Error reading config file {CONFIG_PATH}: {e}")
        # Fallback to default values if read fails
        return {
            "DB_HOST": "localhost",
            "DB_PORT": 3306,
            "DB_USER": "root",
            "DB_PASSWORD": "",
            "DB_NAME": "EntPrice"
        }

def get_db_connection():
    """
    Establishes a connection to the MySQL database using the configuration.
    Returns the connection object or None if connection fails.
    """
    config = get_db_config()
    try:
        conn = mysql.connector.connect(
            host=config["DB_HOST"],
            port=config["DB_PORT"],
            user=config["DB_USER"],
            password=config["DB_PASSWORD"],
            database=config["DB_NAME"]
        )
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting to database: {err}")
        # Depending on requirements, you might want to raise the error,
        # or handle it by returning None or a specific error code.
        return None

def update_db_config(new_config_data):
    """
    Updates the database configuration in config.json.
    
    Args:
        new_config_data (dict): A dictionary containing the configuration
                                 keys and values to update.
    
    Returns:
        bool: True if the configuration was updated successfully, False otherwise.
    """
    current_config = get_db_config() # Ensures config.json exists or defaults are loaded

    # Update current_config with values from new_config_data
    # Only update keys that are expected in the config
    expected_keys = {"DB_HOST", "DB_PORT", "DB_USER", "DB_PASSWORD", "DB_NAME"}
    for key, value in new_config_data.items():
        if key in expected_keys:
            current_config[key] = value
        else:
            print(f"Warning: Unknown configuration key '{key}' provided.")


    try:
        with open(CONFIG_PATH, 'w') as f:
            json.dump(current_config, f, indent=2)
        return True
    except IOError as e:
        print(f"Error writing updated config to {CONFIG_PATH}: {e}")
        return False

if __name__ == '__main__':
    # Example usage (optional, for testing purposes)
    print("Current DB Config:", get_db_config())
    
    # Test database connection
    connection = get_db_connection()
    if connection:
        print("Database connection successful.")
        connection.close()
    else:
        print("Database connection failed.")

    # Test updating config (be cautious with actual credentials)
    # success = update_db_config({"DB_USER": "new_user", "DB_PASSWORD": "new_password"})
    # if success:
    #     print("DB Config updated. New config:", get_db_config())
    # else:
    #     print("Failed to update DB Config.")
    
    # To restore default config if a default file exists and config.json was changed:
    # if os.path.exists(DEFAULT_CONFIG_PATH) and os.path.exists(CONFIG_PATH):
    #     os.remove(CONFIG_PATH) # Remove current config
    #     print("Restored to default config by removing config.json.")
    #     print("New DB Config:", get_db_config()) # This will recopy default
    pass

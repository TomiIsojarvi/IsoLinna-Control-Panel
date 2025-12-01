import os
import json
import uuid
import pyrebase
import time
import sys

import globals

from login_screen import LoginScreen
from main_screen import MainScreen
from constants import *

#------------------------------------------------------------------------------------------------#
#                                              MAIN                                              #
#------------------------------------------------------------------------------------------------#
def main():
    global LOGIN_SCREEN_HEIGHT, MAIN_SCREEN_HEIGHT, SETTINGS_PATH, FIREBASE_CONF_PATH

    # Load settings...

    # Does settings-file exists?
    if os.path.isfile(SETTINGS_PATH):
        # Yes...
        # Is the file empty?
        if os.path.getsize(SETTINGS_PATH) > 0:
            # No ...    
            # Read the settings from settings-file
            try:
                with open(SETTINGS_PATH, 'r') as f:
                    globals.settings = json.load(f)
                    # initialise discovered_sensors
                    globals.discovered_sensors = globals.settings['followed_sensors'].copy()
            except IOError:
                print(f"{SETTINGS_PATH}: Could not open file. Please check the file's permissions.")
                sys.exit(1)
            except json.JSONDecodeError:
                print(f"{SETTINGS_PATH}: File contains invalid JSON.")
                sys.exit(1)
        else:
            # Yes...
            print(f"{SETTINGS_PATH}: File is empty.")
            sys.exit(1)
    else:
        # No...
        # Create default settings
        globals.settings['time_interval'] = 1
        globals.settings['device_uuid'] = str(uuid.uuid1())  # Generate UUID and convert it to string
        globals.settings["broadcasting"] = False
        globals.settings['followed_sensors'] = []

        # Save settings to settings-file
        try:
            with open(SETTINGS_PATH, 'w') as f:
                json.dump(globals.settings, f, indent=4) 
        except IOError:
            print(f"{SETTINGS_PATH}: Could not write file. Please check if you have write permissions.")
            sys.exit(1)

    # Load Firebase configuration...

    # Does configuration-file exists?
    if os.path.isfile(FIREBASE_CONF_PATH):
        # Yes...
        # Is the file empty?
        if os.path.getsize(FIREBASE_CONF_PATH) > 0:
            # No ...    
            # Read the configuration from configuration-file
            try:
                with open(FIREBASE_CONF_PATH, 'r') as f:
                    globals.firebase_config = json.load(f)
            except IOError:
                print(f"{FIREBASE_CONF_PATH}: Could not open file. Please check the file's permissions.")
                sys.exit(1)
            except json.JSONDecodeError:
                print(f"{FIREBASE_CONF_PATH}: File contains invalid JSON.")
                sys.exit(1)
        else:
            # Yes...
            print(f"{FIREBASE_CONF_PATH}: File is empty.")
            sys.exit(1)
    else:
        # No...
        print(f"{FIREBASE_CONF_PATH}: File does not exist.")
        sys.exit(1)

    # Setup Firebase...

    try:
        firebase = pyrebase.initialize_app(globals.firebase_config)
        globals.auth = firebase.auth()
        globals.db = firebase.database()
    except KeyError as e:
        print(f"Firebase configuration is missing a required key: {e}")
        sys.exit(1) 
    except ValueError as e:
        print(f"Invalid value in Firebase configuration: {e}")
        sys.exit(1)
    except TypeError as e:
        print(f"Incorrect Firebase configuration format: {e}")
        sys.exit(1)
    except AttributeError as e:
        print(f"Error initializing Firebase services: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)
    
    # Main loop...
    while True:
        # Are the user ID and the Refresh Token already in Settings?
        if 'user_uid' in globals.settings and 'refresh_token' in globals.settings:
            # Yes...
            # Go to Main Screen.
            main_screen = MainScreen(MAIN_SCREEN_WIDTH, MAIN_SCREEN_HEIGHT)
            main_screen.main()
        else:
            # No...
            # Go to Login Screen.
            login_screen = LoginScreen(LOGIN_SCREEN_WIDTH, LOGIN_SCREEN_HEIGHT, globals.auth)
            user = login_screen.main()

            # If login was successful...
            if user:
                globals.settings['user_uid'] = user['localId']
                globals.settings['id_token'] = user['idToken']
                globals.settings['refresh_token'] = user['refreshToken']
                globals.settings['token_expiration_time'] = int(time.time()) + int(user['expiresIn'])

                # Save settings to settings-file
                try:
                    with open(SETTINGS_PATH, 'w') as f:
                        json.dump(globals.settings, f, indent=4) 
                except IOError:
                    print(f"{SETTINGS_PATH}: Could not write file. Please check if you have write permissions.")
                    sys.exit(1)

                

if __name__ == "__main__":
    main()
from kivy.utils import platform
from kivymd.app import MDApp
import os.path
# Borrowed from https://stackoverflow.com/questions/52981411/cant-write-file-on-ios-using-kivy-in-python
# Needed for iOS devices
# This is due to the fact that iOS won't allow write access to files not
# in root directory
if platform == 'ios':
    root_folder = MDApp().user_data_dir
    CACHE_DIR = os.path.join(root_folder, 'cache')
    cache_folder = os.path.join(root_folder, 'cache')
    CACHE_DIR = cache_folder
else:
    CACHE_DIR = "cache"

if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)
    # Create access token file as it will be read first
    with open(os.path.join(CACHE_DIR, "access_token.json"), "w+") as file:
        pass

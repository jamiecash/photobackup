"""
File: backup.py
Author: Jamie Cash
Date: 3 Mar 2024
Description: The backup script. Run this manually or add this to your cron tab
    to automate backups of photos stored on the cloud. 
"""
import logging
import os
import pandas as pd
from pathlib import Path

import config
from photobackup.cloudprovider import CloudProvider


def main():
    # Logging setup
    logging.basicConfig(level=logging.DEBUG)
    _log = logging.getLogger('main')

    # Get the correct cloud provider and authenticate.
    cp = CloudProvider()
    cp.authenticate()

    # Get info for all media if we don't already have it. If we do, load it
    # from file. This will enable application to restart on failure and pick up 
    # where it left off. Temp media info file should be deleted on completion of 
    # sucessful backup.
    if os.path.exists(r'temp/mediainfo.hfd'):
        photos = pd.read_hdf(r'temp/mediainfo.hfd', 'media')
    else:
        photos = cp.get_media_info()

    # Create local file names
    
        
    # Get list of all media already backed up and set to done
    result = list(Path(config.backup_location).rglob("*.*"))
    print(result)

    # Save the media info file
    photos.to_hdf(r"_temp/mediainfo.hfd", 'media')



if __name__ == "__main__":
    main()
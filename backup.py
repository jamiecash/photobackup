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
    MEDIAINFO_FILENAME = '_temp/mediainfo.hfd'

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
    if os.path.exists(MEDIAINFO_FILENAME):
        photos = pd.read_hdf(MEDIAINFO_FILENAME, key='media')
    else:
        photos = cp.get_media_info()

        # Create save file name from the backup location, the creation date and 
        # the filename.
        path = config.backup_location + '/' if path[-1] not in ["/", "\\"] else ''
        photos['saveAs'] = 'm:/backup/' + \
            photos['creationTime'].dt.strftime('%Y%m%d') + '/' + \
            photos['filename']
    
        
    # Get list of all media already backed up and set to done
    backup_files = list(Path(config.backup_location).rglob("*.*"))
    photos['backupComplete'] = photos['saveAs'].isin(backup_files)

    # Save the media info file
    photos.to_hdf(MEDIAINFO_FILENAME, key='media')

    # Backup the files that haven't already been backed up.
    for index, row in photos[photos['backupComplete']==False].iterrows():
        cp.save_media_item(row['id'], row['saveAs'])
        
        # Set backup complete and save file
        photos.iloc[index]['backupComplete'] == True
        photos.to_hdf(MEDIAINFO_FILENAME, key='media')

    # Delete mediainfo file
    os.remove(MEDIAINFO_FILENAME)
        
if __name__ == "__main__":
    main()
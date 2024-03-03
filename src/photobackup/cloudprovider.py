"""
File: cloudprovider.py
Author: Jamie Cash
Date: 3 Mar 2024
Description: CloudProvider classes to access the photo cloud providers APIs. 
"""

import abc
import config
from datetime import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import logging
import os
import pandas as pd

class CloudProvider(metaclass=abc.ABCMeta):
    """
    Interface for cloud providers. Instantiating  this class will instantiate the 
    correct CloudProvider implementation based on the cloud provider set in 
    config.py. 
    """

    def __new__(cls):
        """
        Return the correct cloud provider
        """
        _log = logging.getLogger(__name__)

        # Get the correct cloud provider class based on settings
        clz = cloud_providers[config.cloud_provider]
        _log.info(f"Using '{clz.__name__}' as the cloud service provider.")
        
        # Return it
        return super(CloudProvider, cls).__new__(clz)

    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'authenticate') and 
                callable(subclass.authenticate))
    
    @abc.abstractmethod
    def authenticate(self):
        """
        Authenticate with cloud provider
        """
        raise NotImplementedError
    
    def get_media_info(self) -> pd.DataFrame:
        """
        Get the metadata for all media items.

        Returns:
            pd.DataFrame: A dataframe containing the metadata for all media 
            items stored with your cloud provider.
        """
        raise NotImplementedError

    def save_media_item(id: str, filename: str):
        """
        Get the specified media item and saves it to disk.

        Arguments:
            id (str): The id of the media item to get as required by your cloud
                providers get media api.
            filename (str)@ The filename to save the media item as.
        """
        raise NotImplementedError
    
    
class GoogleCloudProvider(CloudProvider):
    """
    Access Google Photos API to authenticate and get photos. 
    """

    _log = logging.getLogger(__name__)
    _api = None


    def authenticate(self):
        """
        Authenticate with Google
        """
        self._log.info("Authenticating with Google.")
        SCOPES = ['https://www.googleapis.com/auth/photoslibrary.readonly']
        creds = None

        # If we have already authenticated and have a token, use it
        if os.path.exists('_auth/token.json'):
            creds = Credentials.from_authorized_user_file('_auth/token.json', SCOPES)
                
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    '_auth/client_secret.json', SCOPES)
                creds = flow.run_local_server()
            
            # Save the token for the next run
            with open('_auth/token.json', 'w') as token:
                token.write(creds.to_json())

        self._api = build('photoslibrary', 'v1', credentials=creds, 
                          static_discovery=False)

    def get_media_info(self) -> pd.DataFrame:
        """
        Get the metadata for all media items.

        Returns:
            pd.DataFrame: A dataframe containing the metadata for all media 
            items stored with your cloud provider.
        """
       
        # Get the media items from the Google API. We will use a page size of 100.
        # This will take a while. 
        items = []
        nextpagetoken = None
        start = datetime.now()
        self._log.info(f"Started creating list at {start.strftime('%H:%M:%S')}.")
        while nextpagetoken != '':
            self._log.debug(f"Number of items processed: {len(items)}.")
            results = self._api.mediaItems().list(
                pageSize=100, pageToken=nextpagetoken).execute()
            items += results.get('mediaItems', [])
            nextpagetoken = results.get('nextPageToken', '')

        end = datetime.now()
        elapsed = end - start
        self._log.info(f"Finished creating list at {end.strftime('%H:%M:%S')}. \
                       Elapsed {str(elapsed).split('.')[0]}.")

        # Convert the list of dict into a dataframe and split mediaMetadata into 
        # individual columns.
        df = pd.DataFrame(items)
        dfmeta = df.mediaMetadata.apply(pd.Series)
        photos = pd.concat(
            [
                df.drop('mediaMetadata', axis=1), 
                dfmeta.drop('photo', axis=1), 
                dfmeta.photo.apply(pd.Series)
            ], axis=1)

        return photos

            
cloud_providers = {
    'Google': GoogleCloudProvider
}
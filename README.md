# Photo Backup
Precious family photos on the cloud are at risk of being lost if the company 
hosting them stops trading or if you stop paying for your storage.

Use this application to take regular backups of your photos to local or NAS 
storage.

## Configuration
Run the following to install dependencies.

```
pip install -r requirements.txt
```

Set the _cloud_provider_ and *backup_location* in config.py

This script currently only supports backing up from Google Photos. However it 
has been designed to easily add additional cloud providers by creating new 
CloudProvider instances. See the **Enhancing this Application** section for 
more information.

Follow your cloud providers instructions for accessing their api and saving 
credentials. Instructions for supported providers is provided below.

### Google
Follow the instructions in the google photos api 
[Getting Started](https://developers.google.com/photos/library/guides/get-started) 
guide to enable the Google API and setup credentials. As you will not be 
providing this app to non trusted users, add yourself and anyone else who will 
run this script as test users.

Download the client secrets json file into the '_auth' folder for this project. 
Make sure it is named 'client_secrets.json'

## Usage
Run the backup python script. 

```
python backup.py
```

The first time that you run it, you may be asked to authorise access to your 
cloud providers account. Follow the instructions in the message.

The application reguarly saves its state, and can recover if it is stopped 
before completing a backup.

## Enhancing this Application

### Adding a new cloud provider

#### In requirements.txt
Add any libraries required by your cloud provider to 'requirements.txt' and run 
the following to install them.

```
pip install -r requirements.txt
```

#### In cloudprovider.py
* Create a new class that inherits from _CloudProvider_;
* Implement its _authenticate_, *get_media_info*_ & *save_media_item* methods; and
* Add cloud provier to the *__cloud_providers* dictionary at the bottom of the 
file.

The name of the provider can be any string, it will be used in 'config.py' 
to set the cloud provider to use.

#### In config.py
* Set *cloud_provider* to the name of your new cloud provider as specified in 
the *__cloud_providers* dictionary in 'cloudprovider.py'.  
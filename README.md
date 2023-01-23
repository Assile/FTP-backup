# FTP backup script
This script allows you to backup an FTP server to a local drive. It assumed the server is a regular FTP server (no SSL) and only needs a host link, username, and password. Currently the script recursively moves through the files in the FTP server to collect the files to download and then downloads said files.

# Setup

- `pip install -r requirements.txt`
- Create a file named `.env` containing the following contents (replace the bits in between `<>`, including the brackets, with your own values):
```
FTP_HOST=<host.url>
FTP_USER=<username>
FTP_PASSWORD=<password>
```
- Run the script, some examples follow:
```powershell
# For Windows
python ftp_backup.py --time_stamp "C:\Users\myname\backups\"
```
```sh
# For Linux
python3 ftp_backup.py --time_stamp ~/backups/
```

# Wishlist
- To make a non-recursive version.
- To download the files as they are discovered.
import requests
import os
import re
from shutil import disk_usage as du
import mimetypes
import pathlib

# https://drive.google.com/file/d/1IVPq8VODLpLaP_EDhIaz88PflYQqi4dE/view?usp=sharing
# https://drive.google.com/drive/folders/1g-UCIJBVn6FakY6PqJGk?usp=sharing

class Downloader: 

    def __init__(self, url):
        
        self.output_dir = os.getcwd()
        self.url = url
        self.d_url = 'https://docs.google.com/uc?export=download' # Link for dowlnloading form gdrive

    def get_id_from_url(self):
        
    
        # for files - https://drive.google.com/file/d/FILE-ID-GOES-HERE/view?usp=sharing
        id = re.search('/d/(.*)/view\?usp=sharing', self.url)
        if not id: 
            # for folders - https://drive.google.com/drive/folders/FOLDER-ID-GOES-HERE?usp=sharing
            id = re.search('/folders/(.*)\?usp=sharing', self.url)
        if id:
            return id[1]
        else:
            return None


    def check_system_storage(self, file_size):

        if int(file_size) >= du(os.getcwd()).free:
            raise RuntimeError('Not enough space available') 


    def after_download_file_check(self, filename, headers):

        downloaded_file_properties = {}
        original_file= {}

        downloaded_file_properties['fullpath'] = os.path.join(os.getcwd(), filename)
        downloaded_file_properties['name'] = filename
        downloaded_file_properties['size'] = os.path.getsize(downloaded_file_properties['fullpath'])
        downloaded_file_properties['type'] = mimetypes.types_map[pathlib.PurePath(filename).suffix]

        original_file['fullpath'] = os.path.join(os.getcwd(), filename)
        original_file['name'] = filename
        original_file['size'] = int(headers['Content-Length'])
        original_file['type'] = headers['Content-Type']

        if downloaded_file_properties == original_file:
            result = True
        else:
            raise RuntimeError("Download did not happen properly")

        return downloaded_file_properties, result


    def download(self):

        file_id = self.get_id_from_url()
        if file_id: 
            with requests.Session() as sess: 
                raw = sess.get(self.d_url, params = { 'id' : file_id }, stream = True, allow_redirects=True) 
                try:
                    temp = re.search('filename="(.*)"', raw.headers['Content-Disposition'])  
                    size = raw.headers['Content-Length']
                    self.check_system_storage(size)
                except KeyError:
                    return ("Wrong Input", "Could not downoad the file", 404)
                
                filename = temp.groups()[0]
                chunk = 1024 * 256
                with open( os.path.join(self.output_dir, filename), 'wb') as output_file:
                    for value in raw.iter_content(chunk):
                        if value:
                            output_file.write(value)

            downloaded_file_properties, result = self.after_download_file_check(filename, raw.headers)
            rc = 0
            return rc, downloaded_file_properties, raw.status_code

        else:
            raise RuntimeError('Not able to retrieve File ID')


if __name__ == '__main__':
    
    #file_id = '1IVPq8VODLpLaP_EDhIaz88PflYQqi4dE'
    url = "https://drive.google.com/file/d/1IVPq8VODLpLaP_EDhIaz88PflYQqi4dE/view?usp=sharing"
    obj = Downloader(url)
    sc, filename, rc = obj.download()
    print(sc, filename, rc)


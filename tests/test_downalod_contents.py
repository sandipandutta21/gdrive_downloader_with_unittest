import pytest
from requests.models import Response 
from drive_downloader.download_contents import Downloader
from unittest import mock
from unittest.mock import Mock
import random


def mocked_request_dot_get_with_bytes_response(flag=0):

    if flag == 0:
        data = bytes(b"73 61 6d 70 6c 65 20 70 64 66 20 66 69 6c 65 20 66 6f 72 20 74 68 69 73 20 74 65 73 74 20")
    else:
        data = str('73 61 6d 70 6c 65 20 70 64 66 20 66 69 6c 65 20 66 6f 72 20 74 68 69 73 20 74 65 73 74 20')
    mock_raw = Mock()
    mock_raw.headers = {'Content-Type': 'text/plain', 'Content-Disposition': 'attachment;filename="mockfile.txt";filename*=UTF-8\'\'mockfile.txt', 'Content-Length': '89'}
    mock_raw.text = data
    mock_raw.status_code = 200

    def iter_content(size=2):
        mocked_data = data
        while mocked_data:
            mocked_chunk = data[:size]
            mocked_data = data[size:]
            yield mocked_chunk

    mock_raw.iter_content = iter_content
    return mock_raw


class TestDownloader():

    downaloder_links = [("https://drive.google.com/file/d/1IVPq8VODLpLaP_EDhIaz88PflYQqi4dE/view?usp=sharing", 200), 
                         ("https://drive.google.com/drive/folders/1g-UCIJBVn6FakY6Pkk4JJYwMljOBqJGk?usp=sharing", 404),
                          ("https://drive.google.com/file/d/1IVPq8VODLpLaP_EDhIaz88PflYQqi4E/view?usp=sharing", 404), 
                        ]

    retriever_link = [("https://drive.google.com/file/d/1IVPq8VODLpLaP_EDhIaz88PflYQqi4dE/view?usp=sharing", "1IVPq8VODLpLaP_EDhIaz88PflYQqi4dE"),
                        ("https://drive.google.com/file/1IVPq8VODLpLaP_EDhIaz88PflYQqi4dE/view?usp=sharing", None) 
                     ]

    # This is to test the download functionality - download()
    @pytest.mark.parametrize("link, expected", downaloder_links)
    def test_download(self, link, expected):
        returns = []
        obj = Downloader(link)
        sc, file_prop, rc = obj.download()
        assert rc == expected 


    # This is to test the case where the ID is not pressent in the URL or the URL is not in the correct format - download()
    def test_download_with_exception(self):
        link = 'https://www.url.which/is/not/correct/d/'
        obj = Downloader(link)
        with pytest.raises(RuntimeError) as e:
            obj.download()
        assert str(e.value) == 'Not able to retrieve File ID'
            

    # This is to test the ID retriver form URL - get_id_from_url()
    @pytest.mark.parametrize("link, expected", retriever_link)
    def test_get_id_from_url(self, link, expected):
        obj = Downloader(link)
        assert obj.get_id_from_url() == expected

    # What if the filename already exist - download() -- This test will fail as we are just passing the cloud file's name as the output filename
    def test_for_same_filename_already_exist(self):
        obj = Downloader("https://drive.google.com/file/d/1IVPq8VODLpLaP_EDhIaz88PflYQqi4dE/view?usp=sharing")
        sc1, file_prop1, rc1 = obj.download()
        sc2, file_prop2, rc2 = obj.download()
        assert file_prop2['name'] != file_prop1['name']  

    @mock.patch('requests.Session.get', return_value=mocked_request_dot_get_with_bytes_response())
    def test_downlaoder_without_internet_bytes(self, mock_get):

        obj = Downloader("https://fake.domain/file/d/1IVPq8VODLpLaP_EDhIaz88PflYQqi4dE/view?usp=sharing")
        rc, file_prop, sc = obj.download()
        assert sc == 200 and rc == 0

    # It will fail as the content is in string not bytes
    @mock.patch('requests.Session.get', return_value=mocked_request_dot_get_with_bytes_response(flag=1))
    def test_downlaoder_without_internet_string(self, mock_get):

        obj = Downloader("https://fake.domain/file/d/1IVPq8VODLpLaP_EDhIaz88PflYQqi4dE/view?usp=sharing")
        rc, file_prop, sc = obj.download()
        

    def test_for_check_system_storage(self):
        obj = Downloader("https://fake.domain/file/d/1IVPq8VODLpLaP_EDhIaz88PflYQqi4dE/view?usp=sharing")
        with pytest.raises(RuntimeError) as e:
            obj.check_system_storage(random.randint(888888, 9999999) * 100000)
            #assert e == "RuntimeError('Not enough space available')"
        assert str(e.value) == 'Not enough space available'

"""
Obtains list of URLs for photos for Google Photos album.

They will be then used in calls to /bg.jpg.
You have to have .env file filled with OAuth client values, as well as
album ID.

If you're running this script for the first time, it will ask you to authorize
with OAuth. Copy URL printed in the console to browser, and after being
redirected to http://localhost:12345/auth_return?code=<SOMETHING>
copy and paste <SOMETHING> to console.
"""
from os.path import join, dirname
from xml.etree import ElementTree
import httplib2
import json
import os

from oauth2client.client import OAuth2WebServerFlow
from oauth2client.file import Storage
from dotenv import load_dotenv


dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
# Handle credentials
storage = Storage('./credentials')
credentials = storage.get()
if not credentials:
    # Note: this will
    flow = OAuth2WebServerFlow(
        client_id=os.environ['GOOGLE_CLIENT_ID'],
        client_secret=os.environ['GOOGLE_CLIENT_SECRET'],
        scope='https://picasaweb.google.com/data/',
        redirect_uri='http://localhost:12345/auth_return'
    )
    print(flow.step1_get_authorize_url())
    code = input('Enter code: ')
    credentials = flow.step2_exchange(code)
    storage.put(credentials)
    print('Credentials saved!')
http = httplib2.Http()
http = credentials.authorize(http)
# OK, now get the photos!
url = 'https://picasaweb.google.com/data/feed/api/user/default/albumid/{}'
resp, content = http.request(url.format(os.environ['PICASA_ALBUM_ID']))
root = ElementTree.fromstring(content)
urls = []
for child in root:
    if not child.tag.endswith('entry'):
        continue
    for inner in child:
        if not inner.tag.endswith('group'):
            continue
        for media in inner:
            if not media.tag.endswith('thumbnail'):
                continue
            url = media.attrib['url'].replace('/s72/', '/s1600/')
            url = url[:url.rfind('/') + 1]
            urls.append(url)
            break
        break
with open('urls.json', 'w') as f:
    f.write(json.dumps(urls))
print('Done.')

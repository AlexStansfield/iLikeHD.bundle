import urllib
import base64

from crypto.cipher.aes_cbc import AES_CBC
from crypto.cipher.base import noPadding


class Api(object):
    def __init__(self, config):
        self.config = config

    def login(self, username, password):
        login_params = {'secret_key': self.config.API_KEY,
                        'output': 'xml', 'e': base64.b64encode(username),
                        'p': base64.b64encode(password)}
        login_url = self.config.API_URL_LOGIN + '?' + str(urllib.urlencode(login_params))
        login_xml = XML.ElementFromURL(login_url, headers={'User-Agent': self.config.API_USER_AGENT})
        self.user_id = login_xml.find("customers_id").text
        self.session_key = login_xml.find("session_key").text
        return self.user_id

    def getChannels(self, category):
        channels_params = {'uid': self.user_id, 'session_key': self.session_key, 'quality': 'Auto', 'server': 'auto',
                           'crypt': 'true', 'cat': category}
        channels_url = self.config.API_URL_CHANNELS + '?' + str(urllib.urlencode(channels_params))
        channels_xml = XML.ElementFromURL(channels_url, headers={'User-Agent': self.config.API_USER_AGENT})
        channels = []
        for channel in channels_xml.iter('channel'):
            if channel.find('channel_available').text != 'yes':
                continue
            code = channel.find('hls_url').text
            code = code.decode("hex")
            cipher = AES_CBC(self.config.CIPHER_SECRET, noPadding())
            hls_url = cipher.decrypt(code, self.config.CIPHER_IV)
            hls_url = hls_url.rstrip("\0")
            channels.append({'code': channel.find('channel_code').text, 'name': channel.find('channel_name').text,
                             'thumb': channel.find('channel_thumb').text, 'hls_url': hls_url})
        return channels

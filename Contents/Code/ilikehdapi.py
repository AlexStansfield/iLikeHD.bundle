import urllib
import base64
import time

from crypto.cipher.aes_cbc import AES_CBC
from crypto.cipher.base import noPadding

class Api(object):
    def __init__(self, config):
        self.config = config

    def login(self, username, password):
        login_params = {
            'ukey': self.config.API_DEVICE_UKEY,
            'user_email': username,
            'user_password': password
        }
        login_url = self.config.API_URL_LOGIN + '?' + str(urllib.urlencode(login_params))
        login_xml = XML.ElementFromURL(login_url, headers={'User-Agent': self.config.API_USER_AGENT})
        self.user_id = login_xml.find("user_id").text
        return self.user_id

    def getChannels(self, category):
        channels_params = {'uid': self.user_id, 'category_id': category}
        channels_url = self.config.API_URL_CHANNELS + '?' + str(urllib.urlencode(channels_params))
        channels_xml = XML.ElementFromURL(channels_url, headers={'User-Agent': self.config.API_USER_AGENT})
        channels = []
        channel_codes = []
        for channel in channels_xml.iter('channel'):
            if channel.find('have_package').text != '1':
                continue
            code = channel.find('channel_code').text
            channel_codes.append(code)
            channels.append({
                'code': code,
                'name': channel.find('channel_name').text,
                'thumb': self.config.API_URL_THUMBS + channel.find('channel_code').text + '.png'
            })

        nowShowing = self.getChannelsNowShowing(channel_codes)
        for channel in channels:
            if channel['code'] in nowShowing:
                channel['now_showing'] = nowShowing[channel['code']]

        return channels

    def getStream(self, channel):
        stream_params = {'c': channel, 'uid': self.user_id, 'ukey': self.config.API_DEVICE_UKEY}
        stream_url = self.config.API_URL_STREAM + '?' + str(urllib.urlencode(stream_params))
        stream_xml = XML.ElementFromURL(stream_url, headers={'User-Agent': self.config.API_USER_AGENT})
        code = stream_xml.find('clear_url').text
        code = code.decode("hex")
        cipher = AES_CBC(self.config.CIPHER_SECRET, noPadding())
        hls_url = cipher.decrypt(code, self.config.CIPHER_IV)
        hls_url = hls_url.rstrip("\0")
        return hls_url

    def getChannelNowShowing(self, channel):
        epg_params = {'channel': channel}
        epg_url = self.config.API_URL_EPG_SINGLE + '?' + str(urllib.urlencode(epg_params))
        epg_json = JSON.ObjectFromURL(epg_url)

        nowShowing = self.getNowShowing(epg_json)

        return nowShowing

    def getChannelsNowShowing(self, channels):
        epg_params = {'ccodes': ','.join(channels)}
        epg_url = self.config.API_URL_EPG_MULTI + '?' + str(urllib.urlencode(epg_params))
        epg_json = JSON.ObjectFromURL(epg_url)

        epg = {}

        for channel in epg_json['kdata']['channel']:
            nowShowing = self.getNowShowing(channel['epg'])
            if (len(nowShowing) > 0):
                epg[channel['channel_code']] = nowShowing

        return epg

    def getNowShowing(self, epg):
        nowShowing = {}

        epoch = time.time()

        for show in epg:
            if ((show['start_time'] < epoch) and (show['end_time'] > epoch)):
                nowShowing = {
                    'name': show['title_name_eng'],
                    'start_time': show['start_time_human'],
                    'end_time': time.strftime("%H:%M", time.localtime(show['end_time'])),
                    'duration': show['duration'],
                    'description': show['desc']
                }
                break

        return nowShowing

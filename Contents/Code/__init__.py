import config
import ilikehdapi
import ast
import json
import types
import urllib

####################################################################################################

PREFIX = "/video/ilikehd"
NAME = "iLikeHD"
ICON = R('icon-default.png')

API = ilikehdapi.Api(config)

####################################################################################################

# This function is initially called by the PMS framework to initialize the plugin. This includes
# setting up the Plugin static instance along with the displayed artwork.
def Start():
    # Setup the default breadcrumb title for the plugin
    ObjectContainer.title1 = NAME


# This main function will setup the displayed items.
# Initialize the plugin
@handler(PREFIX, NAME, thumb=ICON)
def MainMenu():
    oc = ObjectContainer()

    # Add Categories option
    oc.add(DirectoryObject(key=Callback(CategoriesMenu), title="Categories"))
    # Add Main Menu Categories
    for category in config.CATEGORIES_MAIN:
        oc.add(DirectoryObject(key=Callback(CategoryMenu, category=category), title=category['title']))
    # Add Preferences
    oc.add(PrefsObject(title=L('Preferences')))

    return oc


@route(PREFIX + '/categoriesmenu')
def CategoriesMenu():
    oc = ObjectContainer(title1="Categories")
    for category in config.CATEGORIES_ALL:
        oc.add(DirectoryObject(key=Callback(CategoryMenu, category=category), title=category['title']))
    return oc


@route(PREFIX + '/categorymenu', category=dict)
def CategoryMenu(category):
    API.login(Prefs['username'], Prefs['password'])
    channels = API.getChannels(category["id"])
    oc = ObjectContainer(title1=category["title"])
    for channel in channels:
        oc.add(CreateChannelObject(channel=channel))
    return oc


@route(PREFIX + '/createchannelobject')
def CreateChannelObject(channel, container=False):
    if (type(channel) != types.DictionaryType):
        Log.Debug(channel)
        Log.Debug(urllib.unquote_plus(channel))
        channel = ast.literal_eval(urllib.unquote_plus(channel))

    if 'now_showing' in channel:
        title = channel['name'] + ' - ' + channel['now_showing']['name']
        summary = channel['now_showing']['description']
    else:
        title = channel['name']
        summary = 'Description not available'

    vco = VideoClipObject(
        key=Callback(CreateChannelObject, channel=channel, container=True),
        rating_key=channel['code'],
        title=title,
        thumb=channel['thumb'],
        summary=summary,
        items=[
            MediaObject(
                #container = Container.MP4,     # MP4, MKV, MOV, AVI
                #video_codec = VideoCodec.H264, # H264
                #audio_codec = AudioCodec.AAC,  # ACC, MP3
                #audio_channels = 2,            # 2, 6
                parts=[
                    PartObject(
                        key=HTTPLiveStreamURL(url=Callback(PlayVideo, channel=channel['code'], stuff="junk"))
                    )
                ],
                #optimized_for_streaming=True
            )
        ]
    )

    if container:
        return ObjectContainer(objects=[vco])
    else:
        return vco

@route(PREFIX + "/play/{channel}/{stuff}")
def PlayVideo(channel, stuff):
    url = API.getStream(channel)
    return Redirect(url)
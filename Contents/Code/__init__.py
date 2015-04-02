import config
import ilikehdapi

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
    channels = API.getChannels(category["id"], Prefs['quality'], Prefs['server'])
    oc = ObjectContainer(title1=category["title"])
    for channel in channels:
        oc.add(CreateVideoClipObject(url=channel['hls_url'], title=channel['name'], thumb=channel['thumb']))
    return oc


@route(PREFIX + '/createvideoclipobject')
def CreateVideoClipObject(url, title, thumb, container=False):
    vco = VideoClipObject(
        key=Callback(CreateVideoClipObject, url=url, title=title, thumb=thumb, container=True),
        # rating_key = url,
        url=url,
        title=title,
        thumb=thumb,
        items=[
            MediaObject(
                #container = Container.MP4,     # MP4, MKV, MOV, AVI
                #video_codec = VideoCodec.H264, # H264
                #audio_codec = AudioCodec.AAC,  # ACC, MP3
                #audio_channels = 2,            # 2, 6
                parts=[
                    PartObject(
                        key=HTTPLiveStreamURL(url=url)
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
import config
import ilikehdapi

####################################################################################################

PREFIX = "/video/ilikehd"
NAME = "iLikeHD"
ICON = R('icon-default.png')

API = ilikehdapi.Api(config)
API_USER = Prefs['username']
API_PASS = Prefs['password']

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
    oc.add(DirectoryObject(key=Callback(CategoriesMenu), title="Categories"))
    oc.add(DirectoryObject(key=Callback(CategoryMenu, category="my", title="Favourites"), title="Favourites"))
    oc.add(DirectoryObject(key=Callback(CategoryMenu, category="pop", title="Popular"), title="Popular"))
    oc.add(DirectoryObject(key=Callback(CategoryMenu, category="all", title="All"), title="All Channels"))
    oc.add(PrefsObject(title=L('Preferences')))
    return oc

@route(PREFIX + '/categoriesmenu')
def CategoriesMenu():
    oc = ObjectContainer(title1="Categories")
    for category_id, category_name in config.CATEGORIES.items():
        oc.add(
            DirectoryObject(key=Callback(CategoryMenu, category=category_id, title='Categories', title2=category_name),
                            title=category_name))
    return oc

@route(PREFIX + '/categorymenu')
def CategoryMenu(category, title, title2=None):
    API.login(API_USER, API_PASS)
    channels = API.getChannels(category)
    oc = ObjectContainer(title1=title, title2=title2)
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
                #aspect_ratio = "1.78",
                #container = Container.MP4,     # MP4, MKV, MOV, AVI
                #video_codec = VideoCodec.H264, # H264
                #audio_codec = AudioCodec.AAC,  # ACC, MP3
                #audio_channels = 2,            # 2, 6
                parts=[
                    PartObject(
                        key=HTTPLiveStreamURL(url=url)
                    )
                ],
                video_resolution='720',
                optimized_for_streaming=True
            )
        ]
    )

    if container:
        return ObjectContainer(objects=[vco])
    else:
        return vco
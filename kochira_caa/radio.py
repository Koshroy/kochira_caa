"""
CAA r/a/dio.

Like 4chan, except CAA.
"""
import requests

from kochira import config
from kochira.auth import requires_permission
from kochira.service import Service, background, Config
from lxml import etree

service = Service(__name__, __doc__)

@service.config
class Config(Config):
    username = config.Field(doc="Username for HTTP basic auth.")
    password = config.Field(doc="Password for HTTP basic auth.")
    url = config.Field(doc="URL of the Icecast2 admin page.")
    mount = config.Field(doc="Name of the Icecast2 mountpoint.")

def _np(ctx):
    config = ctx.config
    mount = config.mount
    r = etree.fromstring(requests.get(config.url, auth=(config.username, config.password)).content)

    mount_exists = bool(r.xpath("source[@mount='{}']".format(mount)))
    artist = r.xpath("source[@mount='{}']/artist/text()".format(mount))
    title = r.xpath("source[@mount='{}']/title/text()".format(mount))

    if not mount_exists:
        return None
    return (artist[0] if artist else "", title[0] if title else "")

@service.command("^\.np$")
@requires_permission("caa_radio")
@background
def now_playing(ctx):
    """
    Now playing.

    Gets the metadata of the currently playing song.
    """
    np = _np(ctx)
    if not np:
        ctx.message("\x02Now playing:\x02 Nothing!")
    elif np == ("", ""):
        ctx.message("\x02Now playing:\x02 No metadata available!")
    else:
        ctx.message("\x02Now playing:\x02 {}".format(" - ".join(np)))

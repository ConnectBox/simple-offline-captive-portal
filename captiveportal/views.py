import time
from flask import redirect, render_template, request, Response, url_for
import requests
from ua_parser import user_agent_parser
import werkzeug

from captiveportal import app


LINK_OPS = {
    "TEXT": "text",
    "HREF": "href",
}
# pylint: disable=invalid-name
_client_last_seen_time = {}
MAX_ASSUMED_CP_SESSION_TIME_SECS = 300
MAX_TIME_WITHOUT_SHOWING_CP_SECS = 86400  # 1 day

_android_has_acked_cp_instructions = {}


def secs_since_last_seen():
    ip_addr_str = werkzeug.wsgi.get_host(request.environ)
    last_session_start_time = \
        _client_last_seen_time.get(ip_addr_str, 0)
    return time.time() - last_session_start_time


def client_is_rejoining_network():
    """
    Checks whether this IP has gone through this CP recently

    We want to avoid bringing up the captive portal browser when a
    user rejoins the network after a short break because spamminess
    is bad, and they shouldn't need a pointer to the content (which
    is what the captive portal browser provides).

    We differentiate rejoining the network as opposed to continuing the
    same captive portal session, and we do this by saying that a rejoin
    is only happening if it's more than MAX_ASSUMED_CP_SESSION_TIME_SECS
    after the last session started
    """
    return secs_since_last_seen() < MAX_TIME_WITHOUT_SHOWING_CP_SECS and \
        secs_since_last_seen() > MAX_ASSUMED_CP_SESSION_TIME_SECS


def is_new_captive_portal_session():
    return secs_since_last_seen() > MAX_TIME_WITHOUT_SHOWING_CP_SECS

def device_requires_ok_press(ua_str):
    """
    Only some devices need an OK press to complete CP workflow

    For some devices it's a distraction, for others it does bad things
    This user agent detection is against the ua that shows the text, rather
    than one of the other UAs that performs connectivity testing

    Currently, only Android >= 6 needs an OK press.
    """
    if "Android" not in ua_str:
        return False

    user_agent = user_agent_parser.Parse(ua_str)
    # Don't assume that everything has an os.major that can be cast to an int.
    try:
        return int(user_agent["os"]["major"]) >= 6
    except (ValueError, TypeError):
        return False


def get_link_type(ua_str):
    """Return whether the device can show useable hrefs


    Lollipop (Android v5) and Marshmallow (Android v6) can render links,
     and can execute javascript but all operations keep the device
     trapped in the reduced-capability captive portal browsers and we
     don't want that, so we just show text
    """
    user_agent = user_agent_parser.Parse(ua_str)
    if user_agent["os"]["family"] == "iOS" and \
            user_agent["os"]["major"] in ("9", "11"):
        # iOS 9 and iOS 11 can open links from the captive portal browser
        #  in the system browser. iOS 10 cannot - the link opens in the
        #  captive portal browser itself.
        return LINK_OPS["HREF"]

    if user_agent["os"]["family"] == "Mac OS X" and \
            user_agent["os"]["major"] == "10" and \
       user_agent["os"]["minor"] in ("12", "13"):
        # Sierra (10.12) and High Sierra (10.13) can open links from the
        #  captive portal browser in the system browser
        return LINK_OPS["HREF"]

    return LINK_OPS["TEXT"]


def android_cpa_needs_204_now():
    """Does this captive portal agent need a 204 right now?

    We expect the user agents to go through various states before receiving
    a 204. This is particularly important for Android >= 7.1, which falls back
    to cellular if it doesn't get a 204 at the right time.
    """
    ua_str = request.headers.get("User-agent", "")
    user_agent = user_agent_parser.Parse(ua_str)
    source_ip = werkzeug.wsgi.get_host(request.environ)

    if "Android" not in ua_str:
        # We're the "X11" agent in Android 7.1+
        # Only show a 204 if the user has pressed "OK" on the CP screen
        return _android_has_acked_cp_instructions.get(source_ip, False)

    # 5.0.1 shows a confusing webpage unavailable page when Dalvik receives
    #  a 204 response after a POST, but as we never present an OK button to
    #  5.0.1 (because device_requires_ok_press never passes), we don't have
    #  to worry about a specific 5.0.1 check here.
    if "Dalvik" in ua_str:
        return _android_has_acked_cp_instructions.get(source_ip, False)

    # We're the Android Webkit agent, never send a 204
    return False


def register_client_last_seen_time():
    ip_addr_str = werkzeug.wsgi.get_host(request.environ)
    _client_last_seen_time[ip_addr_str] = time.time()


def handle_ios_macos():
    """Handle iOS and MacOS interactions
    iOS <v9 and MacOS pre-yosemite
    See: https://forum.piratebox.cc/read.php?9,8927

    iOS >= v9 and MacOS Yosemite and later:
    # pylint: disable=line-too-long
    See: https://apple.stackexchange.com/questions/45418/how-to-automatically-login-to-captive-portals-on-os-x
    """
    if client_is_rejoining_network():
        # Don't raise captive portal browser
        register_client_last_seen_time()
        return render_template("success.html")

    if is_new_captive_portal_session():
        register_client_last_seen_time()
        # raise captive portal browser by not showing success.html
        return show_connected()

    ua_str = request.headers.get("User-agent", "")
    if "CaptiveNetworkSupport" in ua_str:
        # CaptiveNetworkSupport/wispr is the captive portal agent.
        # Always show "success" after initial interaction
        return render_template("success.html")

    # We're the captive portal browser.
    # Show connected message after initial interaction
    return show_connected()

def handle_android():
    """Handle Android interactions"""
    source_ip = werkzeug.wsgi.get_host(request.environ)
    if is_new_captive_portal_session():
        # reset state in order to raise the captive portal browser
        # As >= v7.1 "X11 agent" regularly hits the generate_204
        #  endpoint, in >=7.1 the check isn't really about whether this is a
        #  new captive portal session and more about whether we haven't seen
        #  the device "recently"
        # this code path is also used by < v7.1, but it's ok to reset state
        #  for those devices too because it will still raise the cp browser
        _do_remove_client(source_ip)

    # The X11 captive portal agent periodically checks for internet access.
    # It's the only agent that hits this endpoint after the captive portal
    #  browser has been seen, and as the X11 agent doesn't detect internet
    #  access after a reconnect to the network, despite a 204. Updating the
    #  session start time means that eventually this won't been seen as an
    #  existing captive portal session and we won't send a 204, which
    #  will cause the "sign-in to wifi" sheet to come up.
    register_client_last_seen_time()

    if request.method == "POST":
        _android_has_acked_cp_instructions[source_ip] = True

    if android_cpa_needs_204_now():
        return Response(status=204)
    else:
        return show_connected()


def show_connected():
    ua_str = request.headers.get("User-agent", "")
    user_agent = user_agent_parser.Parse(ua_str)
    if user_agent["os"]["family"] == "iOS" or \
           user_agent["os"]["family"] == "Mac OS X":
        icon_type = "safari"
    else:
        icon_type = "chrome"

    browser_icon = \
        url_for('static', filename='go-animation-%s.gif' % (icon_type,))
    return render_template(
        "connected.html",
        connectbox_url="http://go",
        LINK_OPS=LINK_OPS,
        browser_icon=browser_icon,
        link_type=get_link_type(ua_str),
        show_ok=device_requires_ok_press(ua_str),
    )


def _do_remove_client(source_ip):
    if source_ip in _client_last_seen_time:
        del _client_last_seen_time[source_ip]

    if source_ip in _android_has_acked_cp_instructions:
        del _android_has_acked_cp_instructions[source_ip]


@app.route('/_authorised_clients', methods=['DELETE'])
def remove_authorised_client():
    """Forgets that a client has been seen recently to allow running tests"""
    _do_remove_client(werkzeug.wsgi.get_host(request.environ))
    return Response(status=204)


@app.route('/kindle-wifi/wifistub.html', methods=["GET", "POST"])
def handle_wifistub_html():
    # Captive Portal check for Amazon Kindle Fire
    register_client_last_seen_time()
    return show_connected()


@app.route('/ncsi.txt', methods=["GET", "POST"])
def handle_ncsi_txt():
    # Captive Portal check for Windows
    # See: https://technet.microsoft.com/en-us/library/cc766017(v=ws.10).aspx
    register_client_last_seen_time()
    return show_connected()


# Captive Portal Check for iOS <v9 and MacOS pre-yosemite
@app.route('/success.html', methods=["GET", "POST"])
def handle_early_ios_macos():
    return handle_ios_macos()

# Other iOS captive portal
@app.route('/library/test/success.html', methods=["GET", "POST"])
def handle_other_ios():
    return handle_ios_macos()

# Captive portal check for iOS >= v9 and MacOS Yosemite and later
@app.route('/hotspot-detect.html', methods=["GET", "POST"])
def handle_current_ios_macos():
    return handle_ios_macos()


# See: https://www.chromium.org/chromium-os/chromiumos-design-docs/network-portal-detection
@app.route('/generate_204', methods=["GET", "POST"])
def handle_default_android():
    return handle_android()


# Fallback method introduced in Android 7
@app.route('/gen_204', methods=["GET", "POST"])
def handle_fallback_android():
    return handle_android()

import functools
import os
import time
import unittest
import requests


def getTestTarget():
    # XXX source this properly
    return "127.0.0.1:5000"


class CaptiveportalTestCase(unittest.TestCase):

    # Something that we will find in the CP welcome page
    CAPTIVE_PORTAL_SEARCH_TEXT = \
        "<TITLE>Connected to ConnectBox Wifi</TITLE>"

    def setUp(self):
        """Simulate first connection

        Make sure the ConnectBox doesn't think the client has connected
        before, so we can test captive portal behaviour
        """
        r = requests.delete("http://%s/_authorised_clients" %
                            (getTestTarget(),))
        r.raise_for_status()

    def tearDown(self):
        """Leave system in a clean state

        Make sure the ConnectBox won't think this client has connected
        before, regardless of whether the next connection is from a
        test, or from a normal browser or captive portal connection
        """
        r = requests.delete("http://%s/_authorised_clients" %
                            (getTestTarget(),))
        r.raise_for_status()

    def testNoBaseRedirect(self):
        """A hit on the index does not redirect to ConnectBox"""
        r = requests.get("http://%s" % (getTestTarget(),),
                         allow_redirects=False)
        self.assertFalse(r.is_redirect)

    def testIOS9CaptivePortalResponse(self):
        """iOS9 ConnectBox connection workflow"""
        # 1. Device sends wispr hotspot-detect.html request
        headers = requests.utils.default_headers()
        # This is the UA from iOS 9.2.1 but let's assume it's representative
        headers.update({"User-Agent": "CaptiveNetworkSupport-325.10.1 wispr"})
        r = requests.get("http://%s/hotspot-detect.html" %
                         (getTestTarget(),), headers=headers)
        r.raise_for_status()
        # 2. We provide response that indicates no internet, causing
        #   captive portal browser to be opened
        self.assertNotIn("<BODY>\nSuccess\n</BODY>", r.text)
        # 3. Device sends regular user agent request for hotspot-detect.html
        #    to serve as contents of captive portal browser window
        headers = requests.utils.default_headers()
        headers.update({"User-Agent": "Mozilla/5.0 (iPad; CPU OS 9_2_1 like"
                        " Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko)"
                        " Mobile/13D15"})
        r = requests.get("http://%s/hotspot-detect.html" %
                         (getTestTarget(),), headers=headers)
        r.raise_for_status()
        # 4. We send a welcome page, with a link to click
        self.assertIn("<a href='http://wi.fi'", r.text)
        # 5. Device sends wispr hotspot-detect.html request
        headers = requests.utils.default_headers()
        headers.update({"User-Agent": "CaptiveNetworkSupport-325.10.1 wispr"})
        r = requests.get("http://%s/hotspot-detect.html" %
                         (getTestTarget(),), headers=headers)
        r.raise_for_status()
        # 6. We provide response that indicates an internet connection which
        #    changes captive portal browser button to "Done" and allows the
        #    user to click on the link
        self.assertIn("<BODY>\nSuccess\n</BODY>", r.text)

    def testIOS10CaptivePortalResponse(self):
        """iOS10 ConnectBox connection workflow"""
        # 1. Device sends wispr hotspot-detect.html request
        headers = requests.utils.default_headers()
        # This is the UA from iOS 10.3.1 but let's assume it's representative
        headers.update({"User-Agent": "CaptiveNetworkSupport-346.50.1 wispr"})
        r = requests.get("http://%s/hotspot-detect.html" %
                         (getTestTarget(),), headers=headers)
        r.raise_for_status()
        # 2. We provide response that indicates no internet, causing
        #   captive portal browser to be opened
        self.assertNotIn("<BODY>\nSuccess\n</BODY>", r.text)
        # 3. Device sends regular user agent request for hotspot-detect.html
        #    to serve as contents of captive portal browser window
        headers = requests.utils.default_headers()
        headers.update({"User-Agent": "Mozilla/5.0 (iPad; CPU OS 10_3_1 like"
                        " Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko)"
                        " Mobile/14E304"})
        r = requests.get("http://%s/hotspot-detect.html" %
                         (getTestTarget(),), headers=headers)
        r.raise_for_status()
        # 4. We send a welcome page, but no link because 10.3.1 doesn't allow
        #    exiting of the captive portal browser by clicking on a link. We
        #    do send a text URL for cutting and pasting
        self.assertNotIn("<a href=", r.text)
        self.assertIn("http://wi.fi", r.text)
        # 5. Device sends wispr hotspot-detect.html request
        headers = requests.utils.default_headers()
        headers.update({"User-Agent": "CaptiveNetworkSupport-346.50.1 wispr"})
        r = requests.get("http://%s/hotspot-detect.html" %
                         (getTestTarget(),), headers=headers)
        r.raise_for_status()
        # 6. We provide response that indicates an internet connection which
        #    changes captive portal browser button to "Done" and allows the
        #    user to click on the link
        self.assertIn("<BODY>\nSuccess\n</BODY>", r.text)

    def testSierraCaptivePortalResponse(self):
        """MacOS 10.12 ConnectBox connection workflow

        Expected to be the same as post yosemite"""
        # 1. Device sends wispr hotspot-detect.html request
        headers = requests.utils.default_headers()
        # This is the UA from OS 10.12.4 but let's assume it's representative
        headers.update({"User-Agent": "CaptiveNetworkSupport-346.50.1 wispr"})
        r = requests.get("http://%s/hotspot-detect.html" %
                         (getTestTarget(),), headers=headers)
        r.raise_for_status()
        # 2. Connectbox provides response that indicates no internet, causing
        #   captive portal browser to be opened
        self.assertNotIn("<BODY>\nSuccess\n</BODY>", r.text)
        # 3. Device sends regular user agent request for hotspot-detect.html
        #    to serve as contents of captive portal browser window
        headers = requests.utils.default_headers()
        headers.update({"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X"
                        " 10_12_4) AppleWebKit/603.1.30 (KHTML, like Gecko)"})
        r = requests.get("http://%s/hotspot-detect.html" %
                         (getTestTarget(),), headers=headers)
        r.raise_for_status()
        # 4. Connectbox sends a welcome page, with a link to click
        self.assertIn("<a href='http://wi.fi'", r.text)
        # 5. Device sends wispr hotspot-detect.html request
        headers = requests.utils.default_headers()
        headers.update({"User-Agent": "CaptiveNetworkSupport-346.50.1 wispr"})
        r = requests.get("http://%s/hotspot-detect.html" %
                         (getTestTarget(),), headers=headers)
        r.raise_for_status()
        # 6. Connectbox provides response that indicates an internet
        #    connection which changes captive portal browser button to "Done"
        #    and allows the user to click on the link
        self.assertIn("<BODY>\nSuccess\n</BODY>", r.text)

    def testAndroid5CaptivePortalResponse(self):
        """Android 5 ConnectBox connection workflow

        We don't advertise internet access to Android devices.
        """
        # Strictly this should be requesting
        #  http://clients3.google.com/generate_204 but answering requests for
        #  that site requires DNS mods, which can't be assumed for all
        #  people running these tests, so let's just poke for the page using
        #  the IP address of the server so we hit the default server, where
        #  this 204 redirection is active.
        # 1. Device sends generate_204 request
        headers = requests.utils.default_headers()
        # This is the UA from a Lenovo junk Android 5 tablet, but let's assume
        #  that it's representative of over Android 5 (lollipop) devices
        headers.update({"User-Agent": "Dalvik/2.1.0 (Linux; U; Android 5.0.1; "
                        "Lenovo TB3-710F Build/LRX21M)"})
        r = requests.get("http://%s/generate_204" %
                         (getTestTarget(),), headers=headers)
        r.raise_for_status()
        # 2. Connectbox replies indicating no internet access
        self.assertEqual(r.status_code, 200)
        # 3. Device send another generate_204 request within a few seconds
        r = requests.get("http://%s/generate_204" %
                         (getTestTarget(),), headers=headers)
        r.raise_for_status()
        # 4. Connectbox replies that internet access is still not available
        #    At no point do we want to provide a 204 to the captive portal
        #    agent (dalvik)
        self.assertEqual(r.status_code, 200)
        # 5. On receipt of something other than a 204, the device shows a
        #    "Sign-in to network" notification.
        #    We assume that the user responds to this notification, which
        #    causes the Android captive portal browser to send a request
        #    to the generate_204 URL
        headers.update({"User-Agent": "Mozilla/5.0 (Linux; Android 5.0.1; "
                        "Lenovo TB3-710F Build/LRX21M; wv) AppleWebKit/537.36 "
                        "(KHTML, like Gecko) Version/4.0 Chrome/45.0.2454.95 "
                        "Safari/537.36"})
        r = requests.get("http://%s/generate_204" %
                         (getTestTarget(),), headers=headers)
        r.raise_for_status()
        # 6. Connectbox provides a response with a text-URL and still
        #    indicating that internet access isn't available
        self.assertEqual(r.status_code, 200)
        self.assertIn(self.CAPTIVE_PORTAL_SEARCH_TEXT, r.text)
        # We don't want to show URLs in this captive portal browser
        self.assertNotIn("href=", r.text.lower())

    def testDhcpEndpoint(self):
        pass

    def testAndroid7FallbackCaptivePortalResponse(self):
        pass

    @unittest.skip("to be reworked to reflect 3-agent reality")
    def testAndroid8CaptivePortalResponse(self):
        """Android 8

        Android 8 devices fall back to cellular unless the CPA receives a 204
        (which must happen within ~40 seconds of the first CPA request)
        """
        cpa_ua = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 " \
                 "(KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36"
        cpb_ua = "Mozilla/5.0 (Linux; Android 8.0.0; Mi A1 " \
                 "Build/OPR1.170623.026; wv) AppleWebKit/537.36 " \
                 "(KHTML, like Gecko) Version/4.0 Chrome/67.0.3396.87 " \
                 "Mobile Safari/537.36"
        # 1. Device sends generate_204 request
        headers = requests.utils.default_headers()
        # This is the UA from a Mi A1, but let's assume that it's
        #  representative of other Android 8 (oreo) devices
        # Notice the lack of an android reference, or a dalvik reference
        #  as we had in <= v6 (and possibly v7?)
        headers.update({"User-Agent": cpa_ua})
        r = requests.get("http://%s/generate_204" %
                         (getTestTarget(),), headers=headers)
        r.raise_for_status()
        # 2. Connectbox provides response that indicates no internet to
        #    trigger raising of the captive portal browser
        self.assertEqual(r.status_code, 200)
        # 3. Captive portal browser sends the same request.
        headers.update({"User-Agent": cpb_ua})
        r = requests.get("http://%s/generate_204" %
                         (getTestTarget(),), headers=headers)
        r.raise_for_status()
        # 4. Connectbox replies that internet access is still not available
        #    but sends the connected page.
        self.assertIn(self.CAPTIVE_PORTAL_SEARCH_TEXT, r.text)
        # 5. Captive portal Agent sends the same request
        headers.update({"User-Agent": cpa_ua})
        r = requests.get("http://%s/generate_204" %
                         (getTestTarget(),), headers=headers)
        r.raise_for_status()
        # 6. Connectbox replies that internet access is available
        self.assertEqual(r.status_code, 204)
        # 7. Captive portal browser sends the same request.
        headers.update({"User-Agent": cpb_ua})
        r = requests.get("http://%s/generate_204" %
                         (getTestTarget(),), headers=headers)
        r.raise_for_status()
        # 8. Connectbox provides a response with a text-URL
        self.assertIn(self.CAPTIVE_PORTAL_SEARCH_TEXT, r.text)
        # We don't want to show URLs in this captive portal browser
        self.assertNotIn("href=", r.text.lower())

    def testAndroidShowsOkButton(self):
        """
        The OK button is required for Android7+ workflow

        We do UA parsing so that we don't show it to <= A5 clients but
        so make sure our UA logic is correct
        """
        a6_ua = "Mozilla/5.0 (Linux; Android 6.0.1; " \
                "Nexus 7 Build/MOB30X; wv) AppleWebKit/537.36 " \
                "(KHTML, like Gecko) Version/4.0 Chrome/61.0.3163.98 " \
                "Safari/537.36"
        # BLU Vivo
        a70_ua = "Mozilla/5.0 (Linux; Android 7.0; Vivo XL2 Build/NRD90M; " \
                 "wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 " \
                 "Chrome/67.0.3396.87 Mobile Safari/537.36"
        # Sony Xperia XZ
        a71_ua = "Mozilla/5.0 (Linux; Android 7.1.1; G8231 " \
                 "Build/41.2.A.0.219; wv) AppleWebKit/537.36 " \
                 "(KHTML, like Gecko) Version/4.0 Chrome/59.0.3071.125 " \
                 "Mobile Safari/537.36"
        # Xiaomi Mi A1
        a80_ua = "Mozilla/5.0 (Linux; Android 8.0.0; Mi A1 " \
                 "Build/OPR1.170623.026; wv) AppleWebKit/537.36 " \
                 "(KHTML, like Gecko) Version/4.0 Chrome/67.0.3396.87 " \
                 "Mobile Safari/537.36"
        # XXX Need an A8.1
        # Pixel 1
        a9_ua = "Mozilla/5.0 (Linux; Android 9; " \
                "Pixel Build/PPR1.180610.009; wv) AppleWebKit/537.36 " \
                "(KHTML, like Gecko) Version/4.0 Chrome/70.0.3538.64 " \
                "Mobile Safari/537.36"
        headers = requests.utils.default_headers()
        for ua in (a6_ua, a70_ua, a71_ua, a80_ua, a9_ua):
            headers.update({"User-Agent": ua})
            r = requests.get("http://%s/generate_204" %
                (getTestTarget(),), headers=headers)
            r.raise_for_status()
            self.assertIn("OK</button></form>", r.text)
        # TODO - add old android versions, showing they don't receive
        #  an OK

    def testWindowsCaptivePortalResponse(self):
        """Bounce Windows to the captive portal welcome page"""
        r = requests.get("http://%s/ncsi.txt" % (getTestTarget(),))
        r.raise_for_status()
        # Make sure we get a portal page
        self.assertEqual(r.status_code, 200)
        self.assertIn(self.CAPTIVE_PORTAL_SEARCH_TEXT, r.text)
        r = requests.get("http://%s/ncsi.txt" % (getTestTarget(),))
        r.raise_for_status()
        # Make sure we still get a portal page on this subsequent request
        self.assertEqual(r.status_code, 200)
        self.assertIn(self.CAPTIVE_PORTAL_SEARCH_TEXT, r.text)

    def testAmazonKindleFireCaptivePortalResponse(self):
        """Bounce Kindle Fire to the captive portal welcome page"""
        r = requests.get("http://%s/kindle-wifi/wifistub.html" %
                         (getTestTarget(),))
        r.raise_for_status()
        # Make sure we get a portal page
        self.assertEqual(r.status_code, 200)
        self.assertIn(self.CAPTIVE_PORTAL_SEARCH_TEXT, r.text)
        r = requests.get("http://%s/kindle-wifi/wifistub.html" %
                         (getTestTarget(),))
        r.raise_for_status()
        # Make sure we still get a portal page on this subsequent request
        self.assertEqual(r.status_code, 200)
        self.assertIn(self.CAPTIVE_PORTAL_SEARCH_TEXT, r.text)

    def testUnknownLocalPageResponse(self):
        """
        An unregistered local page hit redirects to the CP welcome page

        (and importantly, does not redirect to ConnectBox content)
        """
        r = requests.get("http://%s/unknown_local_page" % (getTestTarget(),),
                         allow_redirects=False)
        self.assertFalse(r.is_redirect)
        r.raise_for_status()
        self.assertEqual(r.status_code, 200)
        self.assertIn(self.CAPTIVE_PORTAL_SEARCH_TEXT, r.text)

    def testUnknownNonLocalPageResponse(self):
        """
        A remote page hit redirects to the CP welcome page

        (and importantly, does not redirect to ConnectBox content)
        """
        s = requests.Session()
        r = s.request(
            "GET",
            "http://%s/unknown_non_local_page" % (getTestTarget(),),
            allow_redirects=False,
            headers={"Host": "non-local-host.com"},
        )
        r.raise_for_status()
        self.assertFalse(r.is_redirect)

    def testHandleDhcpEvent(self):
        endpoint = functools.partial(
            requests.post,
           "http://%s/handle_dhcp_event" % (getTestTarget(),)
        )
        # unknown operation - be tolerant
        r = endpoint(data={"operation":"bad"})
        self.assertEqual(r.status_code, 204)
        # bad ip
        r = endpoint(data={"operation":"old", "dhcp_ip":"not.an.ip"})
        self.assertEqual(r.status_code, 400)
        # good (valid op1)
        r = endpoint(data={"operation":"old", "dhcp_ip":"1.2.3.4"})
        self.assertEqual(r.status_code, 204)


if __name__ == '__main__':
    unittest.main()

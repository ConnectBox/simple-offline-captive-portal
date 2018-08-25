Android 7.1 introduced a third captive portal user agent, the "X11" agent.

# The "X11" agent

Example user-agent: "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36"

This process is responsible for determining Internet Connectivity.
It will raise the "Sign-in to WiFi Network" sheet if it receives anything other than a 204 response for its magic URL.
If has not received a 204 response for its magic URL by the time the user is trying to use the network, the device will fallback to cellular connectivity if it has cellular connectivity
This process requests its magic URL after each action (clicking a link, submitting a form) in the captive portal browser
It will request its magic URL soon (1-60 seconds) after the user selects "Use network as-is" from the captive portal browser.

# The "Dalvik" agent

Example user-agent: "Dalvik/2.1.0 (Linux; U; Android 7.1.1; Pixel Build/NOF26V)"

This agent requests its magic URL whenever a page is loaded in the captive portal browser
Sometimes it requests its magic URL more than once each time a page is loaded in the captive portal browser
If it receives a 204 response to its magic URL, it closes the captive portal browser

# The "Android webkit" agent

Example user-agent: "Mozilla/5.0 (Linux; Android 7.1.1; Pixel Build/NOF26V; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/

This agent requests its magic URL whenever a page is loaded in the captive portal browser.
It displays the response in the captive portal browser

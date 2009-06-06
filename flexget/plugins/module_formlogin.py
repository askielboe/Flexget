import logging
from flexget.feed import Entry
from flexget.manager import PluginError
import urllib2

mechanize_present = True
try:
    from mechanize import Browser
except ImportError:
    mechanize_present = False

log = logging.getLogger('formlogin')

class InputFormLogin:
    """
    Login on form
    """

    def register(self, manager, parser):
        manager.register('form', input_priority=255)

    def feed_input(self, feed):
        if not mechanize_present:
            raise PluginError('mechanize module required.', log)
        url = feed.config['form']['url']
        username = feed.config['form']['username']
        password = feed.config['form']['password']

        br = Browser()
        br.set_handle_robots(False)
        br.open(url)

        #br.set_debug_redirects(True)
        #br.set_debug_responses(True)
        #br.set_debug_http(True)

        for form in br.forms():
            loginform = form

        loginform['username'] = username
        loginform['password'] = password

        br.form = loginform

        br.submit()

        cookiejar = br._ua_handlers["_cookies"].cookiejar

        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookiejar))
        urllib2.install_opener(opener)                                
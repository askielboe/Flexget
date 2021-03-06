from flexget.plugin import register_plugin, priority
import logging

log = logging.getLogger('details')


class PluginDetails(object):

    def __init__(self):
        # list of feed names where no entries is acceptable situation
        self.no_entries_ok = []

    @priority(-512)
    def on_feed_input(self, feed):
        if not feed.entries:
            if feed.name in self.no_entries_ok:
                log.verbose('Feed didn\'t produce any entries.')
            else:
                log.verbose('Feed didn\'t produce any entries. This is likely due to a mis-configured or non-functional input.')
        else:
            log.verbose('Produced %s entries.' % (len(feed.entries)))

    @priority(-512)
    def on_feed_download(self, feed):
        # Needs to happen as the first in download, so it runs after urlrewrites
        # and IMDB queue acceptance.
        log.verbose('Summary - Accepted: %s (Rejected: %s Undecided: %s Failed: %s)' %
            (len(feed.accepted), len(feed.rejected),
            len(feed.entries) - len(feed.accepted), len(feed.failed)))


register_plugin(PluginDetails, 'details', builtin=True)

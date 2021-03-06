import logging
import re
import urllib
import feedparser
from flexget.entry import Entry
from flexget.utils.search import torrent_availability
from flexget.plugin import PluginWarning, register_plugin

log = logging.getLogger('isohunt')


class UrlRewriteIsoHunt(object):
    """IsoHunt urlrewriter and search plugin.

    should accept: 
    isohunt: <category>
      
      categories: 
      empty or -1: All
      0 : Misc.
      1 : Video/Movies
      2 : Audio
      3 : TV
      4 : Games
      5 : Apps
      6 : Pics
      7 : Anime
      8 : Comics
      9 : Books
      10: Music Video
      11: Unclassified
      12: ALL
    """

    def validator(self):
        from flexget import validator

        root = validator.factory('choice')
        root.accept_choices(['misc', 'movies', 'audio', 'tv', 'games', 'apps', 'pics', 'anime', 'comics',
                             'books', 'music video', 'unclassified', 'all'])
        return root

    def url_rewritable(self, feed, entry):
        url = entry['url']
        # search is not supported
        if url.startswith('http://isohunt.com/torrents/?ihq='):
            return False
        # not replaceable
        if not 'torrent_details' in url:
            return False
        return url.startswith('http://isohunt.com') and url.find('download') == -1

    def url_rewrite(self, feed, entry):
        entry['url'] = entry['url'].replace('torrent_details', 'download')

    def search(self, query, comparator, config):
        # urllib.quote will crash if the unicode string has non ascii characters, so encode in utf-8 beforehand
        comparator.set_seq1(query)
        name = comparator.search_string()
        optionlist = ['misc', 'movies', 'audio', 'tv', 'games', 'apps', 'pics', 'anime', 'comics', 'books',
                      'music video', 'unclassified', 'all']
        url = 'http://isohunt.com/js/rss/%s?iht=%s&noSL' % (
        urllib.quote(name.encode('utf-8')), optionlist.index(config))

        log.debug('requesting: %s' % url)
        rss = feedparser.parse(url)
        entries = []

        status = rss.get('status', False)
        if status != 200:
            raise PluginWarning('Search result not 200 (OK), received %s' % status)

        ex = rss.get('bozo_exception', False)
        if ex:
            raise PluginWarning('Got bozo_exception (bad feed)')

        for item in rss.entries:


            # assign confidence score of how close this link is to the name you're looking for. .6 and above is "close"
            comparator.set_seq2(item.title)
            log.debug('name: %s' % comparator.a)
            log.debug('found name: %s' % comparator.b)
            log.debug('confidence: %s' % comparator.ratio())
            if not comparator.matches():
                continue

            entry = Entry()
            entry['title'] = item.title
            entry['url'] = item.link
            entry['search_ratio'] = comparator.ratio()

            m = re.search(r'Size: ([\d]+).*Seeds: (\d+).*Leechers: (\d+)', item.description, re.IGNORECASE)
            if not m:
                log.debug('regexp did not find seeds / peer data')
                continue
            else:
                log.debug('regexp found size(%s), Seeds(%s) and Leeches(%s)' % (m.group(1), m.group(2), m.group(3)))

                entry['content_size'] = int(m.group(1))
                entry['torrent_seeds'] = int(m.group(2))
                entry['torrent_leeches'] = int(m.group(3))
                entry['search_sort'] = torrent_availability(entry['torrent_seeds'], entry['torrent_leeches'])

            entries.append(entry)
        # choose torrent
        if not entries:
            raise PluginWarning('No close matches for %s' % name, log, log_once=True)

        entries.sort(reverse=True, key=lambda x: x.get('search_sort'))

        return entries

register_plugin(UrlRewriteIsoHunt, 'isohunt', groups=['urlrewriter', 'search'])

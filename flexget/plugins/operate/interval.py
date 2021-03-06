import logging
import datetime
from flexget.plugin import register_plugin, register_parser_option
from flexget.utils.tools import parse_timedelta

log = logging.getLogger('interval')


class PluginInterval(object):
    """
        Allows specifying minimum interval for feed execution.

        Format: [n] [minutes|hours|days|weeks]

        Example:

        interval: 7 days
    """

    def validator(self):
        from flexget import validator
        return validator.factory('interval')

    def on_feed_start(self, feed, config):
        if feed.manager.options.learn:
            log.info('Ignoring feed %s interval for --learn' % feed.name)
            return
        last_time = feed.simple_persistence.get('last_time')
        if not last_time:
            log.info('No previous run recorded, running now')
        elif feed.manager.options.interval_ignore:
            log.info('Ignoring interval because of --now')
        else:
            log.debug('last_time: %r' % last_time)
            log.debug('interval: %s' % config)
            next_time = last_time + parse_timedelta(config)
            log.debug('next_time: %r' % next_time)
            if datetime.datetime.now() < next_time:
                log.debug('interval not met')
                log.verbose('Interval %s not met on feed %s. Use --now to override.' % (config, feed.name))
                feed.abort(silent=True)
                return
        log.debug('interval passed')
        feed.simple_persistence['last_time'] = datetime.datetime.now()

register_plugin(PluginInterval, 'interval', api_ver=2)
register_parser_option('--now', action='store_true', dest='interval_ignore', default=False,
                       help='Ignore interval(s)')

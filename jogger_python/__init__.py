import os
import sys
import time
import traceback
import socket
import logging.handlers

from colorlog import ColoredFormatter

from .config import LoggerConfig

_logger_map = {}

#  time hostname proc_name[pid]: level [(thread\:)?file:line:column] msg
_SYSLOG_LOG_FMT = '%(levelname)s [%(threadName)s:%(module)s.py:%(lineno)d] %(message)s'
_COLOR_LOG_FMT = ('%(log_color)s[%(levelname)1.1s %(asctime)s %(threadName)s:%(module)s.py:%(lineno)d'
                 '] %(reset)s%(message)s')

_SYSLOG_FACILITY = logging.handlers.SysLogHandler.LOG_LOCAL4

_LEVEL_MAP = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warn': logging.WARN,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL,
    'fatal': logging.FATAL
}

_COLORS_MAP = {
    'DEBUG': 'blue',
    'INFO': 'green',
    'WARN': 'yellow',
    'WARNING': 'yellow',
    'ERROR': 'red',
    'CRITICAL': 'bold_red',
    'FATAL': 'bold_red',
}

# Monkey patch the logging formatter to print the full stack trace
# http://www.velocityreviews.com/forums/t717977-castrated-traceback-in-sys-exc_info.html
# - PDW
def _formatException(_, ei):
    """
    Format and return the specified exception information as a string.
    This implementation builds the complete stack trace, combining
    traceback.format_exception and traceback.format_stack.
    """
    lines = traceback.format_exception(*ei)
    if ei[2]:
        lines[1:1] = traceback.format_stack(ei[2].tb_frame.f_back)
    return ''.join(lines)

# monkey patch the logging module
logging.Formatter.formatException = _formatException

def _log_level(level):
    return _LEVEL_MAP.get(level, _LEVEL_MAP["debug"])

def _add_console(logger):
    channel = logging.StreamHandler()

    formatter = ColoredFormatter(_COLOR_LOG_FMT, datefmt="%y%m%d %H:%M:%S.", reset=True, log_colors=_COLORS_MAP)

    channel.setFormatter(formatter)
    logger.addHandler(channel)

def _add_syslog(logger, app_name, remote_host):

    hostname = socket.getfqdn().split('.')[0]
    syslog_formatter = logging.Formatter(_SYSLOG_LOG_FMT)
    channel = logging.handlers.SysLogHandler(remote_host, _SYSLOG_FACILITY, socket.SOCK_DGRAM)

    channel.ident = hostname + ' ' + app_name + '[' + str(os.getpid()) + ']:'
    channel.setFormatter(syslog_formatter)

    logger.addHandler(channel)


def create_logger(config=None):
    assert isinstance(config, LoggerConfig), "config is required and must be a valid instance of LoggerConfig"
    assert config.name not in _logger_map, "logger %s already exists" % config.name

    logger = logging.getLogger(config.name)
    logger.setLevel(_log_level(config.log_level))

    if config.remote_syslog is not None:
        _add_syslog(logger, config.name, config.remote_syslog)

    if config.log_console is True:
        _add_console(logger)

    _logger_map[config.name] = logger
    return logger

#Returns logger with specified name if it exists
def get_logger(name=''):
    if name in _logger_map:
        return _logger_map[name]
    return None

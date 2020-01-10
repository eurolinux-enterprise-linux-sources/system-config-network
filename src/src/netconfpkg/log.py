"Simple Logging Module"
#
# log.py - debugging log service
#
# Alexander Larsson <alexl@redhat.com>
# Matt Wilson <msw@redhat.com>
#
# Copyright 2002 Red Hat, Inc.
#
# This software may be freely redistributed under the terms of the GNU
# library public license.
#
# You should have received a copy of the GNU Library Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#

# FIXME: use pythons logging handlers
import sys

import logging
import syslog


class LogFile:
    "Simple Logging class"
    def __init__ (self, progname, level = 0, filename = None):        
        logging.basicConfig(level=1,
                    format='%(asctime)s %(levelname)s '
                    + progname + ' %(message)s')
                    
        self.handle_func = None
        if filename == None:
            self.syslog = syslog.openlog(progname, syslog.LOG_PID)
            self.handle_func = self.syslog_handler
            self.logfile = sys.stderr
        else:            
            self.handle_func = self.file_handler
            self.open(filename)

        self.level = level

    def handler(self, msg, level):
        "logging callback"
        if self.handle_func:
            self.handle_func(msg, level)

    def close (self):
        "close the log"
        self.logfile.close ()

    def open (self, mfile = None):
        "open the log"
        if file is str:
            logging.basicConfig(
                    filename=mfile,
                    filemode='w')
        elif mfile:
            logging.basicConfig(stream=mfile)
            self.logfile = mfile
        else:
            logging.basicConfig(stream=sys.stderr)

    def get_file (self):
        "get the file fd"
        return self.logfile.fileno ()

    def __call__(self, format, *args):
        "if you call the class object"
        self.handler(format % args)

    def file_handler (self, *args, **kwargs):
        "file logging callback"
        msg = args[0]
        level = kwargs.get("level", 1)
        #level = logging.CRITICAL - level * 10
        if level == 1:
            level = logging.INFO
        elif level == 2:
            level = logging.INFO
        elif level >= 3:
            level = logging.DEBUG - level + 3
        if level <= 0:
            level = 1
        if level <= 0:
            level = 1
        logging.log(level, msg)
        #self.logfile.write ("[%d] %s: %s\n" % (level, time.ctime(), msg))

    def syslog_handler (self, *args, **kwargs):
        "syslog logging callback"
        msg = args[0]
        level = kwargs.get("level", 1)
        syslog.syslog(level, msg)

    def set_loglevel(self, level):
        "set the preferred loglevel"
        self.level = level

    def log(self, level, message):
        "log a normal message"
        if self.level >= level:
            self.handler(message, level = level)

    def ladd(self, level, mfile, message):
        "log an add message"
        if self.level >= level:
            self.handler("++ %s \t%s" % (mfile, message))

    def ldel(self, level, mfile, message):
        "log a del message"
        if self.level >= level:
            self.handler("-- %s \t%s" % (mfile, message))

    def lch(self, level, mfile, message):
        "log a change message"
        if self.level >= level:
            self.handler("-+ %s \t%s" % (mfile, message))


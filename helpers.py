#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Written by Lasse Karstensen <lasse.karstensen@gmail.com>, 2008.
# Released under GPLv2 at http://hyse.org/irssi-log-merge/
#
# Modified by Nikita Marchant <nikita.marchant@gmail.com>, 2014
# Released under GPLv3 at http://github.com/C4ptainCrunCh/irssi_utils.py

import time

def handle_charset(bytestr):
    # http://evanjones.ca/python-utf8.html
    # let's just assume utf8 first, and change it into latin1
    # if there is any sign of it.
    charset = 'utf-8'
    # search for latin-1 bytes of norwegian ae, oe, aa.
    # lower first, then upper case.
    #latin1chars = ['\xe6','\xf8','\xe5','\xc6','\xd8','\xc5']
    # from the list at
    # http://en.wikipedia.org/wiki/ISO/IEC_8859-1#ISO-8859-1
    # the chars from 160-255 are pretty much printable.

    # handle_charset() is called very many times during
    # execution. Expanding the list to keep chr() from being
    # run a few hundred thousand times.
    # latin1chars = [ chr(x) for x in range(160,255+1) ]
    latin1chars = ['\xa0', '\xa1', '\xa2', '\xa3', '\xa4', '\xa5', '\xa6',
    '\xa7', '\xa8', '\xa9', '\xaa', '\xab', '\xac', '\xad',
    '\xae', '\xaf', '\xb0', '\xb1', '\xb2', '\xb3', '\xb4',
    '\xb5', '\xb6', '\xb7', '\xb8', '\xb9', '\xba', '\xbb',
    '\xbc', '\xbd', '\xbe', '\xbf', '\xc0', '\xc1', '\xc2',
    '\xc3', '\xc4', '\xc5', '\xc6', '\xc7', '\xc8', '\xc9',
    '\xca', '\xcb', '\xcc', '\xcd', '\xce', '\xcf', '\xd0',
    '\xd1', '\xd2', '\xd3', '\xd4', '\xd5', '\xd6', '\xd7',
    '\xd8', '\xd9', '\xda', '\xdb', '\xdc', '\xdd', '\xde',
    '\xdf', '\xe0', '\xe1', '\xe2', '\xe3', '\xe4', '\xe5',
    '\xe6', '\xe7', '\xe8', '\xe9', '\xea', '\xeb', '\xec',
    '\xed', '\xee', '\xef', '\xf0', '\xf1', '\xf2', '\xf3',
    '\xf4', '\xf5', '\xf6', '\xf7', '\xf8', '\xf9', '\xfa',
    '\xfb', '\xfc', '\xfd', '\xfe', '\xff']

    for char in latin1chars:
        # used to prefix common utf-8 double-byte chars.
        if char == '\xc3':
            continue
        if char in bytestr:
            found_at = bytestr.find(char)
            if bytestr[found_at - 1] == '\xc3':
                # neitakk
                continue
            #print "%s (%s) found at %i" % (char, hex(ord(char)), bytestr.find(char))
            charset = 'latin-1'
            break

    # urk. minor hardcoded hack.
    bytestr = bytestr.replace("\xc3\x65", "\x65")

    try:
        bytestr = bytestr.decode(charset, 'replace')
    except Exception as e:
        print(dump(bytestr))
        print("handle_charset: {}".format(e))
        raise Exception
    return bytestr


# following three procedures are stolen from
# http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/142812 Jack
# Trainor 2008
""" dump any string to formatted hex output """
def dump(s):
    import types
    if type(s) == types.StringType:
        return dumpString(s)
    elif type(s) == types.UnicodeType:
        return dumpUnicodeString(s)

#FILTER = ''.join([(len(repr(chr(x))) == 3) and chr(x) or '.' for x in range(256)])

""" dump any string, ascii or encoded, to formatted hex output """
def dumpString(src, length=16):
    result = []
    for i in xrange(0, len(src), length):
       chars = src[i:i+length]
       hex = ' '.join(["%02x" % ord(x) for x in chars])
       printable = ''.join(["%s" % ((ord(x) <= 127 and FILTER[ord(x)]) or '.') for x in chars])
       result.append("%04x  %-*s  %s\n" % (i, length*3, hex, printable))
    return ''.join(result)

""" dump unicode string to formatted hex output """
def dumpUnicodeString(src, length=8):
    result = []
    for i in xrange(0, len(src), length):
       unichars = src[i:i+length]
       hex = ' '.join(["%04x" % ord(x) for x in unichars])
       printable = ''.join(["%s" % ((ord(x) <= 127 and FILTER[ord(x)]) or '.') for x in unichars])
       result.append("%04x  %-*s  %s\n" % (i*2, length*5, hex, printable))
    return ''.join(result)

def parse_timestamp(timestring):
    # from http://www.python.org/doc/2.5.2/lib/node745.html :
    # .. If, when coding a module for general use, you need a locale
    # independent version of an operation that is affected by the
    # locale (such as string.lower(), or certain formats used with
    # time.strftime()), you will have to find a way to do it without
    # using the standard library routine. Even better is convincing
    # yourself that using locale settings is okay. Only as a last
    # resort should you document that your module is not compatible
    # with non-"C" locale settings.
    #
    # So, here we go. :(
    # --- Log opened Tue Mar 28 21:17:38 2006
    # datetime(year, month, day[, hour[, minute[, second[, microsecond[,tzinfo]]]]])
    # en: Sun Oct 15 23:58:13 2006
    # >>> time.strftime("%a %b %d %H:%M:%S %Y", time.localtime())
    # 'Mon Nov 17 17:47:16 2008'
    # 'tor mar 29 13:16:47 2007' - norwegian day names used. replace
    # enough so that strptime can recognize it as english.
    #
    # TODO: We have the month, the year and the date. We don't need
    # to bother transforming and parsing the day name, as it is a
    # function of the mentioned three. Remove it some time.
    tdata = """
# notation hell. format: tovalue = from1,from2..
mon = man, ma.
tue = tir, ti.
wed = ons, on.
thu = tor, to.
fri = fre, fr.
# latin-1
#sat = lør
#sun = søn
#sat = l\xf8r, l\xf8.
#sun = s\xf8n, s\xf8.
sat = lør, lø.
sun = søn, sø.
#, s\xc3\xb8n
#
apr = april
may = mai
jun = juni, jun.
jul = juli, jul.
aug = aug.
sep = sep.
oct = oct., okt, okt.
nov = nov.
dec = des"""
    format  = '%a %b %d %H:%M:%S %Y'
    transforms = {}
    for t in tdata.split("\n"):
        if len(t) == 0:
            continue
        if t[0] == "#":
            continue

        (tovalue, keys) = t.split("=", 1)
        if not "," in keys:
            keys = [ keys ]
        else:
            keys = keys.split(",")

        for key in keys:
            key = unicode(key, 'utf-8')
            transforms[ key.strip() + " " ] = tovalue.strip() + " "
    s = None

    for fromkey, tovalue in transforms.items():
        #print fromkey, tovalue
        i = timestring.find(fromkey)
        if i > -1:
            #print "performing transform %s->%s" % (fromkey, tovalue)
            timestring = timestring.replace(fromkey, tovalue)

    s = time.strptime(timestring, format)
    return s

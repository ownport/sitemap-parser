#!/usr/bin/env python
#
#   Python script for parsing sitemaps and sitemap indexes
#
#
#   TODO use SitemapParser as generator


__author__  = 'Andrey Usov <https://github.com/ownport/sitemap-parser>'
__version__ = '0.1'

import urllib2

from gzip import GzipFile 
from cStringIO import StringIO

try:
    import xml.etree.cElementTree as xml_parser
except ImportError:
    import xml.etree.ElementTree as xml_parser

DEFAULT_USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) sitemap-parser/{}'.format(__version__)

NAMESPACES = (
    '{http://www.google.com/schemas/sitemap/0.84}',
    '{http://www.google.com/schemas/sitemap/0.9}',
    '{http://www.sitemaps.org/schemas/sitemap/0.9}',
)

# Entity escape
# 
# Character	            Escape Code
# ---------------------+-----------
# Ampersand(&)	        &amp;
# Single Quote (')      &apos;
# Double Quote (")	    &quot;
# Greater Than (>)	    &gt;
# Less Than	(<)	        &lt;

# -----------------------------------------------
#   SitemapParser
# -----------------------------------------------
class SitemapParser(object):
    
    def __init__(self, proxies={}, debug=False):
        ''' init 

        Cause requests to go through a proxy. If proxies is given, it 
        must be a dictionary mapping protocol names to URLs of proxies. 
        The default is to read the list of proxies from the environment 
        variables <protocol>_proxy. If no proxy environment variables 
        are set, in a Windows environment, proxy settings are obtained 
        from the registry's Internet Settings section and in a Mac OS X 
        environment, proxy information is retrieved from the OS X System 
        Configuration Framework. To disable autodetected proxy pass an 
        empty dictionary.
        
        '''
        self._proxies = proxies
        self._debug = debug

        self._urls = list()
        self._sitemap_urls = list()
        
    @staticmethod
    def _plain_tag(tag):
        ''' remove namespaces and returns tag '''

        for namespace in NAMESPACES:
            if tag.find(namespace) >= 0:
                return tag.replace(namespace,'')
        return tag

    def _get(self, url):
        ''' get sitemap, if it compressed -> decompress'''
        SUPPORTED_PLAIN_CONTENT_TYPE = (
            'text/xml', 'application/xml',
        )
        SUPPORTED_COMPESSED_CONTENT_TYPE = (
            'application/octet-stream', 'application/x-gzip',
        )

        proxy = urllib2.ProxyHandler(self._proxies)
        opener = urllib2.build_opener(proxy)
        urllib2.install_opener(opener)        

        req = urllib2.Request(url, headers={'User-Agent': DEFAULT_USER_AGENT})
        try:
            resp = urllib2.urlopen(req)
        except urllib2.URLError, err:
            raise RuntimeError(err)
        
        if resp.code == 200:
            content_type = resp.headers['content-type'].lower()
            if ';' in content_type:
                content_type = content_type.split(';')[0]
            if content_type in SUPPORTED_PLAIN_CONTENT_TYPE:
                return resp.read()
            elif content_type in SUPPORTED_COMPESSED_CONTENT_TYPE:
                return GzipFile(fileobj=StringIO(resp.read())).read()
        return None
                    
    def parse_string(self, sitemap):
        ''' parse sitemap from string 
        
        parse sitemap if there's urlset, returns the list of url details:
        loc (required), lastmod (optional), changefreq (optional), priority (optional) '''

        root = xml_parser.fromstring(sitemap)
        
        if self._plain_tag(root.tag) == 'sitemapindex':
            for sitemap in root:
                url = dict([(self._plain_tag(param.tag), param.text) for param in sitemap])
                self._sitemap_urls.append(url['loc'])

        if self._plain_tag(root.tag) == 'urlset':
            for url in root:
                url = dict([(self._plain_tag(param.tag), param.text) for param in url])
                yield url

    def parse_url(self, sitemap_url):
        ''' parse sitemap from url'''
        self._sitemap_urls.append(sitemap_url)
        
        while True:
            try:
               sm_url = self._sitemap_urls.pop()
            except IndexError:
                break
                        
            sm_content = self._get(sm_url)
            if sm_content:
                for url in self.parse_string(sm_content):
                    yield sm_url, url
    
    def parse_file(self, sitemap_file):
        ''' parse sitemap from file '''
        pass


if __name__ == '__main__':
    
    import argparse
    argparser = argparse.ArgumentParser(description='sitemap-parser')
    argparser.add_argument('-u', '--url', help='sitemap url')
    argparser.add_argument('-p', '--path', help='path to sitemap file')
    argparser.add_argument('-d', '--debug', action='store_true', help='activate debug')
    
    args = argparser.parse_args()
    
    parser = SitemapParser(debug=args.debug)
    if args.url:
        for url in parser.parse_url(args.url):
            print url
    elif args.path:
        for url in parser.parse_file(args.path):
            print url
    else:
        argparser.print_help()



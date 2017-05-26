#!/usr/bin/env python
import argparse, httplib2
import threading

import sys
from bs4 import BeautifulSoup, SoupStrainer
from urlparse import urlparse


def parse_href(link, base_url):
    if link['href'] != "#" and link['href'] != "/" and "javascript" not in \
            link['href'] and "mailto:" not in link['href']:
        link_found = None
        if (link['href'].startswith(base_url.scheme)):
            link_found = urlparse(link['href'])
        else:
            if link['href'].startswith("/"):
                link_found = urlparse(base_url.scheme + "://" + base_url.netloc + link['href'])
            else:
                if link['href'].startswith("http"):
                    link_found = urlparse(link['href'])
                else:
                    path = base_url.geturl().split("/")
                    link_found = urlparse(base_url.geturl().replace(path[len(path) - 1], "") + link['href'])
        if link_found:
            return link_found
    return None


def get_links(base, url):
    links = []
    if base.netloc == url.netloc:
        try:
            http = httplib2.Http(disable_ssl_certificate_validation=True)
            status, response = http.request(url.geturl())
            if status.status == 200 and "image" not in status['content-type']:
                for link in BeautifulSoup(response, "html.parser", parse_only=SoupStrainer('a')):
                    if link.has_attr('href'):
                        try:
                            link = parse_href(link, base)
                        except:
                            pass
                        if link:
                            links.append(link)
        except:
            pass
    return links


def worker(base, url, crawled):
    for link in get_links(base, url):
        if link not in crawled:
            crawled.append(link)
            threading.Thread(target=worker, args=(base, urlparse(link.geturl()), crawled,)).start()
            sys.stdout.write(link.geturl() + "\n")
            sys.stdout.flush()
    return


if __name__ == '__main__':
    crawled = []
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", help="The URL to scan.")
    args = parser.parse_args()
    if args.url:
        base_url = urlparse(args.url)
        base = []
        for link in get_links(base_url, base_url):
            base.append(link)
        for url in base:
            threading.Thread(target=worker, args=(base_url, url, crawled,)).start()

#!/usr/bin/env python
import random
import urlclustering


def pprint(clusters):
    for key, urls in clusters.iteritems():
        print 'REGEX:', key[0]
        print 'HUMAN:', key[1]
        print 'URLS:'
        print '\t' + '\n\t'.join(urls) + '\n'

urls = [
    u'http://example.com',
    u'http://example.com/about',
]
cats = [u'http://example.com/cat/%s' % x
        for x in ('sports', 'tech', 'life', 'politics', 'world')]
tags = [u'http://example.com/tag/%s/tag%s' % (random.randint(100, 999), x)
        for x in xrange(10)]
arts = [u'http://example.com/article/?id=%s' % x for x in xrange(10)]

c = urlclustering.cluster(urls + cats + tags + arts, 5)

pprint(c['clusters'])
print 'UNCLUSTERED:'
print '\t' + '\n\t'.join(c['unclustered'])

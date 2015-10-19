#!/usr/bin/env python
from __future__ import unicode_literals
from urlclustering.urlclusterer import cluster_urls
from urlclustering.reimprover import improve_patterns, _str_reduce
import unittest


class TestUrlClusterer(unittest.TestCase):

    def test_single_cluster(self):
        urls = ['http://s.com/blah/%d' % x for x in range(1, 20)]
        c = cluster_urls(urls, 10)
        self.assertEqual(c['unclustered'], [])
        self.assertEqual(
            sorted(c['clusters'].keys()),
            sorted([('http://s.com/blah/(\\d+)',
                     'http://s.com/blah/[NUMBER]')]))
        self.assertEqual(
            sorted(c['clusters'].values()), sorted([urls]))

    def test_mixed(self):
        c_urls = ['http://s.com/blah/?id=%d' % x for x in range(1, 20)]
        u_urls = ['http://s.com/asdf', 'http://s.com/a/a/b']
        c = cluster_urls(c_urls + u_urls, 10)
        self.assertEqual(sorted(c['unclustered']), sorted(u_urls))
        self.assertEqual(
            sorted(c['clusters'].keys()),
            sorted([('http://s.com/blah/?\\?id=(\\d+)',
                     'http://s.com/blah?id=[NUMBER]')]))
        self.assertEqual(
            sorted(c['clusters'].values()), sorted([c_urls]))

    def test_other(self):
        x_urls = ['http://s.com/blah/%d' % x for x in range(1, 20)]
        y_urls = ['http://s.com/a/b/aa%dbb' % x for x in range(1, 20)]
        z_urls = ['http://b.com/ab/aa%dbb' % x for x in range(1, 50)]
        c = cluster_urls(x_urls + y_urls + z_urls, 10)
        improve_patterns(c['clusters'])
        self.assertEqual(c['unclustered'], [])
        self.assertEqual(
            sorted(c['clusters'].keys()),
            sorted([('http://b.com/ab/aa([^/]+)bb',
                     'http://b.com/ab/aa[...]bb'),
                    ('http://s.com/blah/(\\d+)',
                     'http://s.com/blah/[NUMBER]'),
                    ('http://s.com/a/b/aa([^/]+)bb',
                     'http://s.com/a/b/aa[...]bb')]))

    def test_lazy_str_reduce(self):
        return
        strings = ['abc123asdf', 'abc1234asdf', 'abc234asdf']
        self.assertEqual(_str_reduce(strings, '(.*)', '[...]'),
                         ('abc(.*)asdf', 'abc[...]asdf'))

    def test_lazy_str_reduce_other(self):
        return
        strings = ['1abc123asdf3', '2abc1234asdf4', '3abc234asdf5']
        self.assertEqual(_str_reduce(strings, '(.*)', '[...]'),
                         ('(.*)', '[...]'))

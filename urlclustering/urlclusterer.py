import re
from collections import defaultdict
from urlclustering.urltree import URLTreeNode
from urlclustering.parsedurl import ParsedURL

"""
This package facilitates the clustering of similar URLs.

How it works:
-------------
URLs are grouped by domain. Only same domain URLs are clustered.

URLs are then grouped by a signature which is the number of path elements
and the number of QueryString parameters & values the URL has.
Examples:
http://ex.com/about has a signature of (1, 0)
http://ex.com/article?123 has a signature of (1, 1)
http://ex.com/path/to/file?par1=val1&par2=val2 has a signature of (3, 4)

URLs with the same signature are inserted in a tree structure. For
each part (path element or QS parameter or QS value) two nodes are created:
- One with the verbatim part.
- One with the reduced part i.e. a regex that could replace the part.
Leaf nodes hold the number of URLs that match and the number of reductions.

E.g. inserting URL `http://ex.com/article?123` will create 2 top nodes:
    root 1: `article`
    root 2: `[^/]+`
And each top node will have two children:
    child 1: `123`
    child 2: `\d+`
Inserting 3 URLs of the form `/article/[0-9]+` would lead to a tree like this:

           `article`                        `[^/]+`
      /    /      \     \             /    /      \     \
  `123`  `456`  `789`  `\d+`      `123`  `456`  `789`  `\d+`
  1 URL  1 URL  1 URL  3 URLs     1 URL  1 URL  1 URL  3 URLs
  0 re   0 re   0 re   1 re       1 re   1 re   1 re   2  re

The final step is to choose the best leafs. In this case `article` -> `\d+`
is best because it macthes all 3 URLs with 1 reduction so the cluster returned
is http://ex.com/article?(\d+)
"""


def _cluster_same_signature_urls(parsed_urls, min_cluster_size):
    """
    Returns patterns matching >=min_cluster_size urls in best -> worst order.
    List of URLs must have the same signature (path + QS elements).
    """
    patterns = []
    if len(parsed_urls) == 0:
        return patterns
    max_reductions = len(parsed_urls[0].parts)

    # build our URL tree
    root = URLTreeNode()
    for parsed in parsed_urls:
        root.add_url(parsed)

    # reduce leafs by removing the best one at each iteration
    leafs = root.leafs()
    while leafs:
        bestleaf = max(
            leafs,
            key=lambda x:
                len(x['urls']) * (max_reductions - x['reductions']) ** 2
        )
        if len(bestleaf['urls']) >= min_cluster_size:
            patterns.append((bestleaf['pattern'],
                             bestleaf['h_pattern']))
        leafs.remove(bestleaf)
        remaining_leafs = []
        for leaf in leafs:
            leaf['urls'] -= bestleaf['urls']
            if leaf['urls']:
                remaining_leafs.append(leaf)
        leafs = remaining_leafs

    return patterns


def _cluster_same_domain_urls(parsed_urls, min_cluster_size):
    """Returns clusters and a list of unclustered urls."""

    # group URLs by signature
    url_map = defaultdict(list)
    for parsed in parsed_urls:
        url_map[parsed.signature].append(parsed)

    # build clusters
    clusters = defaultdict(list)
    unclustered = []
    for parsed_urls in url_map.itervalues():
        if len(parsed_urls) < min_cluster_size:
            unclustered.extend([x.url for x in parsed_urls])
            continue
        patterns = _cluster_same_signature_urls(parsed_urls, min_cluster_size)
        for (pattern, h_pattern) in patterns:
            remaining_urls = []
            # add matching URLs to cluster and remove from remaining URLs
            for parsed in parsed_urls:
                if re.search(pattern, parsed.url):
                    clusters[(pattern, h_pattern)].append(parsed.url)
                else:
                    remaining_urls.append(parsed)
            parsed_urls = remaining_urls

        # everything left goes to unclustered
        unclustered.extend(x.url for x in parsed_urls)

    return {'clusters': clusters, 'unclustered': unclustered}


def cluster_urls(urls, min_cluster_size=10):
    if min_cluster_size < 2:
        min_cluster_size = 2
    res = {'clusters': {}, 'unclustered': []}

    # get ParsedURL objects for each url
    parsed_urls = []
    for url in urls:
        parsed_urls.append(ParsedURL(url))

    # group urls by domain
    by_domain = defaultdict(list)
    for parsed in parsed_urls:
        try:
            by_domain[parsed.domain].append(parsed)
        except:
            res['unclustered'].append(parsed.url)

    # cluster in each domain group
    for domain, parsed_urls in by_domain.iteritems():
        c_res = _cluster_same_domain_urls(parsed_urls, min_cluster_size)
        res['clusters'].update({('%s%s' % (domain, k[0]),
                                 '%s%s' % (domain, k[1])): v
                                for k, v in c_res['clusters'].iteritems()})
        res['unclustered'].extend(c_res['unclustered'])

    return res

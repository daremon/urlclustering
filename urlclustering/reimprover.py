import re
from urlclustering.urltree import URLTreeNode

"""
Work in progress - enter at your own risk :)

The idea is to improve a regex for a specific set of urls
e.g. for these URLs
    /path/to/thumb_dog.jpg
    /path/to/thumb_cat.jpg
    /path/to/thumb_hen.jpg
we currently get
    /path/to/([^/]+)
but we can also get
    /path/to/thumb_([^/]+).jpg
"""


def _str_reduce(strings, pattern, h_pattern):
    """
    Reduces the given strings to a regexp by extracting the
    commong prefix and suffix
    """
    prefix = u''
    for ix in range(1, len(strings[0])):
        prefix = strings[0][:ix]
        matching = len(strings) == len(filter(lambda x: x[:ix] == prefix,
                                              strings))
        if not matching:
            prefix = strings[0][:ix-1]
            break

    suffix = u''
    for ix in range(1, len(strings[0]) - len(prefix)):
        suffix = strings[0][-ix:]
        matching = len(strings) == len(filter(lambda x: x[-ix:] == suffix,
                                              strings))
        if not matching:
            if ix > 1:
                suffix = strings[0][-(ix-1):]
            else:
                suffix = u''
            break

    return (u"%s%s%s" % (prefix, pattern, suffix),
            u"%s%s%s" % (prefix, h_pattern, suffix))


def _improve_cluster_pattern(cluster_key, urls):
    """
    Improve regex to use maximum literals and minimum metacharacters.
    All urls must be matched.
    """
    pattern, h_pattern = cluster_key
    pattern_parsed = []
    h_pattern_parsed = []
    cur_pattern = pattern
    cur_h_pattern = h_pattern
    while True:
        if cur_pattern == '':
            break
        p = re.search(r'^(.*?)((%s)|(%s))(.*)$' % (
            re.escape(URLTreeNode.REDUCED_PATH_LITERAL),
            re.escape(URLTreeNode.REDUCED_PARAM_LITERAL)), cur_pattern)
        h_p = re.search(r'^(.*?)(\[\.\.\.\])(.*)$', cur_h_pattern)
        if not p:
            if cur_pattern != '':
                pattern_parsed.append(cur_pattern)
                h_pattern_parsed.append(cur_h_pattern)
            break
        if p.group(1) != '':
            pattern_parsed.append(p.group(1))
            h_pattern_parsed.append(h_p.group(1))
        pattern_parsed.append(p.group(2))
        h_pattern_parsed.append(h_p.group(2))
        cur_pattern = p.group(5)
        cur_h_pattern = h_p.group(3)

    group = 0
    matches = [re.search(pattern, url) for url in urls]
    improved_pattern = u''
    improved_h_pattern = u''
    for ix in range(0, len(pattern_parsed)):
        if (pattern_parsed[ix] !=
            URLTreeNode.REDUCED_PATH_LITERAL and
            pattern_parsed[ix] !=
                URLTreeNode.REDUCED_PARAM_LITERAL):
            improved_pattern += pattern_parsed[ix]
            improved_h_pattern += h_pattern_parsed[ix]
            continue
        group += 1
        reduced_strings = [m.group(group) for m in matches]
        improved = _str_reduce(
            reduced_strings, pattern_parsed[ix], h_pattern_parsed[ix])
        improved_pattern += improved[0]
        improved_h_pattern += improved[1]

    return (improved_pattern, improved_h_pattern)


def improve_patterns(clusters):
    for key in clusters.iterkeys():
        improved = _improve_cluster_pattern(key, clusters[key])
        if improved != key:
            clusters[improved] = clusters[key]
            del clusters[key]

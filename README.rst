urlclustering
=============

This package facilitates the clustering of similar URLs of a website.

**Live demo**: http://urlclustering.com

General information
~~~~~~~~~~~~~~~~~~~

You give a (preferably long and complete) list of URLs as input e.g.:

::

    urls = [
        'http://example.com',
        'http://example.com/about',
        'http://example.com/contact',

        'http://example.com/cat/sports',
        'http://example.com/cat/tech',
        'http://example.com/cat/life',
        'http://example.com/cat/politics',

        'http://example.com/tag/623/tag1',
        'http://example.com/tag/335/tag2',
        'http://example.com/tag/671/tag3',

        'http://example.com/article/?id=1',
        'http://example.com/article/?id=2',
        'http://example.com/article/?id=3',
    ]

You get a list of clusters as a result. For each cluster you get:

-  a REGEX that matches all cluster URLs
-  a HUMAN readable string representing the cluster
-  a list with all matched cluster URLs

So for our example the result is:

::

    REGEX: http://example.com/cat/([^/]+)
    HUMAN: http://example.com/cat/[...]
    URLS:
        http://example.com/cat/sports
        http://example.com/cat/tech
        http://example.com/cat/life
        http://example.com/cat/politics

    REGEX: http://example.com/tag/(\d+)/([^/]+)
    HUMAN: http://example.com/tag/[NUMBER]/[...]
    URLS:
        http://example.com/tag/623/tag1
        http://example.com/tag/335/tag2
        http://example.com/tag/671/tag3

    REGEX: http://example.com/article/?\?id=(\d+)
    HUMAN: http://example.com/article?id=[NUMBER]
    URLS:
        http://example.com/article/?id=1
        http://example.com/article/?id=2
        http://example.com/article/?id=3

    UNCLUSTERED URLS:
        http://example.com
        http://example.com/about
        http://example.com/contact

When to use
~~~~~~~~~~~

This is most useful for website analysis tools that report findings to
the user. E.g. a service that crawls your website and reports page
loading time may find that 10,000 pages take >2 seconds to load. Instead
of listing 10,000 URLs it's better to cluster them. So the end user will
see something like:

::

    Slow pages (>2 secs):
    - http://example.com/                             (1 URL)
    - http://example.com/sitemap                      (1 URL)
    - http://example.com/search?q=[...]               (578 URLs)
    - http://example.com/tags?tag1=[...]&tag2=[...]   (409 URLs)
    - http://example.com/article?id=[NUMBER]          (7209 URLs)

How it works:
~~~~~~~~~~~~~

URLs are grouped by domain. Only same domain URLs are clustered.

URLs are then grouped by a signature which is the number of path
elements and the number of QueryString parameters & values the URL has.

Examples:

-  http://ex.com/about has a signature of (1, 0)
-  http://ex.com/article?123 has a signature of (1, 1)
-  http://ex.com/path/to/file?par1=val1&par2=val2 has a signature of (3,4)

URLs with the same signature are inserted in a tree structure. For each
part (path element or QS parameter or QS value) two nodes are created:

-  One with the verbatim part.
-  One with the reduced part i.e. a regex that could replace the part.

Leaf nodes hold the number of URLs that match and the number of
reductions.

E.g. inserting URL ``http://ex.com/article?123`` will create 2 top
nodes:

::

    root 1: `article`
    root 2: `[^/]+`

And each top node will have two children:

::

    child 1: `123`
    child 2: `\d+`

Inserting 3 URLs of the form ``/article/[0-9]+`` would lead to a tree
like this:

::

           `article`                        `[^/]+`
      /    /      \     \             /    /      \     \
    `123`  `456`  `789`  `\d+`      `123`  `456`  `789`  `\d+`
    1 URL  1 URL  1 URL  3 URLs     1 URL  1 URL  1 URL  3 URLs
    0 re   0 re   0 re   1 re       1 re   1 re   1 re   2  re

The final step is to choose the best leafs. In this case ``article`` ->
``\d+`` is best because it macthes all 3 URLs with 1 reduction so the
cluster returned is http://ex.com/article/[NUMBER]

License
~~~~~~~

Copyright (c) 2015 Dimitris Giannitsaros.

Licensed under the MIT License.

from urlclusterer import cluster_urls


def cluster(urls, min_cluster_size=10):
    return cluster_urls(urls, min_cluster_size)

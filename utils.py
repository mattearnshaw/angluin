import collections

def recursive_keys(d):
    for key, value in d.items():
        if type(value) is dict:
            yield from recursive_keys(value)
        else:
            yield key

def groupby_unsorted(seq, key):
    indexes = collections.defaultdict(list)
    for i, elem in enumerate(seq):
        indexes[key(elem)].append(i)
    for k, idxs in indexes.items():
        yield k, (seq[i] for i in idxs)

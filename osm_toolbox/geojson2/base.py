def deepCopy(ds):
    '''
    makes a copy of listlike and dictlike ds ignoring additional attributes
    '''
    if isinstance(ds, list):
        return [deepCopy(i) for i in ds]
    elif isinstance(ds, dict):
        return {k: deepCopy(v) for k, v in ds.items()}
    # otherwise directly pass
    return ds
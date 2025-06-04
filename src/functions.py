def flattenDictionary(d: dict, parent_key: str = '', sep: str = '-') -> dict:
    flat_dict = {}

    def recurse(subdict, top_key):
        if isinstance(subdict, dict):
            for k, v in subdict.items():
                if isinstance(v, dict):
                    recurse(v, top_key)
                else:
                    flat_key = f"{top_key}{sep}{k}"
                    flat_dict[flat_key] = v
        else:
            flat_dict[top_key] = subdict

    for key, value in d.items():
        if isinstance(value, dict):
            recurse(value, key)
        else:
            flat_dict[key] = value

    return flat_dict

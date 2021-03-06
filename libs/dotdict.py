# -*- coding: utf-8 -*-


class DotDict(dict):
    """Make attribute-style dict. 

    It allows dict.key to paly with the item.
    """

    def __getattr__(self, key):
        return self[key]

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError as k:
            raise AttributeError(k)

    def __repr__(self):
        return '<DotDict ' + dict.__repr__(self) + '>'

    def __getstate__(self):
        return dict(self)

    def __setstate__(self, value):
        for (k, v) in list(value.items()):
            self[k] = v


if __name__ == '__main__':
    a = DotDict(name='test')
    print(a, type(a))
    print(isinstance(a, dict))
    b = dict(a)
    print(b, type(b))


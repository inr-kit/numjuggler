from __future__ import print_function, absolute_import, division

import string


def make_label(item):
    return '{' + item + '}'


class PartialFormatter(string.Formatter):

    def __init__(self, on_missing=make_label, on_bad_fmt=None):
        self.on_missing, self.on_bad_fmt = on_missing, on_bad_fmt

    def get_field(self, field_name, args, kwargs):
        # Handle a key not found
        try:
            val = super(PartialFormatter, self).get_field(field_name, args, kwargs)
            # Python 3, 'super().get_field(field_name, args, kwargs)' works
        except (KeyError, AttributeError):
            val = self.on_missing(field_name), field_name
        return val

    def format_field(self, value, spec):
        # handle an invalid format
        if value is None:
            return self.on_missing(spec)
        try:
            return super(PartialFormatter, self).format_field(value, spec)
        except ValueError:
            if self.bad_fmt is not None:
                return self.on_bad_fmt(spec)
            else:
                raise

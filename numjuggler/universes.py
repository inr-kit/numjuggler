"""
Representation of universe structure of the input files.
"""

class Cells(dict):
    """
    Cells is a set of cells stored in a dictionary. Keyas are cell names, values -- tuples of cell properties.

    This class adds some methods to the original dict type.

    Validity of keys and values is not cheked, but assumed by the added methods. Each key must be a positive integer.
    Each value must be a tuple (u, fill, ).
    """

    def get_tree(self):
        """
        For each cell return complete path, in the form suitable for tally card.
        """

        # prepare temporary structure:
        ud = {}
        for n, p in self.items():
            u, f = p[:2]
            ul = ud.get(u, [])
            if not ul: ud[u] = ul
            ul.append((n, f))


        for c, f in in ud[0]:
            if f == 0:
                yield (c, )
            else:
                for 





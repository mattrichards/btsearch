#!/usr/bin/python

# btsearch Copyright (C) 2016, Matt Richards.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
btsearch is a tool for querying a file that contains the
output of GDB's `thread apply all bt`.
"""

# Keywords for the query language.
KEYWORD_AND = "AND"
KEYWORD_OR = "OR"

class Index(object):
    """Index represents an analyzed version of a file containing
    a thread dump.
    """

    def __init__(self, f):
        """Constructs an Index from an iterable object that contains
        a series of backtraces separated by two newlines.
        """
        self.allbts = []
        btlines = []
        for line in f:
            line = line.strip()
            if line == "" and len(btlines) > 0:
                # End of backtrace
                self.allbts.append(Backtrace("\n".join(btlines)))
                btlines = []
                continue

            btlines.append(line)

        if len(btlines) > 0:
            self.allbts.append(Backtrace("\n".join(btlines)))
        #print "Indexed %d backtraces" % len(self.allbts)
        self.inverted_index = make_func_to_bt_index(self.allbts)

    def query(self, query):
        """Query takes a query string, parses it, runs the query
        against the index, then returns the set of matching backtraces.

        Query string syntax looks like:
           func1 AND func2 OR func3
        """
        q = parse_query(query)

        # 'q' should be well-formed at this point since parse_query()
        # would have raised if there were issues.

        results = set()
        op = None
        for i, predicate in enumerate(q):
            if i % 2 == 0:
                cur_results = self.match_predicate(predicate)
                if op is None or op == "OR":
                    results.update(cur_results)
                else:
                    results.intersection_update(cur_results)
            else:
                op = predicate

        return sorted(results)

    def match_predicate(self, pred):
        return self.inverted_index.get(pred, set())


def make_func_to_bt_index(bts):
    """Takes a list of Backtraces and produces a dict of function names
    to sets of Backtraces that contain that function.
    """
    idx = {}
    for bt in bts:
        for func in bt.functions:
            try:
                idx[func].add(bt)
            except KeyError:
                idx[func] = set([bt])

    return idx


def parse_query(query):
    """Parses a query string into a list of attributes and operators."""
    tokens = query.split()
    for i, token in enumerate(tokens):
        if i % 2 == 0:
            continue
        # Allow the user to enter operators in any case; make them all upper
        # case to be consistent.
        token = token.upper()
        if token != KEYWORD_OR and token != KEYWORD_AND:
            raise SyntaxError("Invalid operator '%s', must be AND or OR")
        tokens[i] = token
    return tokens


class Backtrace(object):
    """Backtrace represents the backtrace of a single threads at
    a moment in time.
    """

    def __init__(self, snippet):
        """Creates a Backtrace from a thread's backtrace output from GDB,
        like:
        Thread 1 (process 3292):
        #0  0x00007fff821e2c48 in readdir$INODE64 ()
        #1  0x00007fff821ba944 in fts_build ()
        #2  0x00007fff821bafd8 in fts_children$INODE64 ()
        #3  0x0000000100001ba5 in _mh_execute_header ()
        #4  0x000000010000191f in _mh_execute_header ()
        #5  0x00007fff8b6545c9 in start ()
        """
        self.snippet = snippet.strip()
        lines = self.snippet.split('\n')
        self.id = int(lines[0].split()[1])
        self.functions = set()
        for line in lines[1:]:
            if len(line) == 0 or line[0] != '#':
                # There can be stuff at the end of a backtrace like:
                #   Cannot access memory at address 0xffffffff
                # Probably useful to keep in the snippet, but we should not
                # index these.
                continue

            self.functions.add(line.split()[3])

    def __str__(self):
        """Pretty prints the Backtrace."""
        return self.snippet

    def __cmp__(self, other):
        """Order Backtraces by thread id."""
        return self.id - other.id

def main():
    bt = Backtrace("""Thread 1 (process 3292):
#0  0x00007fff821e2c48 in readdir$INODE64 ()
#1  0x00007fff821ba944 in fts_build ()
#2  0x00007fff821bafd8 in fts_children$INODE64 ()
#3  0x0000000100001ba5 in _mh_execute_header ()
#4  0x000000010000191f in _mh_execute_header ()
#5  0x00007fff8b6545c9 in start ()    
""")
    #print bt
    #print make_func_to_bt_index([bt])
    f = open("./bt.txt")
    idx = Index(f)
    f.close()


if __name__ == "__main__":
    main()

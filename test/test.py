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

import unittest
import btsearch

class TestQueryParsing(unittest.TestCase):

    def test_single(self):
        q = btsearch.parse_query("func")
        self.assertEqual(len(q), 1)

    def test_or(self):
        q = btsearch.parse_query("func OR func1")
        self.assertEqual(q, ["func", "OR", "func1"])

    def test_and(self):
        q = btsearch.parse_query("func AND func1")
        self.assertEqual(q, ["func", "AND", "func1"])

    def test_multiple(self):
        q = btsearch.parse_query("func AND func1 OR func2")
        self.assertEqual(q, ["func", "AND", "func1", "OR", "func2"])

    def test_case_insensitive(self):
        q = btsearch.parse_query("func and func1")
        self.assertEqual(q, ["func", "AND", "func1"])

    def test_extra_spaces(self):
        q = btsearch.parse_query(" func    AND func1 OR      func2   ")
        self.assertEqual(q, ["func", "AND", "func1", "OR", "func2"])

    def test_invalid_query(self):
        ex = None
        try:
            btsearch.parse_query("func func")
        except SyntaxError, e:
            ex = e
            pass
        self.assertIsNotNone(ex)


class TestPredicateMatching(unittest.TestCase):

    def test_simple(self):
        idx = btsearch.Index(
            ["Thread 67 (process 16602):",
            "#0  0x00007fff88f4b94a in __workq_kernreturn ()",
            "#1  0x00007fff95149b29 in _pthread_wqthread ()",
             "#2  0x00007fff951473dd in start_wqthread ()]"])
        matches = idx.match_predicate("_pthread_wqthread")
        self.assertEqual(len(matches), 1)

    def test_multiple(self):
        idx = btsearch.Index(
            ["Thread 67 (process 16602):",
             "#0  0x00007fff88f4b94a in __workq_kernreturn ()",
            "#1  0x00007fff95149b29 in _pthread_wqthread ()",
            "#2  0x00007fff951473dd in start_wqthread ()]",
             "",
             "Thread 66 (process 16602):",
             "#0  0x00007fff951473dd in start_wqthread ()]",
             "",
             "Thread 65 (process 16602):",
             "#0  0x00007fff88f4b94a in __workq_kernreturn ()",
            "#1  0x00007fff95149b29 in _pthread_wqthread ()",
             "#2  0x00007fff951473dd in start_wqthread ()]"])
        matches = idx.match_predicate("_pthread_wqthread")
        self.assertEqual(len(matches), 2)

    def test_none(self):
        idx = btsearch.Index(
            ["Thread 67 (process 16602):",
             "#0  0x00007fff88f4b94a in __workq_kernreturn ()",
            "#1  0x00007fff95149b29 in _pthread_wqthread ()",
             "#2  0x00007fff951473dd in start_wqthread ()]"])
        matches = idx.match_predicate("great_thundle")
        self.assertEqual(len(matches), 0)
        
if __name__ == "__main__":
    unittest.main()

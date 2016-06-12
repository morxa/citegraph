#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2016 Till Hofmann
# This file is part of CiteGraph.

# CiteGraph is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# CiteGraph is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with CiteGraph.  If not, see <http://www.gnu.org/licenses/>.

import citegraph
import unittest

class TestScholarAuthorParser(unittest.TestCase):
    def setUp(self):
        self.parser = citegraph.ScholarAuthorParser()
    def test_get_author_id(self):
        self.assertEqual(self.parser.find_author('Tim Niemueller'),
                         'iRMEfoAAAAAJ')
        self.assertEqual(self.parser.find_author('John McCarthy'),
                         'SuVID2wAAAAJ')
        self.assertEqual(self.parser.find_author('Sven König'),
                         'tpoh43QAAAAJ')
        self.assertEqual(self.parser.find_author('Łukasz Kaiser'),
                         'JWmiQR0AAAAJ')
        self.assertEqual(self.parser.find_author('Paul Erdős'),
                         'cVeVZ1YAAAAJ')
    def test_parse_author(self):
        name = 'Tim Niemueller'
        author = citegraph.Author(name, self.parser.find_author(name))
        coauthor_name = 'Gerhard Lakemeyer'
        coauthor = citegraph.Author(coauthor_name,
                    self.parser.find_author(coauthor_name))
        coauthors = self.parser.parse_author(author)
        self.assertTrue(coauthor in coauthors)

if __name__ == '__main__':
    unittest.main()

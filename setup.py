#!/usr/bin/env python3

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

from distutils.core import setup

setup(name='citegraph',
      version='0.1',
      description='Tool to generate dot graphs showing co-authors',
      author='Till Hofmann',
      author_email='hofmanntill@gmail.com',
      py_modules=['citegraph'],
     )

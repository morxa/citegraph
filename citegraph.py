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

import argparse
import copy
from lxml import html
import pygraphviz
import re
import requests
import urllib.parse

class ScholarAuthorParser(object):
    def __init__(self):
        """ Set all URLs, paths, regular expressions, etc. used in this class.
        """
        self.base_url = 'https://scholar.google.com'
        self.coauthor_xpath = '//h3[@class="gsc_1usr_name"]/a'
        self.author_search_url = \
            '/citations?view_op=search_authors&mauthors={name}'
        self.coauthor_search_url ='/citations?view_op=list_colleagues&user={id}'
        self.author_match_string = '.*\Wuser=([^&]*)&'
        self.author_xpath = '//h3[@class="gsc_1usr_name"]/a'
    def find_author(self, name):
        """ Find the author with the given name.
        @param name the name of the author
        @return author ID
        """
        url = self.author_search_url.format(name=urllib.parse.quote(name))
        page = requests.get(self.base_url + url)
        tree = html.fromstring(page.content)
        author_tree_objects = tree.xpath(self.author_xpath)
        if len(author_tree_objects) > 1:
            print("WARNING: More than 1 author found for query '{name}'! "
                    'Using first author in the list.'.format(name=name))
        author_tree_object = author_tree_objects[0]
        author_url = author_tree_object.attrib['href']
        #print("Author's URL is {0}".format(author_url))
        return self.get_id_from_url(author_url)
    def get_id_from_url(self, author_url):
        """ Get an author ID from a URL.
        @param author_url the Google Scholar URL of the author
        @return the author's ID
        """
        match = re.match(self.author_match_string, author_url)
        if not match:
            print("ERROR: Could not get author ID from URL. "
                    "URL: {0}, regexp: {1}".format(
                        author_url, self.author_match_string))
            return None
        author_id = match.groups(1)[0]
        #print("Author's ID is {0}.".format(author_id))
        return author_id
    def get_url_from_id(self, author_id):
        """ Compute the Google Scholar URL for an author with the given ID.
        @param author_id the ID of the author
        @return the Google Scholar ID of the author
        """
        return self.base_url + self.coauthor_search_url.format(id=author_id)
        
    def parse_author(self, author, num_coauthors):
        """ Parse the given author.
        This assumes the author's name and URL is already set properly. Fetch
        the URL from Google Scholar and parse the result. Set the author's
        coauthors to the list resulting from the request.
        @param author the author to parse; name and URL must be set.
        @param num_coauthors the number of coauthors to return.
        @return the author's coauthors
        """
        page = requests.get(self.get_url_from_id(author.id))
        tree = html.fromstring(page.content)
        coauthor_tree_objects = tree.xpath(self.coauthor_xpath)
        coauthor_limit = num_coauthors or len(coauthor_tree_objects)
        for coauthor_tree_object in coauthor_tree_objects[0:coauthor_limit]:
            # Each coauthor is an 'a' object. The text is the author's name, the
            # href is the Google Scholar URL.
            name = coauthor_tree_object.text_content()
            url = coauthor_tree_object.attrib['href']
            author_id = self.get_id_from_url(url)
            coauthor = Author(name, author_id, url)
            author.add_coauthor(coauthor)
        return author.coauthors
        
class Author(object):
    def __init__(self, name, id, url = ''):
        self.name = name
        self.url = url
        self.id = id
        self.coauthors = set()
    def __eq__(self, other):
        """ Check if two authors are equal.
        Two authors are equal if they have the same name.
        @param other the other author
        @return true if the authors are eqal
        """
        return self.id == other.id
    def __ne__(self, other):
        """ Check if two authors are unequal.
        This is the inverse of __eq__.
        @param other the other author
        @return true if the objects are unequal
        """
        return not self.__eq__(other)
    def __hash__(self):
        """ Compute a hash of the object.
        Computes the hash using the author name.
        @return the hash of the object
        """
        return hash(self.name)
    def add_coauthor(self, coauthor):
        """ Add the given coauthor to the list of coauthors.
        @param coauthor the Author object to add
        """
        self.coauthors.add(coauthor)
    def __str__(self):
        """ String represenation of an author.
        @return the name of the author
        """
        return self.name

class DotGraphGenerator:
    """ The DotGraphGenerator turns a set of authors into a dot graph.
    """
    def __init__(self, output, layout):
        """ Initialize the generator.
        @param output the path to the output file
        @param layout the layout filter to use
        """
        self.output = output
        self.layout = layout
    def authors_to_dot(self, query_author, authors):
        """ From a set of authors, compute a dot graph.
        @param authors a set of authors
        @return a pygraphviz.AGraph object that represents the graph
        """
        self.query_author = query_author
        graph = pygraphviz.AGraph(strict=True, overlap=False)
        for author in authors:
            is_root = author == query_author
            graph.add_node(author.id, label=author.name, root=is_root)
        for author in authors:
            for coauthor in author.coauthors:
                graph.add_edge(author.id, coauthor.id)
        return graph
    def draw_graph(self, graph):
        """ Draw the given dot graph. Writes output to the local directory.
        @param graph the graph to draw
        """
        print('Number of nodes: {0}; number of edges: {1}'\
                .format(graph.number_of_nodes(), graph.number_of_edges()))
        graph.node_attr['shape'] = 'box'
        graph.node_attr['style'] = 'filled'
        graph.graph_attr['outputorder'] = 'edgesfirst'
        graph.graph_attr['label'] = \
            'CiteGraph for {0}'.format(self.query_author.name)
        graph.layout(prog=self.layout)
        graph.draw(self.output)

if __name__ == '__main__':
    aparser = argparse.ArgumentParser(description='Get a graph for coauthors.')
    aparser.add_argument('name', type=str,
        help='the name of the author')
    aparser.add_argument('-d', '--depth', type=int, default=5,
        help='Depth of the resulting graph, i.e. max distance to coauthor')
    aparser.add_argument('-b', '--breadth', type=int, default=0,
        help='Breadth of the resulting graph, i.e. number of coauthors to add')
    aparser.add_argument('-o', '--output', type=str, default='authors.pdf',
        help='Output file; the output type is automatically determined by the '
                'suffix of the output file')
    aparser.add_argument('-l', '--layout', type=str, default='circle',
        help='Layout filter to use. Good options are circle and neato. '
                'See the manpage of dot(1) for all options')
    args = aparser.parse_args()
    sparser = ScholarAuthorParser()
    author_id = sparser.find_author(args.name)
    query_author = Author(args.name, author_id)
    authors = set()
    authors.add(query_author)
    pending_authors = copy.copy(authors)
    for _ in range(0,args.depth):
        new_authors = set()
        for author in pending_authors:
            new_authors = new_authors.union(sparser.parse_author(author,
                                                                 args.breadth))
        pending_authors.clear()
        for author in new_authors:
            if author not in authors:
                authors.add(author)
                pending_authors.add(author)
    print('Author: {author}'.format(author=query_author))
    print('Coauthors:')
    for a in query_author.coauthors:
        print(a)
    print('Number of total authors: {0}'.format(len(authors)))
    dot_generator = DotGraphGenerator(args.output, args.layout)
    graph = dot_generator.authors_to_dot(query_author, authors)
    dot_generator.draw_graph(graph)

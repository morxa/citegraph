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

from lxml import html
import re
import requests
import urllib

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
        url = self.author_search_url.format(name=urllib.quote(name))
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
        
    def parse_author(self, author):
        """ Parse the given author.
        This assumes the author's name and URL is already set properly. Fetch
        the URL from Google Scholar and parse the result. Set the author's
        coauthors to the list resulting from the request.
        @param author the author to parse; name and URL must be set.
        @return the author's coauthors
        """
        page = requests.get(self.get_url_from_id(author.id))
        tree = html.fromstring(page.content)
        coauthor_tree_objects = tree.xpath(self.coauthor_xpath)
        for coauthor_tree_object in coauthor_tree_objects:
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

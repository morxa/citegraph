# citegraph
This is a small tool to generate a DOT graph that shows all co-authors (and
their co-authors) for a given author. The information is read from Google
Scholar.

As an example, to see John McCarthy's co-authors up to depth 2 (meaning his
co-authors and all his co-authors' co-authors), run:

    $ ./citegraph.py -d 2 "John McCarthy"

This will produce a file `authors.circo.pdf`.

You can also limit the shown co-authors of each author to the top x co-authors:

    $ ./citegraph.py -d 3 -b 8 "John McCarthy"

Note that the number of shown authors quickly gets too big. If you want to have
a high depth (`-d`), then you need to limit the branching factor (`-b`)
accordingly.

For more options, run

    $ ./citegraph.py -h

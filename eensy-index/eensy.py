import collections
import os
import math
import unittest


Loc = collections.namedtuple("Loc", "document offsets")
Result = collections.namedtuple("Result", "document score")


class Document:
    """ A single file in the search corpus. """
    def __init__(self, id, filename):
        self.id = id
        self.name = filename.replace(".txt", "")
        self.filename = filename
        self.max_tf = 0


STOP_WORDS = set("""the of in and to a an was for on with is by as at from that
it were are has had also its this may be or""".split())


def tokens(text):
    words = text.lower().split()
    for word in words:
        if any(c.isalpha() or c.isdigit() for c in word):
            if word not in STOP_WORDS:
                yield word


class Index:
    def __init__(self, dir):
        """Create an index with files from a given directory."""
        self.documents = []
        self.terms = collections.defaultdict(list)

        for filename in os.listdir(dir):
            path = os.path.join(dir, filename)
            with open(path) as f:
                text = f.read()
            self.add_doc(filename, text)

    def add_doc(self, filename, text):
        """Add a document to the index."""
        id = len(self.documents)
        doc = Document(id, filename)
        self.documents.append(doc)

        locs_in_file = collections.defaultdict(lambda: Loc(doc, []))
        for i, word in enumerate(tokens(text)):
            locs_in_file[word].offsets.append(i)
        doc.max_tf = max(len(loc.offsets) for loc in locs_in_file.values())

        for word, locs in locs_in_file.items():
            self.terms[word].append(locs)

    def idf(self, term):
        """Compute inverse document frequency of a term."""
        locs = self.lookup(term)
        if locs:
            df = len(locs) / len(self.documents)
            return math.log(1/df)

    def lookup(self, term):
        """Get information about the given search term, or None."""
        return self.terms.get(term, [])

    def search(self, query, limit=10):
        """Perform a whole search, returning the top `limit` results."""
        file_scores = collections.defaultdict(float)
        for word in tokens(query):
            locs = self.lookup(word)
            if locs:
                idf = self.idf(word)
                for loc in locs:
                    tf = 100 * len(loc.offsets) / loc.document.max_tf
                    file_scores[loc.document] += tf * idf

        results = [Result(doc, score) for doc, score in file_scores.items()]
        results.sort(key=lambda pair: pair.score, reverse=True)
        return results[:limit]

    def save(self, index_dir):
        """Write this index to a directory on disk."""
        if not os.path.isdir(index_dir):
            os.makedirs(index_dir)

        with open(os.path.join(index_dir, "documents.txt"), "w") as f:
            for doc in self.documents:
                f.write("{},{},{}".format(doc.name, doc.filename, doc.max_tf))

        directory = []
        with open(os.path.join(index_dir, "index.dat"), "wb") as f:
            bytes_written = 0
            for word, locs in self.terms.items():
                bits = word.encode('utf-8') + b"\n"
                for loc in locs:
                    bits.append(???)
                directory.append((word, bytes_written, len(bits)))
                f.write(bits)
                bytes_written += len(bits)

        with open(os.path.join(index_dir, "directory.txt"), "w") as f:
            for word, offset, nbytes in directory:
                f.write("{},{},{}".format(word, offset, nbytes))

## class IndexTests(unittest.TestCase):
##     def test_...(self):
##         self.assertEqual(...)
## 
## if __name__ == '__main__':
##     unittest.main()


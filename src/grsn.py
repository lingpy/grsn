"""
Grouping sounds with orthography profiles.
"""
import unicodedata
from csvw.dsv import UnicodeDictReader, UnicodeWriter
from collections import defaultdict


def unorm(normalization, string):
    if isinstance(string, str):
        return unicodedata.normalize(normalization, string)
    return string


def segment(word, profile):
    if len(word) == 0:
        return [word]
    queue = [[[], word, '']]
    while queue:
        segmented, current, rest = queue.pop(0)
        if current in profile and not rest:
            return segmented + [current]
        elif len(current) == 1 and not current in profile:
            if rest:
                queue += [[segmented + [current], rest, '']]
            else:
                return segmented + [current]
        elif not current in profile:
            queue += [[
                    segmented, 
                    current[:len(current)-1],
                    current[-1] + rest
                    ]]
        else:
            queue += [[
                    segmented + [current],
                    rest,
                    ''
                    ]]


def convert(segments, profile, column, missing="«{0}»"):
    return [
            profile.get(
                s, {column : missing.format(s)}
                ).get(
                    column, missing.format("column--{0}-not-found".format(column))
                    ) for s in segments]


def retrieve_profile(
        words, mapping=None, grapheme_column="Grapheme",
        frequency_column="Frequency"):
    """
    Retrieve a profile for separated words.

    Parameters
    ----------
    words: list of iterables
    mapping: function that determines how individual segments are 
             retrieved from each word, if None, we assume that the 
             individual words are iterables
    """
    profile = defaultdict(lambda : {grapheme_column: "", frequency_column: 0})
    for word in words:
        for token in mapping(word) if mapping else word:
            profile[token][grapheme_column] = token
            profile[token][frequency_column] += 1

    return profile


class OrthoProfile:

    def __init__(self, profile, normalization="NFD", missing="«{0}»", null="NULL", grapheme_column="Grapheme"):
        
        self.profile = {}
        self.columns = [grapheme_column] + [
                c for c in sorted(profile[0].keys()) if c != grapheme_column]
        for row in profile:
            self.profile[unorm(normalization, row[grapheme_column])] = {
                    k: unorm(normalization, row.get(k)) for k in self.columns}
        self.norm = lambda x: unorm(normalization, x)
        self.missing = missing
        self.null = null
        self.grapheme = grapheme_column

    def __getitem__(self, idx):
        return self.profile[idx]

    def __call__(self, sequence, column=None):
        column = column or self.grapheme
        if column not in self.columns:
            raise ValueError("The column {0} is not available.".format(column))
        return [elm for elm in convert(segment(self.norm(sequence), self.profile),
                       self.profile, column or self.grapheme, self.missing) if elm != self.null]
    
    @classmethod
    def from_file(cls, file, normalization="NFD", delimiter="\t",
                  missing="«{0}»", null="NULL", grapheme_column="Grapheme"):
        data = []
        with UnicodeDictReader(file, delimiter=delimiter) as reader:
            for row in reader:
                data += [row]
        return cls(data, normalization=normalization,
                   missing=missing, null=null, grapheme_column=grapheme_column)
    

    @classmethod
    def from_table(cls, table, normalization="NFD", delimiter="\t",
                   missing="«{0}»", null="NULL",
                   grapheme_column="Grapheme"):
        header = table[0]
        data = []
        for row in table[1:]:
            data += [dict(zip(header, row))]
        return cls(data, normalization=normalization, missing=missing,
                   null=null, grapheme_column=grapheme_column)

    @classmethod
    def from_words(cls, words, normalization="NFD", missing="«{0}»",
                      mapping=None, null="NULL",
                   grapheme_column="Grapheme"):
        return cls(list(retrieve_profile(words, mapping=mapping).values()),
                   normalization=normalization, missing=missing, null=null,
                   grapheme_column=grapheme_column)

    def to_table(self):
        table = [self.columns]
        for row in self.profile.values():
            table += [[row[c] for c in self.columns]]
        return table

    def write(self, path, delimiter="\t"):
        with UnicodeWriter(path, delimiter=delimiter) as writer:
            writer.writerows(self.to_table())


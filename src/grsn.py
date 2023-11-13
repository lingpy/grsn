"""
Sound Grouper: Grouping sounds with conversion tables.
"""
import unicodedata
from csvw.dsv import UnicodeDictReader, UnicodeWriter
from collections import defaultdict


def unorm(normalization, string):
    """
    Apply unicode normalization to a string.

    Note
    ----
    In contrast to the normal method, errors are caught and the input is
    returned, e.g., when passing an integer.
    """
    if isinstance(string, str):
        return unicodedata.normalize(normalization, string)
    return string


def segment(word, segments):
    """
    Use 
    """
    if len(word) == 0:
        return [word]
    queue = [[[], word, ""]]
    while queue:
        segmented, current, rest = queue.pop(0)
        if current in segments and not rest:
            return segmented + [current]
        elif len(current) == 1 and not current in segments:
            if rest:
                queue += [[segmented + [current], rest, ""]]
            else:
                return segmented + [current]
        elif not current in segments:
            queue += [[segmented, current[: len(current) - 1], current[-1] + rest]]
        else:
            queue += [[segmented + [current], rest, ""]]


def convert(segments, converter, column, missing="«{0}»"):
    return [
        converter.get(s, {column: missing.format(s)}).get(
            column, missing.format("column--{0}-not-found".format(column))
        )
        for s in segments
    ]


def retrieve_converter(
    words, mapping=None, grapheme_column="Sequence", frequency_column="Frequency"
):
    """
    Retrieve a conversion table for segmented words.

    Parameters
    ----------
    words: list of iterables
    mapping: function that determines how individual segments are
             retrieved from each word, if None, we assume that the
             individual words are iterables
    """
    converter = defaultdict(lambda: {grapheme_column: "", frequency_column: 0})
    for word in words:
        for token in mapping(word) if mapping else word:
            converter[token][grapheme_column] = token
            converter[token][frequency_column] += 1
    return converter


class SoundGrouper:
    """
    Group sounds with a conversion table.
    """
    def __init__(
        self,
        converter,
        normalization="NFD",
        missing="«{0}»",
        null="NULL",
        grapheme_column="Sequence",
    ):

        self.converter = {}
        self.columns = [grapheme_column] + [
            c for c in sorted(converter[0].keys()) if c != grapheme_column
        ]
        for row in converter:
            self.converter[unorm(normalization, row[grapheme_column])] = {
                k: unorm(normalization, row.get(k)) for k in self.columns
            }
        self.norm = lambda x: unorm(normalization, x)
        self.missing = missing
        self.null = null
        self.grapheme = grapheme_column

    def __getitem__(self, idx):
        return self.converter[idx]

    def __call__(self, sequence, column=None):
        column = column or self.grapheme
        if column not in self.columns:
            raise ValueError("The column {0} is not available.".format(column))
        return [
            elm
            for elm in convert(
                segment(self.norm(sequence), self.converter),
                self.converter,
                column or self.grapheme,
                self.missing,
            )
            if elm != self.null
        ]

    @classmethod
    def from_file(
        cls,
        file,
        normalization="NFD",
        delimiter="\t",
        missing="«{0}»",
        null="NULL",
        grapheme_column="Sequence",
    ):
        data = []
        with UnicodeDictReader(file, delimiter=delimiter) as reader:
            for row in reader:
                data += [row]
        return cls(
            data,
            normalization=normalization,
            missing=missing,
            null=null,
            grapheme_column=grapheme_column,
        )

    @classmethod
    def from_table(
        cls,
        table,
        normalization="NFD",
        delimiter="\t",
        missing="«{0}»",
        null="NULL",
        grapheme_column="Sequence",
    ):
        header = table[0]
        data = []
        for row in table[1:]:
            data += [dict(zip(header, row))]
        return cls(
            data,
            normalization=normalization,
            missing=missing,
            null=null,
            grapheme_column=grapheme_column,
        )

    @classmethod
    def from_words(
        cls,
        words,
        normalization="NFD",
        missing="«{0}»",
        mapping=None,
        null="NULL",
        grapheme_column="Sequence",
    ):
        return cls(
            list(retrieve_converter(words, mapping=mapping).values()),
            normalization=normalization,
            missing=missing,
            null=null,
            grapheme_column=grapheme_column,
        )

    def to_table(self):
        table = [self.columns]
        for row in self.converter.values():
            table += [[row[c] for c in self.columns]]
        return table

    def write(self, path, delimiter="\t"):
        with UnicodeWriter(path, delimiter=delimiter) as writer:
            writer.writerows(self.to_table())

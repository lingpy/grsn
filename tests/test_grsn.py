from grsn import segment, convert, SoundGrouper, retrieve_converter, unorm
from pathlib import Path
from csvw.dsv import UnicodeDictReader
from pytest import raises


def test_unorm():

    assert len(unorm("NFD", "á")) == 2
    assert len(unorm("NFC", "á")) == 1
    assert unorm("NFD", 1) == 1
    assert unorm("NFC", None) is None

def test_segment():

    assert segment("matam", {"m", "at", "a", "m"}) == [
            "m", "at", "a", "m"]
    assert segment("", {"a"}) == [""]
    assert segment("m", {}) == ["m"]


def test_convert():
    prf = {
            "am": {"grouped": "a.m", "ungrouped": "a m"},
            "t": {"grouped": "t", "ungrouped": "t"}
            }
    assert convert(segment("tam", prf), prf, "grouped") == ["t", "a.m"]
    assert convert(segment("tam", prf), prf, "ungrouped") == ["t", "a m"]
    assert convert(segment("tak", prf), prf, "grouped") == ["t", "«a»", "«k»"]


def test_SoundGrouper():
    
    with UnicodeDictReader(Path(__file__).parent / "data.tsv", delimiter="\t") as reader:
        data = [row for row in reader]

    prf = SoundGrouper(data, normalization="NFC", missing="?")
    assert prf("tam", "IPA") == ["t", "ã"]
    prf2 = SoundGrouper.from_file(Path(__file__).parent / "data.tsv",
                                  delimiter="\t", missing="?")
    assert prf("tum") == ["t", "?", "?"]

    prf3 = SoundGrouper.from_table([["Graphemes", "IPA"]] + [[row["Sequence"], row["IPA"]] for row in
                                    data],
                                   grapheme_column="Graphemes")
    assert prf3("amim") == ["am", "«i»", "«m»"]

    assert prf3.to_table()[0][0] == "Graphemes"

    my_list = [["a", "b"], ["aa", "bb"], ["cc", "cc"]]
    op1 = SoundGrouper.from_table(my_list, grapheme_column="a")
    op2 = SoundGrouper.from_table(op1.to_table(),
                                 grapheme_column=op1.grapheme)
    assert op1.to_table()[-1][0] == "cc"
    
    op2.write(Path(__file__).parent / "test.csv", delimiter=",")
    op3 = SoundGrouper.from_file(
            Path(__file__).parent / "test.csv", delimiter=",", 
            grapheme_column="a")
    assert len(op3.converter) == 2
    assert op3["aa"]["b"] == "bb"

    op4 = SoundGrouper.from_words(["mat the ma"], mapping=lambda x: x.split())
    op5 = SoundGrouper.from_words(["mat the ma".split()])
    assert op4("mat") == op5("mat")

    assert raises(ValueError, op5, "mat", column="IPPA")

def test_retrieve_converter():
    assert "th" in retrieve_converter(["m a th e m a t i cs"], mapping=lambda x: x.split())


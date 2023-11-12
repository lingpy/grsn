# Grouping Sounds with Orthography Profiles

This package offers very straightforward implementations for the Orthography Profile method proposed by [Moran and Cysouw (2018)](https://langsci-press.org/catalog/book/176). The implementation differs from the representative implementation in the segments package in so far as it does not allow for rule-based orthography profile parsing, following the experience we had with using orthography profiles for the [Lexibank repository](https://lexibank.clld.org). As a result, the code is much more limited in size, but it is also more flexible with respect to the way in which sequence manipulations with orthography profiles can be handled.

## Basic Usage: Segmenting and Converting with the `segment` and `convert` Functions

The package offers to basic methods, one to segment and one to convert a string (see [List 2023](https://calc.hypotheses.org/6361) for details on the algorithm behind these methods). 

```python
>>> from grsn import segment, convert
```

I order to segment a string into a list of graphemes, you only need to pass a list of graphemes to the function (a Python iterable that can be queried with `a in b`, such as a list, a dictionary, or a set).

In order to convert a segmented string, we use a dictionary lookup with the specific structure for the representation of orthography profiles presented in the JavaScript implementation by [List (2023)](https://calc.hypotheses.org/6361). 

```python
>>> lookup = {
        "@": {"Grapheme": "a", "IPA": "ə"},
        "a": {"Grapheme": "a", "IPA": "a"},
        "ts_h": {"Grapheme": "a", "IPA": "tsʰ"},
        "k_h": {"Grapheme": "a", "IPA": "kʰ"},
    }
```

In order to convert from one orthography to another orthography profile we first have to segment our sequence, and since the lookup we just defined can be queried if it contains a character sequence or not, we can conveniently just use this lookup:

```python
>>> segments = segment("k_hats_h@", lookup)
>>> segments
["k_h", "a", "ts_h", "@"]
```

To convert this sequence now into its IPA representation, we apply the `convert` function to the list of segments.

```python
>>> tokens = convert(segments, lookup, column="IPA")
>>> tokens
['kʰ', 'a', 'tsʰ', 'ə']
```

If we use elements that are not given as such in the profile, this will be marked by default by putting the character in `«»`-quotes. 

```python
>>> tokens = convert(segment("k_hits_h@", lookup), lookup, column="IPA")
>>> tokens
['kʰ', '«i»', 'tsʰ', 'ə']
```

You can modify this behaviour with the `missing` keyword:

```python
>>> tokens = convert(segment("k_hits_h@", lookup), lookup, column="IPA", missing="?{0}¿)
>>> tokens
['kʰ', '?i¿', 'tsʰ', 'ə']
```

## Extended Usage: `OrthoProfile` Class



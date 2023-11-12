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

While `segment` and `convert` offer two basic functions that are equivalent in principle to the usage of orthography profiles as described by Moran and Cysouw (2018), they are not that convenient to use when dealing with externally stored orthography profiles that one wants to use to manipulate many different sequences. Here, the `OrthoProfile` class offers a more robust way to manipulate sequences with orthography profiles that one can store in TSV or CSV files. To get started, add your profile to a TSV or a CSV file, just as they are described by Moran and Cysouw (2018) and then load the data with the help of the `OrthoProfile.from_file` method.

```python
>>> from grsn import OrthoProfile
>>> op = OrthoProfile.from_file("data.csv", delimiter=",", grapheme_column="Grapheme", null='NULL')
>>> op("k_hats_h@", column="IPA")
['kʰ', 'a', 'tsʰ', 'ə']
```

Having loaded an orthography profile, you can convert or segment a sequence by calling the object, as shown above, and specifying the column name.

The delimiter allows you to handle both TSV and CSV data (thanks to the [csvw](https://pypi.org/project/csvw) package used to parse CSV files, which is currently the only dependency of `grsn`). The keyword `grapheme_column` points to the column that contains the base orthography from which conversion starts (default name `Grapheme` follows the terminology of Moran and Cysouw and the [segments](https://pypi.org/project/segments) package). The keyword `null` points to the value that would be ignored when encountered as a replacement value in the conversion routine (as a default set to `'NULL'`).

Additionally, you can initiate a profile from a list of dictionaries, from a table, and from a list of segmented words.

```python
>>> op1 = OrthoProfile([{"Grapheme": "a", "IPA": "a"}, {"Grapheme": "k_h", "IPA": "kʰ"}, {"Grapheme": "ts_h", "IPA": "tsʰ"}, {"Grapheme": "@", "IPA": "ə"}])
>>> op2 = OrthoProfile.from_table([["Grapheme", "IPA"], ["a", "a"], ["k_h", "kʰ"], ["@", "ə"], ["ts_h", "tsʰ"]])
>>> op3 = OrthoProfile.from_words(["k_h a ts_h @"], mapping=lambda x: x.split())
```

In the last case, no replacement is defined, but instead, the frequency of each element will be calculated. The underlying function used to retrieve an orthography profile from a list of segmented words is the `retrieve_profile` function.

```python
>>> retrieve_profile(["k_h a ts_h @"], mapping=lambda x: x.split())
defaultdict(<function grsn.retrieve_profile.<locals>.<lambda>()>,
            {'k_h': {'Grapheme': 'k_h', 'Frequency': 1},
             'a': {'Grapheme': 'a', 'Frequency': 1},
             'ts_h': {'Grapheme': 'ts_h', 'Frequency': 1},
             '@': {'Grapheme': '@', 'Frequency': 1}})
```

This means, if you want to use a retrieved profile for conversion, you have to add entries for the conversion yourself, for example, by writing the profile to file and then adding a column for the conversion.

```python
>>> op3.write("data.csv", delimiter=",")
```

Alternatively, you can manipulate the `profile` attribute of the `OrthoProfile` class. If you do so, however, you must add new values also to the `columns` attribute of the `OrthoProfile` class, since `columns` determines what is written to file.

```python
>>> op3.profile["k_h"]["IPA"] = "kʰ"
>>> op3.profile["ts_h"]["IPA"] = "tsʰ"
>>> op3.profile["a"]["IPA"] = "a"
>>> op3("k_hats_h@", column="IPA")
ValueError: The column IPA is not available.
>>> op3.columns += ["IPA"]
>>> op3("k_hats_h@", column="IPA")
['kʰ', 'a', 'tsʰ', '«column--IPA-not-found»']
```

Not that in our example above, the conversion for `"ə"` fails, since the grapheme was not defined when manipulating the orthography profile. As a result, the conversion explicitly points to the problem in the output.


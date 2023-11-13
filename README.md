# Grouping Sounds with Conversion Tables

This package takes inspiration from the Orthography Profile method proposed by [Moran and Cysouw (2018)](https://langsci-press.org/catalog/book/176) by offering a very straightforward way to manipulate sound sequences with conversion tables.

## Basic Usage: Segmenting and Converting with the `segment` and `convert` Functions

The package offers to basic methods, one to segment and one to convert a string (see [List 2023](https://calc.hypotheses.org/6361) for details on the algorithm behind these methods). 

```python
>>> from grsn import segment, convert
```

I order to segment a string into a list of graphemes, you only need to pass a list of graphemes or subsequences to the function (a Python iterable that can be queried with `a in b`, such as a list, a dictionary, or a set).

In order to convert a segmented string, we use a dictionary lookup with the specific structure for the representation of conversion tables presented in the JavaScript implementation by [List (2023)](https://calc.hypotheses.org/6361). 

```python
>>> lookup = {
        "@": {"Sequence": "a", "IPA": "ə"},
        "a": {"Sequence": "a", "IPA": "a"},
        "ts_h": {"Sequence": "a", "IPA": "tsʰ"},
        "k_h": {"Sequence": "a", "IPA": "kʰ"},
    }
```

In order to convert from one sequence to another sequence representation we first have to segment our sequence, and since the lookup we just defined can be queried if it contains a character sequence or not, we can conveniently just use this lookup:

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

If we use elements that are not given as such in the conversion table, this will be marked by default by putting the character in `«»`-quotes. 

```python
>>> tokens = convert(segment("k_hits_h@", lookup), lookup, column="IPA")
>>> tokens
['kʰ', '«i»', 'tsʰ', 'ə']
```

You can modify this behaviour with the `missing` keyword:

```python
>>> tokens = convert(segment("k_hits_h@", lookup), lookup, column="IPA", missing="?{0}¿")
>>> tokens
['kʰ', '?i¿', 'tsʰ', 'ə']
```

## Extended Usage: `SoundGrouper` Class

While `segment` and `convert` offer two basic functions to manipulate sequences with conversion tables, they are not that convenient to use when dealing with externally stored tables that one wants to use to manipulate many different sequences. Here, the `SoundGrouper` class offers a more robust way to manipulate sequences with conversion tables that one can store in TSV or CSV files. To get started, add your conversion table to a TSV or a CSV file and then load the data with the help of the `SoundGrouper.from_file` method.

```python
>>> from grsn import SoundGrouper
>>> op = SoundGrouper.from_file("data.csv", delimiter=",", grapheme_column="Grapheme", null='NULL')
>>> op("k_hats_h@", column="IPA")
['kʰ', 'a', 'tsʰ', 'ə']
```

Having loaded an orthography profile, you can convert or segment a sequence by calling the object, as shown above, and specifying the column name.

The delimiter allows you to handle both TSV and CSV data (thanks to the [csvw](https://pypi.org/project/csvw) package used to parse CSV files, which is currently the only dependency of `grsn`). The keyword `grapheme_column` points to the column that contains the base orthography from which conversion starts (default name `Grapheme` follows the terminology of Moran and Cysouw and the [segments](https://pypi.org/project/segments) package). The keyword `null` points to the value that would be ignored when encountered as a replacement value in the conversion routine (as a default set to `'NULL'`).

Additionally, you can initiate a profile from a list of dictionaries, from a table, and from a list of segmented words.

```python
>>> op1 = SoundGrouper([{"Grapheme": "a", "IPA": "a"}, {"Grapheme": "k_h", "IPA": "kʰ"}, {"Grapheme": "ts_h", "IPA": "tsʰ"}, {"Grapheme": "@", "IPA": "ə"}])
>>> op2 = SoundGrouper.from_table([["Grapheme", "IPA"], ["a", "a"], ["k_h", "kʰ"], ["@", "ə"], ["ts_h", "tsʰ"]])
>>> op3 = SoundGrouper.from_words(["k_h a ts_h @"], mapping=lambda x: x.split())
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

Alternatively, you can manipulate the `converter` attribute of the `SoundGrouper` class. If you do so, however, you must add new values also to the `columns` attribute of the `SoundGrouper` class, since `columns` determines what is written to file.

```python
>>> op3.converter["k_h"]["IPA"] = "kʰ"
>>> op3.converter["ts_h"]["IPA"] = "tsʰ"
>>> op3.converter["a"]["IPA"] = "a"
>>> op3("k_hats_h@", column="IPA")
ValueError: The column IPA is not available.
>>> op3.columns += ["IPA"]
>>> op3("k_hats_h@", column="IPA")
['kʰ', 'a', 'tsʰ', '«column--IPA-not-found»']
```

Not that in our example above, the conversion for `"ə"` fails, since the segment was not defined when manipulating the conversion table. As a result, the conversion explicitly points to the problem in the output.


# Illustrating how Orthography Profiles can be Used to Group Sounds

The profile we provide is constructed in such a way that it starts from ungrouped sounds and then groups them. The data are taken from the Lexibank dataset [LuangthongkomKaren](https://github.com/lexibank/luangthongkumkaren), using the EDICTOR version that can be found [online](https://lingulist.de/edictor/links/ltkkaren.html). 

We wrote a little script that creates the data profile automatically from the grouped sounds. To use it, you must have LingPy and PyEdictor installed on your system:

```
pip install pyedictor==0.4
pip install lingpy==2.6.11
```

Additionally, you must install our little `grsn` package, so assuming you open a terminal in the folder of this package, just type:

```
pip install -e .
```

To run the script to download the data, type:

```
python make_profile.py
```

To test if the conversion from ungrouped sounds to grouped sounds is correctly done (reflecting the manual status of editing we used), type:

```
python check_groupings.py
```


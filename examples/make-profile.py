from pyedictor import fetch
from lingpy import *
from collections import defaultdict

def desegment(tokens):
    out = []
    for t in tokens:
        out += [tk.split("/")[1] if "/" in tk else tk for tk in t.split(".")]
    return out


def clean_grouped_tokens(tokens):
    out = []
    for t in tokens:
        items = t.split(".")
        out_items = []
        for itm in items:
            if "/" in itm:
                out_items += [itm.split("/")[1]]
            else:
                out_items += [itm]
        out += [".".join(out_items)]
    return out


wl = fetch(
        "ltkkaren", 
        languages=[
            "Kayah",
            "Kayan",
            "Kayaw",
            "NorthernPao",
            "NorthernPwo",
            "NorthernSgaw",
            "ProtoKaren",
            "SouthernPao",
            "SouthernPwo",
            "SouthernSgaw",
            "WesternBwe",],
        base_url="https://lingulist.de/edev",
        to_lingpy=True
        )

# modify tokens in the data and create profile
wl.add_entries("desegmented", "tokens", lambda x: clean_grouped_tokens(x))
prf = defaultdict(int)
for idx, tokens in wl.iter_rows("tokens"):
    new_tokens = desegment(tokens)
    wl[idx, "tokens"] = basictypes.lists(new_tokens)
    for tk in tokens:
        prf[tuple([t.split('/')[1] if "/" in t else t for t in tk.split('.')])] += 1

with open("karen-profile.tsv", "w") as f:
    f.write("Grapheme\tGrouped\tPlain\tFrequency\n")
    f.write("^\tNULL\tNULL\t\n")
    f.write("$\tNULL\tNULL\t\n")
    f.write("_\tNULL\tNULL\t\n")
    for k, v in sorted(prf.items(), key=lambda x: x[1], reverse=True):
        f.write("_".join(k)+"\t"+".".join(k)+"\t"+" ".join(k)+"\t"+str(v)+"\n")
wl.output("tsv", filename="karen", ignore="all", prettify=False)
print("Created Profile and Downloaded the Wordlist.")


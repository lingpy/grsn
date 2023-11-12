from grsn import OrthoProfile
from lingpy import Wordlist, basictypes

def clean(token):
    if "." in token:
        return ".".join(
                [t.split("/")[1] if "/" in t else t for t in token.split(".")]
                )
    return token.split("/")[1] if "/" in token else token


def ungroup(tokens, modify_token=None):
    modify_token = modify_token if modify_token else lambda x: x
    out = []
    for token in tokens:
        for segment in token.split("."):
            out += [modify_token(segment)]
    return out


op = OrthoProfile.from_file("karen-profile.tsv", normalization="NFC")
wl = Wordlist("karen.tsv")

errors = 0
for idx, doculect, concept, tokens in wl.iter_rows(
        "doculect", "concept", "desegmented"):
    tokens = basictypes.lists(tokens)
    ungrouped = ungroup(tokens, modify_token=clean)
    grouped = [clean(t) for t in tokens]

    auto_grouped = op("_".join(ungrouped), column="Grouped")
    auto_ungrouped = op("_".join(ungrouped), column="Plain")

    if auto_grouped != grouped:
        print(idx, doculect, tokens, " ".join(grouped), " ".join(auto_grouped))
        errors += 1
print("Found {0} errors in data.".format(errors))


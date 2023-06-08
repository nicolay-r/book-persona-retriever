from os.path import join, dirname, realpath

import pandas as pd
from tqdm import tqdm


class FcpApi:
    """ Fictional character personalities API.
    """

    __current_dir = dirname(realpath(__file__))
    personalities = join(__current_dir, "./data/fictional-character-personalities/personalities.txt")

    def __init__(self):
        self._lexicon = None
        self._reversed = None

    def extract_as_lexicon(self, path=None):
        assert(isinstance(path, str) or path is None)
        path = self.personalities if path is None else path
        df = pd.read_csv(path, sep="\t")

        lexicon = {}
        lexicon_df = df[["spectrum", "spectrum_low", "spectrum_high"]]
        for _, row in tqdm(lexicon_df.iterrows(), desc="Reading lexicon", total=len(df)):

            spectrum = row["spectrum"]

            # seeking for existed.
            if spectrum not in lexicon:
                r = row.to_dict()
                lexicon[spectrum] = {"low": r["spectrum_low"], "high": r["spectrum_high"]}
            else:
                continue

        self._lexicon = lexicon

        return lexicon

    def find_by_id(self, val_id):
        spectrum_values = self._lexicon[val_id]
        return spectrum_values["low"], spectrum_values["high"]

    def reversed_spectrums(self):

        if self._lexicon is None:
            self.extract_as_lexicon()

        # Reversed spectrums.
        rev_spectrums = {}
        for s_type, value_d in self._lexicon.items():
            l = value_d["low"]
            h = value_d["high"]
            if l not in rev_spectrums:
                rev_spectrums[l] = {"class": s_type, "type": "low"}
            if h not in rev_spectrums:
                rev_spectrums[h] = {"class": s_type, "type": "high"}
                
        self._reversed = rev_spectrums

        return rev_spectrums

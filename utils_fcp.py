from os.path import join, dirname, realpath

import pandas as pd
from tqdm import tqdm


class FcpApi:
    """ Fictional character personalities API.
    """

    __current_dir = dirname(realpath(__file__))
    personalities = join(__current_dir, "./data/fictional-character-personalities/personalities.txt")

    def extract_as_lexicon(self, path=None):
        assert(isinstance(path, str) or path is None)
        path = self.personalities if path is None else path
        df = pd.read_csv(path, sep="\t")

        lexicon = {}
        lexicon_df = df[["spectrum", "spectrum_low", "spectrum_high"]]
        for _, row in tqdm(lexicon_df.iterrows(), desc="Reading lexicon", total=len(df)):
            r = row.to_dict()

            spectrum = r["spectrum"]

            # seeking for existed.
            if spectrum not in lexicon:
                lexicon[spectrum] = {"low": set([r["spectrum_low"]]), "high": set([r["spectrum_high"]])}
            else:
                meta = lexicon[spectrum]
                meta["low"].add(r["spectrum_low"])
                meta["high"].add(r["spectrum_high"])

        return lexicon
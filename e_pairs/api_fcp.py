import pandas as pd
from tqdm import tqdm


class FcpApi:
    """ Fictional character personalities API.
    """

    lex_low = "low"
    lex_high = "high"

    def __init__(self, personalities_path):
        self._lexicon = None
        self._reversed = None
        self.personalities_path = personalities_path

    def extract_as_lexicon(self, path=None):
        assert(isinstance(path, str) or path is None)
        path = self.personalities_path if path is None else path
        df = pd.read_csv(path, sep="\t")

        lexicon = {}
        lexicon_df = df[["spectrum", "spectrum_low", "spectrum_high"]]
        for _, row in tqdm(lexicon_df.iterrows(), desc="Reading lexicon", total=len(df)):

            spectrum = row["spectrum"]

            # seeking for existed.
            if spectrum not in lexicon:
                r = row.to_dict()
                lexicon[spectrum] = {FcpApi.lex_low: r["spectrum_low"], FcpApi.lex_high: r["spectrum_high"]}
            else:
                continue

        self._lexicon = lexicon

        return lexicon

    def find_by_id(self, val_id):
        spectrum_values = self._lexicon[val_id]
        return spectrum_values[self.lex_low], spectrum_values[self.lex_high]

    @staticmethod
    def spectrum_to_ind(val):
        """ BAPXXX -> XXX
            NOTE: idexing goes from 1, hence we substract 1.
        """
        assert(isinstance(val, str))
        assert("BAP" in val)
        return int(val[3:]) - 1

    @staticmethod
    def float_to_spectrum_key(spec_val):
        assert(isinstance(spec_val, float))
        return FcpApi.lex_low if spec_val < 0 else FcpApi.lex_high

    @staticmethod
    def ind_to_spectrum(ind):
        assert(isinstance(ind, int) and ind >= 0)
        return "BAP" + str((ind + 1))

    def reversed_spectrums(self):

        if self._lexicon is None:
            self.extract_as_lexicon()

        # Reversed spectrums.
        rev_spectrums = {}
        for s_type, value_d in self._lexicon.items():
            l = value_d[FcpApi.lex_low]
            h = value_d[FcpApi.lex_high]
            if l not in rev_spectrums:
                rev_spectrums[l] = {"class": s_type, "type": "low"}
            if h not in rev_spectrums:
                rev_spectrums[h] = {"class": s_type, "type": "high"}
                
        self._reversed = rev_spectrums

        return rev_spectrums

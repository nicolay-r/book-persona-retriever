import json
from os.path import basename

from tqdm import tqdm


class SpectrumIOUtils(object):

    @staticmethod
    def write(filepath, speaker_names, speaker_prompts, weights):

        with open(filepath, "w") as file:
            filename = basename(filepath)
            for speaker_id, prompt in tqdm(enumerate(speaker_prompts), desc=f"Write spectrums {filename}"):
                s = json.dumps({"name": speaker_names[speaker_id],
                                "prompts": prompt.split(),
                                "weights": [round(w, 3) for w in weights[speaker_id]]})
                file.write(s + "\n")

    @staticmethod
    def read(filepaths):
        """ filepaths: list or str
                sources of the spectrums, i.e. single file or multiple files.
        """
        assert(isinstance(filepaths, list) or isinstance(filepaths, str))
        filepaths = [filepaths] if isinstance(filepaths, str) else filepaths

        spectrums = {}
        for filepath in filepaths:
            with open(filepath, "r") as file:
                filename = basename(filepath)
                for line in tqdm(file.readlines(), desc=f"Read lines {filename}"):
                    speaker_info = json.loads(line)
                    spectrums[speaker_info["name"]] = {
                       "prompts": speaker_info["prompts"],
                       "weights": speaker_info["weights"] if "weights" in speaker_info else []
                    }

        return spectrums

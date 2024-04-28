from os.path import join


class HlaExperimentConfig:
    # This a models for the representation of the speakers.
    # ALOHA chatbot paper: https://arxiv.org/abs/1910.08293

    hla_spectrums_limit = 20  # ALOHA parameter which is proposes to keep the most representative traits.
    hla_spectrum_preset = "prompt_top_{}".format(str(hla_spectrums_limit))
    hla_neg_set_speakers_limit = 10

    def __init__(self, books_storage):
        self.hla_melted_data_filepath = join(books_storage, "features_melted.txt")
        self.hla_users_melted_filepath = join(books_storage, "features_melted.txt")
        self.hla_speaker_clusters_path = join(books_storage, "clusters.jsonl")
        # We limit to 20 because of the 2 polarities of spectrums (two different values per one trait).
        self.hla_prompts_filepath = join(books_storage, f"./spectrum_speaker_prompts-{self.hla_spectrum_preset}.txt")
        self.hla_users_embedding_factor = join(books_storage, "./x.speakers-factor.npz")

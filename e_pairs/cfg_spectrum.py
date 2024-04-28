from os.path import join


class SpectrumConfig:

    spectrum_speakers_in_paragraph = 1
    spectrum_comment_speaker_positions = [0, 1, 2]
    spectrum_per_user_count = 8
    embedding_model_name = 'all-mpnet-base-v2'

    def __init__(self, books_storage):
        self.features_norm = join(books_storage, "./x.spectrum-embeddings-norm.npz")
        self.features_diff = join(books_storage, "./x.spectrum-embeddings-diff.npz")
        self.speakers = join(books_storage, "./y.spectrum-speakers.npz")
        self.st_embeddings = join(books_storage, "./x.spectrum-embeddings-sent-transformers-{preset}.npz")

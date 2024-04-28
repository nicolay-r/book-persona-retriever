from os.path import join


class SpectrumConfig:

    speakers_in_paragraph = 1
    spectrum_per_user_count = 8
    comment_speaker_positions = [0, 1, 2]
    embedding_model_name = 'all-mpnet-base-v2'

    def __init__(self, books_storage):
        self.features_norm = join(books_storage, "./x.spectrum-embeddings-norm.npz")
        self.features_diff = join(books_storage, "./x.spectrum-embeddings-diff.npz")
        self.speakers = join(books_storage, "./y.spectrum-speakers.npz")
        self.st_embeddings = join(books_storage, "./x.spectrum-embeddings-sent-transformers-{preset}.npz")

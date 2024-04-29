from os.path import join

from api.my import MyAPI


class SpectrumConfig:

    speakers_in_paragraph = 1
    spectrum_per_user_count = 8
    comment_speaker_positions = [0, 1, 2]
    embedding_model_name = 'all-mpnet-base-v2'
    features_norm = join(MyAPI.books_storage, "./x.spectrum-embeddings-norm.npz")
    features_diff = join(MyAPI.books_storage, "./x.spectrum-embeddings-diff.npz")
    speakers = join(MyAPI.books_storage, "./y.spectrum-speakers.npz")
    st_embeddings = join(MyAPI.books_storage, "./x.spectrum-embeddings-sent-transformers-{preset}.npz")

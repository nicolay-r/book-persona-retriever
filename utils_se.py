from os.path import dirname, realpath, join

from utils import range_exclude_middle, range_middle


class SEApi(object):

    # Main parameters.
    __current_dir = dirname(realpath(__file__))

    dataset_folding_parts = 5
    dataset_folding_fixed_parts = {
        'train': range_exclude_middle(dataset_folding_parts),
        "valid": range_middle(dataset_folding_parts),
    }
    parlai_dataset_episode_candidates_and_traits_shuffle_seed = 42
    parlai_dataset_persona_prefix = ""
    parlai_dataset_candidates_limit = 20
    parlai_dataset_ovesampling_candidates_selection_seed = 42
    dataset_fold_filepath = join(__current_dir, "./data/ceb_books_annot/dataset_f{fold_index}.txt")
    # HLA-related parameters.
    hla_spectrums_limit = 20            # ALOHA parameter which is proposes to keep the most representative traits.
    hla_spectrum_preset = "prompt_top_{}".format(str(hla_spectrums_limit))
    hla_prompts_filepath = join(__current_dir, "./data/ceb_books_annot/spectrum_speaker_prompts-{preset}.txt".format(
        preset=hla_spectrum_preset))
    # The result dataset details.
    parlai_dataset_filepath = join(__current_dir, "./data/se_task/dataset_parlai_{}.zip")
    parlai_dataset_train_candidates_oversample_factor = 5

    def __init__(self):
        pass

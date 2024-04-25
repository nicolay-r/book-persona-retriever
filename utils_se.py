from os.path import dirname, realpath, join

from utils import range_exclude_middle, range_middle


class SEApi(object):

    # Main parameters.
    __current_dir = dirname(realpath(__file__))
    books_storage = join(__current_dir, "./data/se_task/")
    books_storage_original = join(__current_dir, "./data/ceb_books_annot")

    selected_output_dir = join(__current_dir, "./data/se_task_selected/")

    dataset_folding_parts = 5
    dataset_folding_fixed_parts = {
        'train': range_exclude_middle(dataset_folding_parts),
        "valid": range_middle(dataset_folding_parts),
    }
    parlai_dataset_episode_candidates_and_traits_shuffle_seed = 42
    parlai_dataset_persona_prefix = ""
    parlai_dataset_candidates_limit = 20
    parlai_dataset_ovesampling_candidates_selection_seed = 42
    dataset_fold_filepath = join(books_storage_original, "./dataset_f{fold_index}.txt")
    # HLA-related parameters.
    hla_spectrums_limit = 20            # ALOHA parameter which is proposes to keep the most representative traits.
    hla_spectrum_preset = "prompt_top_{}".format(str(hla_spectrums_limit))
    hla_prompts_filepath = join(books_storage_original, "./spectrum_speaker_prompts-{preset}.txt".format(preset=hla_spectrum_preset))
    # The result dataset details.
    parlai_dataset_filepath = join(books_storage, "./dataset_parlai_{}.zip")
    parlai_dataset_train_candidates_oversample_factor = 5

    predefined_speakers = ['153_2', '1257_7', '1257_9', '403_3', '1258_8']

    ignored_speakers = ['33857_0', '1399_0', '34415_0', '36159_0', '3610_0', '4274_0', '4687_0',
                        '38087_0', '39520_0', '40922_0', '8874_0', '42153_0', '11110_0', '47279_0',
                        '14532_0', '15627_0', '48942_0', '49954_0', '50325_1', '50329_0', '17564_0',
                        '18060_0', '18418_0', '51251_0', '51715_0', '51815_0', '20085_0', '21308_0',
                        '21318_0', '21373_0', '21374_1', '21867_0', '55831_0', '24926_0', '57988_0',
                        '25739_0', '58707_0', '26830_0', '26851_0', '27907_0', '28088_0', '28376_0',
                        '29824_0']

    def __init__(self):
        pass

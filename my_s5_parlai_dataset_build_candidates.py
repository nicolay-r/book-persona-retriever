from core.utils_parlai_facebook_formatter import create_candidates_dict
from utils_my import MyAPI


my_api = MyAPI()
d = create_candidates_dict(my_api, dataset_filepath=my_api.dataset_filepath, limit_per_book=1000)
print("Books considered: {}".format(len(d)))
print("Candidates per book: {}".format(
    round(sum([len(candidates) for candidates in d.values()]) / len(d), 2)
))

from utils_gd import GuttenbergDialogApi
from utils_my import MyAPI


gd_api = GuttenbergDialogApi()
my_api = MyAPI()

dialog_segments_iter = gd_api.iter_dialog_segments(
    book_path_func=my_api.get_book_path,
    split_meta=True)

for k in dialog_segments_iter:
    print(k)
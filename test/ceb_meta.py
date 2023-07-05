from utils_ceb import CEBApi

# reading char_map
ceb_api = CEBApi()
ceb_api.read_char_map()
print(ceb_api.get_meta_gender())
print(ceb_api.get_meta_role())

def iter_parse_chatgpt4_1106_em(src):
    """ Parse Empathy mappings from the ChatGPT-4 responses.
    """
    with open(src, "r") as f:
        for line in f.readlines():
            # Skipping comment.
            line = line.strip()
            if line[0] == '#':
                continue
            # Setup category.
            if line[-1] == ':':
                cat = line
                continue
            else:
                yield cat, line


def iter_parse_mistral_parse_em(text, line_to_cat_func):
    assert(callable(line_to_cat_func))

    cat = None
    cats = set()
    for line in text.split("\n"):
        line = line.strip()
        if len(line) < 1:
            continue
        if line[-1] == ':':
            cat = line_to_cat_func(line)
            if cat is None:
                continue
            cats.add(cat)
            continue
        elif cat in cats:
            em_instance = mistral_clear_em_instance(line)
            if em_instance is not None:
                yield cat, em_instance


def mistral_clear_em_instance(text):

    text = text.replace('</s>', '')
    if len(text) > 0 and text[0] in ["*", '+']:
        text = text[1:].strip()
    if len(text) > 0 and text[-1] == '.':
        text = text[:-1]
    if text.lower() in ["none", "none specified", "none mentioned"]:
        return None
    if "none specified" in text.lower():
        return None
    if "none mentioned" in text.lower():
        return None
    if "overall," in text.lower():
        return None

    return text

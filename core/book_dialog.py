from utils_ceb import CEBApi


class BookDialogueService:

    def __init__(self):
        self.__book_id = None
        self.__book_text = None
        self.__lines = None
        self.__l_from = None
        self.__l_to = None
        self.__paragraph = None
        self.__dialog_utterances = []
        self.__missed = 0
        self.__found = 0

        # map (utt_id => segments)
        self.__segment_bounds = {}

    def set_book(self, book_id, ceb_api):
        assert(isinstance(ceb_api, CEBApi))

        # If already read this book and it is cached.
        if self.__book_id == book_id:
            return

        self.__book_id = book_id
        book_path = ceb_api.get_book_path(book_id)
        with open(book_path, "r") as b:
            text = b.read()

        self.__lines = text.split('\n')

    def stat(self):
        return self.__missed, self.__found

    def set_paragraphs(self, l_from, l_to):

        # check if cached.
        if l_from is not None and \
                l_to is not None and \
                l_from == self.__l_from and \
                l_to == self.__l_to:
            return self.__paragraph

        # Reinit from scratch and clear dependencies.
        self.__l_from = l_from
        self.__l_to = l_to
        self.__paragraph = ' '.join([l.strip() for l in self.__lines[int(l_from):int(l_to)+1]])
        self.__paragraph = ' '.join(self.__paragraph.split())

        self.__dialog_utterances.clear()
        self.__missed = 0
        self.__found = 0

    def register_utterance(self, utt, l_from, l_to):
        """ Add one utterance during the reading stage.
        """
        assert(l_from == self.__l_from and l_to == self.__l_to)
        self.__dialog_utterances.append(utt)

    def __reg_segment(self, u_ind, segment, b_ind):
        """register utterance segment with index `u_ind`, entered at `b_ind`"""
        if u_ind not in self.__segment_bounds:
            self.__segment_bounds[u_ind] = []
        self.__segment_bounds[u_ind].append((b_ind, b_ind + len(segment)))

    def annotate_dialog(self):
        """ The problem is that in streaming mode it might be challenging to
            annotate text around utterances. with the code below we perform
            annotation considering an already extracted paragraphs with the
            list of utterances mentioned in it.
        """
        self.__segment_bounds.clear()

        # index from which we will seek for the upcomming entry.
        curr_index = 0

        # for each utterance.
        for utt_ind, utterance in enumerate(self.__dialog_utterances):

            # to segments.
            segments = [u.strip() for u in utterance.split("[USEP]")]

            for i, utt_segment in enumerate(segments):

                b_ind = self.__paragraph.index(utt_segment, curr_index) \
                    if utt_segment in self.__paragraph else None

                if b_ind is not None:
                    self.__reg_segment(u_ind=utt_ind, segment=utt_segment, b_ind=b_ind)
                    curr_index = b_ind
                    self.__found += 1
                else:
                    self.__missed += 1
                    print(">>>")
                    print(self.__book_id)
                    print(utt_segment)
                    print(utt_segment in self.__paragraph)

        # Clear empty bounds and utterances.
        s_inds = list(self.__segment_bounds.keys())
        for i in s_inds:
            if len(self.__segment_bounds[i]) == 0:
                del self.__segment_bounds[i]

        annot_data = []

        # compose parts
        utt_ids = list(sorted(self.__segment_bounds.keys()))
        for utt_ind, utt_id in enumerate(utt_ids):
            # we extract
            # [SPAN#1] [BETWEEN#1] [SPAN#2] [BETWEEN#2] ... [SPAN#N] [AFTER#N]
            segments = self.__segment_bounds[utt_id]
            for seg_ind, seg_bounds in enumerate(segments):

                # add UTT.
                annot_data.append(
                    ">{utt_id}: {text}".format(utt_id=utt_id, text=self.__paragraph[seg_bounds[0]:seg_bounds[1]]))

                is_after = False
                text_start = seg_bounds[1] + 1
                if seg_ind < len(segments) - 1:
                    # Not the last segment, we are in between.
                    text_end = segments[seg_ind + 1][0] - 1
                else:
                    # This is the last segment
                    # We need to check whether the next utterance is on a way.
                    if utt_ind < len(utt_ids) - 1:
                        # Yes, there is a next utterance.
                        utt_id_next = utt_ids[utt_ind + 1]
                        text_end = self.__segment_bounds[utt_id_next][0][0] - 1
                    else:
                        # Seek for seek for the end of sentence.
                        is_after = True
                        try:
                            text_end = self.__paragraph.index('.', text_start + 1)
                        except ValueError:
                            # Considering the rest of paragraph.
                            text_end = len(self.__paragraph)

                # Filter non significant cases.
                text = self.__paragraph[text_start:text_end].strip()
                if len(text) < 2:
                    continue

                # Annotate text.
                annot_data.append(
                    "{t}{utt_id}: {text}".format(
                        t="." if is_after else "#",
                        utt_id=utt_id,
                        text=text))

        return annot_data

from collections import Counter
from functools import cmp_to_key

from api.ldc import LdcAPI


def filter_response_speakers(dialogue_qr_pairs_it):
    """ Filtering algorithm of the speakers considered for the result dataset.
    """

    def __compare(a, b):
        av = speaker_entries[a]
        bv = speaker_entries[b]
        if av < bv:
            return -1
        elif av > bv:
            return 1
        else:
            if a == b:
                raise Exception("Similar IDs")
            return -1 if a < b else 1

    speaker_ids = set()
    speaker_entries = Counter()
    for r_speaker_id, _ in dialogue_qr_pairs_it:
        speaker_entries[r_speaker_id] += 1
        speaker_ids.add(r_speaker_id)

    # Optional parameter. Keep the most frequent.
    if LdcAPI.dataset_filter_speaker_total_speakers_count is not None:
        ordered_speaker_ids = sorted(speaker_ids,
                                     key=cmp_to_key(lambda a, b: (__compare(a, b))),
                                     reverse=True)
        print(f"\nMost Frequent speakers (total): {len(ordered_speaker_ids)}")
        print("\n".join(["{}: {}".format(sid, speaker_entries[sid]) for sid in ordered_speaker_ids]))
        speaker_ids = ordered_speaker_ids[:LdcAPI.dataset_filter_speaker_total_speakers_count]
        predefined_ids = ordered_speaker_ids[LdcAPI.dataset_filter_speaker_total_speakers_count:
                                             LdcAPI.dataset_filter_speaker_total_speakers_count + LdcAPI.dataset_predefined_speakers_count]
        print(f"Predefined Speakers (total): {len(predefined_ids)}")
        print(", ".join(predefined_ids))

    for speaker_id in speaker_ids:

        entries = speaker_entries[speaker_id]

        # Optional check whether we meet the criteria of the min. amount of the utterances per speaker.
        if LdcAPI.dataset_filter_speaker_min_utterances_per_speaker is not None:
            if entries < LdcAPI.dataset_filter_speaker_min_utterances_per_speaker:
                continue

        yield speaker_id

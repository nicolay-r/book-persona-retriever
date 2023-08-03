from collections import Counter

from utils_my import MyAPI


def filter_response_speakers(dialogue_qr_pairs_it):
    """ Filtering algorithm of the speakers considered for the result dataset.
    """

    speaker_ids = set()
    speaker_entries = Counter()
    for r_speaker_id, _ in dialogue_qr_pairs_it:
        speaker_entries[r_speaker_id] += 1
        speaker_ids.add(r_speaker_id)

    # Optional parameter. Keep the most frequent.
    if MyAPI.dataset_filter_speaker_total_speakers_count is not None:
        ordered_speaker_ids = sorted(speaker_ids, key=lambda speaker_id: speaker_entries[speaker_id], reverse=True)
        speaker_ids = ordered_speaker_ids[:MyAPI.dataset_filter_speaker_total_speakers_count]

    for speaker_id in speaker_ids:

        entries = speaker_entries[speaker_id]

        # Optional check whether we meet the criteria of the min. amount of the utterances per speaker.
        if MyAPI.dataset_filter_speaker_min_utterances_per_speaker is not None:
            if entries < MyAPI.dataset_filter_speaker_min_utterances_per_speaker:
                continue

        yield speaker_id

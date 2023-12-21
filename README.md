# Book Processing Framework

This repository represents a core of the book processing aimed at dialogue extraction [algorithm]
for forming the related **datasets** of conversations between characters.
The content of dataset yields of dialogues, with utterances that **automatically annotated with speakers** [quotation annotations].

The directions this project was aimed at the following research directions:
* `e_pairs` -- extraction of dialogue pairs including speaker assignation
* `e_se_subin`  -- extraction of the speakers for utterances.
* `e_rag` -- extraction of utterances and contexts as well as forming character knowledge based for RAG and augmenting transformers.

For each direction we provide a pipeline (sequence of the separately ordered scripts) aimed at resource construction and evaluation.

**Limitation:** we consdier books from Project Gutenberg. We utilize CEB framework with pre-annotated and grouped speakers.
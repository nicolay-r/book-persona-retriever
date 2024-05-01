# Book Processing Framework

## Contents
* [Workflow](#workflow)
* [Research directions](#research-directions)
* [**Datasets**](#datasets)
* [**Experiments**](#experiments)
* [Dependencies](#dependencies)

## Workflow

This repository represents a core of the book processing aimed 
at [**automatic dialogue extraction**](https://arxiv.org/abs/2004.12752)
and allows forming **datasets** of conversations between characters.
The content of dataset yields of dialogues, with utterances that 
annotated with speakers 
([**quotation annotation**](https://github.com/dbamman/litbank?tab=readme-ov-file#quotation-annotations) problem,
[[paper]](https://arxiv.org/pdf/2004.13980.pdf)).

<p align="center">
    <img src="pics/pipeline_architecture.png" width="1000"/>
</p>

### Personalities
We also provide API for collection information on characters and composing their personalities in a vector form.
We adopt **spectrum** model for 
vectorizing characters representation, using 
[spectrums as features](https://github.com/tacookson/data/tree/master/fictional-character-personalities).
By provide [personalities factorization model](https://github.com/newpro/aloha-chatbot) 
over vectorized representation of characters:

<p align="center">
    <img src="pics/characters_embedding_visualization_tsne.png" width="350"/>
</p>

## Research Directions
The directions this project was aimed at the following research directions:
* `e_pairs` -- extraction of dialogue pairs including speaker assignation;
* `e_se`  -- extraction of the speakers for utterances, which is discovered by [Subin Jung](https://github.com/SubinJung-CS);
* `e_rag` -- extraction of utterances and contexts as well as forming character knowledge based for RAG and augmenting Large Languge Models (LLM).

For each direction we provide a pipeline (sequence of the separately ordered scripts) aimed at resource construction and evaluation.

# Datasets

* **[LDC](#ldc)**
  1. **[LDC-400-RP](#ldc-400-rp)**
  2. **[LDC-400-SR](#ldc-400-sr)**

## `LDC`

The common version of the resource dubbed as Literature Dialogue Collection (`LDC`).

It consists of dialogues extracted from 17K books of the Project Gutenberg platform.
This resource could be automatically constructed using the following steps:
1. [Downloading](download_data.py) all the necessary books 📚 and resources (Downloading takes: **~3.5 hours** ☕)
2. Executing the scripts from `e_pairs` directory.

We fine-cleaned dataset of dialogue pairs between `400` **most-frequently** appeared characters which results in `LDC-400` datasets.

## `LDC-400-RP`

This dataset if for the **Response Prediction** problem.

We utilize
[ParlAI](https://github.com/facebookresearch/ParlAI)
framework for conducting experiments.
In order to embed extracted data, we utilize the related data formatter. 

Link for **ParlAI** agents / task: [[parlai-agents]](https://github.com/nicolay-r/parlai_bookchar_task/blob/master/build.py)

**Candidates count:** 20

| Collection-type | Format | train                                                                                                                                             | valid                                                                                                                                             | test                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
|-----------------|--------|---------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **NO-HLA**      | ParlAI | [Train w/o HLA](https://www.dropbox.com/scl/fi/cmflno09yyvw70mpf4fli/dataset_parlai_train_original.txt.zip?rlkey=477zsekm5j0a4dpco0w9479uo&dl=1)  | [Valid w/o HLA](https://www.dropbox.com/scl/fi/508zfhxewvweqtn4k7hfg/dataset_parlai_valid_original.txt.zip?rlkey=3a0syeturb84lxtmizq1o5bsx&dl=1)  | Not Applicable                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| **HLA**-spectrum| ParlAI | [Train with HLA](https://www.dropbox.com/scl/fi/ax62dvkik12alxj604ute/dataset_parlai_train_spectrum.txt.zip?rlkey=xuvmvze6fnak413gst54qd4qz&dl=1) | [Valid with HLA](https://www.dropbox.com/scl/fi/lr96to0rzc6wpo84isscb/dataset_parlai_valid_spectrum.txt.zip?rlkey=5wrgtrtuulf3baxr724bcycdu&dl=1) | Five speakers: [[1]](https://www.dropbox.com/scl/fi/59pcnfytpckv34dbvm2x0/139_1.parlai_dataset.txt.zip?rlkey=c9fwoxbyta9f05f79l4bkym8o&dl=1) [[2]](https://www.dropbox.com/scl/fi/q07aph6we2x2wkwid65en/155_21.parlai_dataset.txt.zip?rlkey=qzs9cj4uk01vir2k46ztr7934&dl=1) [[3]](https://www.dropbox.com/scl/fi/214biikj5wianib7517ou/403_3.parlai_dataset.txt.zip?rlkey=qo6f7kr2mw6gafix467vl2cxe&dl=1) [[4]](https://www.dropbox.com/scl/fi/rhfukpgaxvpevqw4jnhmg/507_3.parlai_dataset.txt.zip?rlkey=6qcxui6a7mtc5b8xhp4zsoy7n&dl=1) [[5]](https://www.dropbox.com/scl/fi/07mp58p0fnw531tptdit4/1257_9.parlai_dataset.txt.zip?rlkey=1wesdzd1hqj668ztirh5yqidc&dl=1) |

> **NOTE:** [Please use `nicolay-r/parlai_bookchar_task` repository](https://github.com/nicolay-r/parlai_bookchar_task) on embedding task into ParlAI.
> All the resources below are automatically downloaded once the task is embedded into ParlAI framework. 

## `LDC-400-SR`

This dataset is for **Speaker Recognition** problem.

We utilize
[ParlAI](https://github.com/facebookresearch/ParlAI)
framework for conducting experiments.
In order to embed extracted data, we utilize the related data formatter. 

Link for **ParlAI** agents / task: [[parlai-agents]](https://github.com/nicolay-r/parlai_bookchar_task/blob/speaker-recognition-task/build.py)

**Candidates count:** 20

| Collection-type  | Format | train                                                                                                                                                      | valid                                                                                                                                                      | test                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
|------------------|--------|------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **HLA**-spectrum | ParlAI | [Train with HLA](https://www.dropbox.com/scl/fi/r241a1ma2douus965h7lf/dataset_parlai_train_hla.txt.zip?rlkey=dwcnm0yxn2boujomd53nx0595&dl=1) |[Valid with HLA](https://www.dropbox.com/scl/fi/arzub1tmegklkf93dthpr/dataset_parlai_valid_hla.txt.zip?rlkey=lpa8vcs48f3bxegk3gtw22h2i&dl=1)  | Five speakers: [[1]](https://www.dropbox.com/scl/fi/5gqbauw3bp3mnvkfkvh21/153_2.parlai_dataset.txt.zip?rlkey=a0rzgilfdq4vao7oy4cibt2ew&dl=1) [[2]](https://www.dropbox.com/scl/fi/0z1fwabtqv2fjsxdhjel1/403_3.parlai_dataset.txt.zip?rlkey=jsnymkkxs10b2j8r7ewfxpw6k&dl=1) [[3]](https://www.dropbox.com/scl/fi/w2y28hhpkral36uk5rby1/1257_7.parlai_dataset.txt.zip?rlkey=wm7mue848kzr4yubd7m9idpew&dl=1) [[4]](https://www.dropbox.com/scl/fi/8a56x1oviz15w4ppi1v9q/1257_9.parlai_dataset.txt.zip?rlkey=ysnibgk3j68nedtlp3g6oc2ew&dl=1) [[5]](https://www.dropbox.com/scl/fi/vpeq6r29zoja352eabe99/1258_8.parlai_dataset.txt.zip?rlkey=f8y9261af2bu1pameffw14bzc&dl=1) |

> **NOTE:** [Please use `nicolay-r/parlai_bookchar_task` repository](https://github.com/nicolay-r/parlai_bookchar_task) on embedding task into ParlAI.
> All the resources below are automatically downloaded once the task is embedded into ParlAI framework.

## Experiments
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nicolay-r/deep-book-processing/blob/master/parlai_gutenberg_experiments.ipynb)


## Dependencies 

We consider books from [Project Gutenberg](https://www.gutenberg.org/).

We utilize:
* [CEB-framework](https://github.com/naoya-i/charembench) -- pre-annotated and grouped speakers from **Project Gutenberg**. [[paper]]()
* [gutenberg-dialog](https://github.com/ricsinaruto/gutenberg-dialog) -- automatic dialogue annotation algorithm [[paper]]()

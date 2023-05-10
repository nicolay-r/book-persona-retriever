import unittest
from os.path import join, dirname

from arekit.common.data.input.providers.label.multiple import MultipleLabelProvider
from arekit.common.data.input.providers.rows.samples import BaseSampleRowProvider
from arekit.common.data.input.providers.text.single import BaseSingleTextProvider
from arekit.common.entities.base import Entity
from arekit.common.experiment.data_type import DataType
from arekit.common.folding.nofold import NoFolding
from arekit.common.labels.base import NoLabel
from arekit.common.labels.provider.constant import ConstantLabelProvider
from arekit.common.labels.scaler.single import SingleLabelScaler
from arekit.common.opinions.annot.algo.pair_based import PairBasedOpinionAnnotationAlgorithm
from arekit.common.pipeline.base import BasePipeline
from arekit.common.pipeline.items.base import BasePipelineItem
from arekit.common.text.parser import BaseTextParser
from arekit.contrib.bert.terms.mapper import BertDefaultStringTextTermsMapper
from arekit.contrib.utils.data.storages.row_cache import RowCacheStorage
from arekit.contrib.utils.data.writers.csv_native import NativeCsvWriter
from arekit.contrib.utils.entities.formatters.str_display import StringEntitiesDisplayValueFormatter
from arekit.contrib.utils.io_utils.samples import SamplesIO
from arekit.contrib.utils.pipelines.items.sampling.bert import BertExperimentInputSerializerPipelineItem
from arekit.contrib.utils.pipelines.items.text.terms_splitter import TermsSplitterParser
from arekit.contrib.utils.pipelines.text_opinion.extraction import text_opinion_extraction_pipeline
from arekit.contrib.utils.pipelines.text_opinion.filters.distance_based import DistanceLimitedTextOpinionFilter


class CEBTextEntitiesParser(BasePipelineItem):
    """ TODO! Customize text entities parser.
    """

    def __init__(self):
        super(CEBTextEntitiesParser, self).__init__()

    @staticmethod
    def __process_word(word):
        assert(isinstance(word, str))

        # If this is a special word which is related to the [entity] mention.
        if word[0] == "[" and word[-1] == "]":
            entity = Entity(value=word[1:-1], e_type=None)
            return entity

        return word

    def apply_core(self, input_data, pipeline_ctx):
        assert(isinstance(input_data, list))
        return [self.__process_word(w) for w in input_data]


__output_dir = join(dirname(__file__), "out")

terms_mapper = BertDefaultStringTextTermsMapper(
    entity_formatter=StringEntitiesDisplayValueFormatter())

text_provider = BaseSingleTextProvider(terms_mapper)

sample_rows_provider = BaseSampleRowProvider(
    label_provider=MultipleLabelProvider(SingleLabelScaler(NoLabel())),
    text_provider=text_provider)

writer = NativeCsvWriter()
samples_io = SamplesIO(__output_dir, writer, target_extension=".tsv.gz")

pipeline = BasePipeline([
    BertExperimentInputSerializerPipelineItem(
        sample_rows_provider=sample_rows_provider,
        samples_io=samples_io,
        save_labels_func=lambda data_type: True,
        balance_func=lambda data_type: data_type == DataType.Train,
        storage=RowCacheStorage())
])

#####
# Declaring pipeline related context parameters.
#####
no_folding = NoFolding(doc_ids=[0, 1], supported_data_type=DataType.Train)

# TODO. Take documents operation from ARElight
# https://github.com/nicolay-r/ARElight/blob/b147353c4c88ce28c605e3ab536a665cdda49656/arelight/doc_ops.py#L4
# But in ARElight it is in Memory, which means that it is consider all the texts to be provided in RAM.
# we need to keep only paths to files and read files when it is necessary.
doc_ops = FooDocumentOperations()

text_parser = BaseTextParser(pipeline=[
    CEBTextEntitiesParser(),
    TermsSplitterParser(),
    ])

train_pipeline = text_opinion_extraction_pipeline(
    annotators=[PairBasedOpinionAnnotationAlgorithm(
        dist_in_terms_bound=100, label_provider=ConstantLabelProvider(NoLabel()))],
    text_opinion_filters=[DistanceLimitedTextOpinionFilter(terms_per_context=100)],
    get_doc_func=lambda doc_id: doc_ops.get_doc(doc_id),
    text_parser=text_parser)
#####

pipeline.run(input_data=None,
             params_dict={
                 "data_folding": no_folding,
                 "data_type_pipelines": {DataType.Train: train_pipeline}
             })
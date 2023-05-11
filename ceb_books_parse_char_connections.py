from os import listdir
from os.path import join, isfile

from arekit.common.data.input.providers.label.multiple import MultipleLabelProvider
from arekit.common.data.input.providers.rows.samples import BaseSampleRowProvider
from arekit.common.data.input.providers.text.single import BaseSingleTextProvider
from arekit.common.entities.base import Entity
from arekit.common.experiment.api.ops_doc import DocumentOperations
from arekit.common.experiment.data_type import DataType
from arekit.common.folding.nofold import NoFolding
from arekit.common.labels.base import NoLabel
from arekit.common.labels.provider.constant import ConstantLabelProvider
from arekit.common.labels.scaler.single import SingleLabelScaler
from arekit.common.news.base import News
from arekit.common.news.sentence import BaseNewsSentence
from arekit.common.opinions.annot.algo.pair_based import PairBasedOpinionAnnotationAlgorithm
from arekit.common.opinions.collection import OpinionCollection
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
from arekit.contrib.utils.pipelines.text_opinion.annot.algo_based import AlgorithmBasedTextOpinionAnnotator
from arekit.contrib.utils.pipelines.text_opinion.extraction import text_opinion_extraction_pipeline
from arekit.contrib.utils.pipelines.text_opinion.filters.distance_based import DistanceLimitedTextOpinionFilter
from arekit.contrib.utils.synonyms.simple import SimpleSynonymCollection

from utils_my import MyAPI


class FilesDocOperations(DocumentOperations):
    """ Document Operations based on the list of provided file paths.
    """

    def __init__(self, file_paths=None, sentence_parser=None):
        """
            file_paths: list
                list of file paths related to documents.
            sentence_splitter: object
                how data is suppose to be separated onto sentences.
                str -> list(str)
        """

        assert(isinstance(file_paths, list) or file_paths is None)
        assert(callable(sentence_parser) or sentence_parser is None)

        self.__docs_paths = file_paths

        # Line-split sentence parser by default.
        self.__sentence_parser = lambda text: [t.strip() for t in text.split('\n')] \
            if sentence_parser is None else sentence_parser

    def __read_doc(self, doc_id, contents):
        """ input_data: list
        """

        # setup input data.
        sentences = self.__sentence_parser(contents)
        sentences = list(map(lambda text: BaseNewsSentence(text), sentences))

        # Parse text.
        return News(doc_id=doc_id, sentences=sentences)

    def get_doc(self, doc_id):
        """ Perform reading operation of the document.
        """
        with open(self.__docs_paths[doc_id], "r") as f:
            contents = f.read()
            return self.__read_doc(doc_id=doc_id, contents=contents)


class CEBTextEntitiesParser(BasePipelineItem):
    """ Text includes the following entries: {12_5_0}
    """

    def __init__(self):
        super(CEBTextEntitiesParser, self).__init__()

    @staticmethod
    def __process_word(word):
        assert(isinstance(word, str))

        # If this is a special word which is related to the [entity] mention.
        if word[0] == "{" and word[-1] == "}":
            entity = Entity(value=word[1:-1], e_type="PERSON")
            return entity

        return word

    def apply_core(self, input_data, pipeline_ctx):
        assert(isinstance(input_data, list))
        return [self.__process_word(w) for w in input_data]


#########################################
# Input parameters
#########################################
in_dir = MyAPI.books_storage_en
out_dir = MyAPI.books_storage
#########################################

terms_mapper = BertDefaultStringTextTermsMapper(
    entity_formatter=StringEntitiesDisplayValueFormatter())

text_provider = BaseSingleTextProvider(terms_mapper)

sample_rows_provider = BaseSampleRowProvider(
    label_provider=MultipleLabelProvider(SingleLabelScaler(NoLabel())),
    text_provider=text_provider)

writer = NativeCsvWriter()
samples_io = SamplesIO(out_dir, writer, target_extension=".csv")

pipeline = BasePipeline([
    BertExperimentInputSerializerPipelineItem(
        sample_rows_provider=sample_rows_provider,
        samples_io=samples_io,
        save_labels_func=lambda data_type: True,
        balance_func=lambda _: False,
        storage=RowCacheStorage())
])

#####
# Declaring pipeline related context parameters.
#####
no_folding = NoFolding(doc_ids=[0, 1], supported_data_type=DataType.Train)

doc_ops = FilesDocOperations(file_paths=[join(in_dir, f) for f in listdir(in_dir) if isfile(join(in_dir, f))])

text_parser = BaseTextParser(pipeline=[
    TermsSplitterParser(),
    CEBTextEntitiesParser(),
    ])

synonyms = SimpleSynonymCollection(iter_group_values_lists=[], is_read_only=False, debug=False)
train_pipeline = text_opinion_extraction_pipeline(
    annotators=[
        AlgorithmBasedTextOpinionAnnotator(
            annot_algo=PairBasedOpinionAnnotationAlgorithm(
                dist_in_terms_bound=200,
                label_provider=ConstantLabelProvider(NoLabel())),
            value_to_group_id_func=lambda value: '_'.join(value.split('_')[:2]),  # doc_char_var -> doc_char
            get_doc_existed_opinions_func=lambda _: OpinionCollection(synonyms),
            create_empty_collection_func=lambda: OpinionCollection(synonyms))
    ],
    text_opinion_filters=[DistanceLimitedTextOpinionFilter(terms_per_context=100)],
    get_doc_func=lambda doc_id: doc_ops.get_doc(doc_id),
    text_parser=text_parser)
#####

pipeline.run(input_data=None,
             params_dict={
                 "data_folding": no_folding,
                 "data_type_pipelines": {DataType.Train: train_pipeline}
             })
from os import listdir
from os.path import join, isfile

from arekit.common.data import const
from arekit.common.data.input.providers.label.multiple import MultipleLabelProvider
from arekit.common.data.input.providers.rows.samples import BaseSampleRowProvider
from arekit.common.data.input.providers.text.single import BaseSingleTextProvider
from arekit.common.entities.base import Entity
from arekit.common.experiment.data_type import DataType
from arekit.common.folding.nofold import NoFolding
from arekit.common.labels.base import NoLabel
from arekit.common.labels.provider.constant import ConstantLabelProvider
from arekit.common.labels.scaler.single import SingleLabelScaler
from arekit.common.news.parsed.base import ParsedNews
from arekit.common.news.parsed.providers.entity_service import EntityServiceProvider
from arekit.common.news.parsed.term_position import TermPositionTypes
from arekit.common.opinions.annot.algo.pair_based import PairBasedOpinionAnnotationAlgorithm
from arekit.common.opinions.collection import OpinionCollection
from arekit.common.pipeline.base import BasePipeline
from arekit.common.pipeline.items.base import BasePipelineItem
from arekit.common.text.parser import BaseTextParser
from arekit.common.text_opinions.base import TextOpinion
from arekit.contrib.bert.terms.mapper import BertDefaultStringTextTermsMapper
from arekit.contrib.utils.data.doc_ops.dir_based import DirectoryFilesDocOperations
from arekit.contrib.utils.data.storages.row_cache import RowCacheStorage
from arekit.contrib.utils.data.writers.csv_native import NativeCsvWriter
from arekit.contrib.utils.entities.formatters.str_display import StringEntitiesDisplayValueFormatter
from arekit.contrib.utils.io_utils.samples import SamplesIO
from arekit.contrib.utils.pipelines.items.sampling.bert import BertExperimentInputSerializerPipelineItem
from arekit.contrib.utils.pipelines.items.text.terms_splitter import TermsSplitterParser
from arekit.contrib.utils.pipelines.text_opinion.annot.algo_based import AlgorithmBasedTextOpinionAnnotator
from arekit.contrib.utils.pipelines.text_opinion.extraction import text_opinion_extraction_pipeline
from arekit.contrib.utils.pipelines.text_opinion.filters.base import TextOpinionFilter
from arekit.contrib.utils.pipelines.text_opinion.filters.distance_based import DistanceLimitedTextOpinionFilter
from arekit.contrib.utils.synonyms.simple import SimpleSynonymCollection

from utils_ceb import CEBApi
from utils_my import MyAPI


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


class DirectionFilter(TextOpinionFilter):

    def filter(self, text_opinion, parsed_news, entity_service_provider):
        assert(isinstance(text_opinion, TextOpinion))
        assert(isinstance(parsed_news, ParsedNews))
        assert(isinstance(entity_service_provider, EntityServiceProvider))
        s = entity_service_provider.get_entity_position(text_opinion.SourceId)
        t = entity_service_provider.get_entity_position(text_opinion.TargetId)

        s_s = s.get_index(TermPositionTypes.SentenceIndex)
        t_s = s.get_index(TermPositionTypes.SentenceIndex)
        if t_s < s_s:
            return False

        s_t = s.get_index(TermPositionTypes.IndexInSentence)
        t_t = t.get_index(TermPositionTypes.IndexInSentence)
        return t_t > s_t


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
        storage=RowCacheStorage(force_collect_columns=[const.SENT_IND]))
])

#####
# Declaring pipeline related context parameters.
#####
ceb_api = CEBApi()
doc_ops = DirectoryFilesDocOperations(
    dir_path=in_dir,
    file_names=[f for f in listdir(in_dir) if isfile(join(in_dir, f))],
    sentence_parser=lambda t: [p.Text for p in ceb_api.iter_book_paragraphs(t)])

no_folding = NoFolding(doc_ids=range(len(doc_ops)), supported_data_type=DataType.Train)

text_parser = BaseTextParser(pipeline=[
    TermsSplitterParser(),
    CEBTextEntitiesParser(),
    ])

synonyms = SimpleSynonymCollection(iter_group_values_lists=[], is_read_only=False)
train_pipeline = text_opinion_extraction_pipeline(
    annotators=[
        AlgorithmBasedTextOpinionAnnotator(
            annot_algo=PairBasedOpinionAnnotationAlgorithm(
                dist_in_terms_bound=200,
                label_provider=ConstantLabelProvider(NoLabel())),
            value_to_group_id_func=lambda value: '_'.join(value.split('_')[:2]),  # doc_char_var -> doc_char
            create_empty_collection_func=lambda: OpinionCollection(synonyms))
    ],
    text_opinion_filters=[
        DistanceLimitedTextOpinionFilter(terms_per_context=100),
        DirectionFilter()
    ],
    get_doc_by_id_func=doc_ops.get_doc,
    text_parser=text_parser)
#####

pipeline.run(input_data=None,
             params_dict={
                 "data_folding": no_folding,
                 "data_type_pipelines": {DataType.Train: train_pipeline}
             })
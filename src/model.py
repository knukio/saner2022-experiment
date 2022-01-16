from enum import Enum

import gensim

import Setting


class ModelType(Enum):
    # word embedding model
    GLOVE_300 = "glove-wiki-gigaword-300.bin"
    GLOVE_50 = "glove-wiki-gigaword-50.bin"
    FASTTEXT_300 = "fasttext.bin"
    FASTTEXT_300_SMALL = "wiki-news-300d-1M-subword.bin"
    WORD2VEC_300 = "word2-vec-GoogleNews-vectors-negative300.bin"


class Model:
    def __init__(self, model_type: ModelType):
        filePath = Setting.MODEL_LOCATION + "/" + model_type.value
        if model_type in [ModelType.FASTTEXT_300, ModelType.FASTTEXT_300_SMALL]:
            self.__model = gensim.models.fasttext.load_facebook_vectors(filePath)
        else:
            self.__model = gensim.models.KeyedVectors.load_word2vec_format(filePath, binary=True)
        self.__vocab = self.__model.wv

    @property
    def model(self):
        return self.__model

    @property
    def vocab(self):
        return self.__vocab

    def get_dimension(self):
        return self.__model.vector_size

    def get_vector(self, word):
        return self.__model[word]

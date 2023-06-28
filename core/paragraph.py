class Paragraph:
    """ Description of the paragraph.
    """

    def __init__(self, line_ind):
        """ Create emtpy paragraph.
        """
        self.__line_from = line_ind
        self.__line_to = line_ind
        self.__text = ""

    @property
    def DisplayBounds(self):
        return "[{}-{}]".format(self.__line_from, self.__line_to)

    @property
    def Text(self):
        return self.__text

    @property
    def LineFrom(self):
        return self.__line_from

    @property
    def LineTo(self):
        return self.__line_to

    def extend(self, line, line_ind):
        assert(line_ind >= self.__line_from)
        self.__text += line
        self.__line_to = line_ind

    def num_words(self):
        return len(self.__text.split())

    def modify_text(self, f):
        assert(callable(f))
        self.__text = f(self.__text)

    def __contains__(self, item):
        return item in self.__text

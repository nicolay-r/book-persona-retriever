import numpy as np
import zipstream


class NpzUtils(object):

    @staticmethod
    def save(data, target):
        np.savez(target, data)

    @staticmethod
    def load(source):
        data = np.load(source)
        return data['arr_0']


def save_zip_stream(target, inner_filename, data_it):
    """ Saving data iterator into zip file.
    """

    z = zipstream.ZipFile()
    z.write_iter(inner_filename, data_it)

    with open(target, "wb") as f:
        for line in z:
            f.write(line)

    print("Saved: {}".format(target))

from collections import namedtuple
import numpy as np
import os
import urllib
from tensorflow.contrib.learn.python.learn.datasets.mnist import DataSet
from nn_utils import whiten

DATASETS_DIR = 'data'
DATASET_TYPES = ['train', 'valid', 'test']


def create_binarized_mnist(which):
    print('Creating binarized %s dataset' % which)
    file_path = DATASETS_DIR + '/binarized_mnist_{}.amat'.format(which)

    # Download dataset if necessary
    if not os.path.isfile(file_path):
        if not os.path.exists(DATASETS_DIR):
            os.makedirs(DATASETS_DIR)
        url = 'http://www.cs.toronto.edu/~larocheh/public/datasets/binarized_mnist/binarized_mnist_{}.amat'.format(which)
        urllib.urlretrieve(url, file_path)
        print('Downloaded %s to %s' % (url, file_path))
    with open(file_path) as f:
        data = [l.strip().split(' ') for l in f.readlines()]
        data = np.array(data).astype(int)
        np.save(DATASETS_DIR + '/binarized_mnist_{}.npy'.format(which), data)
    return data


def binarized_mnist():
    # Download and create datasets if necessary
    for which in DATASET_TYPES:
        if not os.path.isfile(os.path.join(DATASETS_DIR, 'binarized_mnist_{}.npy'.format(which))):
            create_binarized_mnist(which)
    dataset = {which: UnlabelledDataSet(np.load(DATASETS_DIR + '/binarized_mnist_{}.npy'.format(which)))
               for which in DATASET_TYPES}
    return dataset


class UnlabelledDataSet(object):
    def __init__(self,
                 images):
        self._num_examples = images.shape[0]
        self._images = images
        self._whitened_images = whiten(images)
        self._epochs_completed = 0
        self._index_in_epoch = 0

    @property
    def images(self):
        return self._images
    @property
    def whitened_images(self):
        return self._whitened_images
    @property
    def num_examples(self):
        return self._num_examples

    @property
    def epochs_completed(self):
        return self._epochs_completed

    def next_batch(self, batch_size, whitened=False):
        """Return the next `batch_size` examples from this data set."""
        start = self._index_in_epoch
        self._index_in_epoch += batch_size
        if self._index_in_epoch > self._num_examples:
            # Finished epoch
            self._epochs_completed += 1
            # Shuffle the data
            perm = np.arange(self._num_examples)
            np.random.shuffle(perm)
            self._images = self._images[perm]
            # Start next epoch
            start = 0
            self._index_in_epoch = batch_size
            assert batch_size <= self._num_examples
        end = self._index_in_epoch
        if whitened:
            return self.images[start:end], self._whitened_images[start:end]
        else: return self._images[start:end], self.images[start:end]
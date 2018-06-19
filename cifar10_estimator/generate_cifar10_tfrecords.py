# Copyright 2017 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Read CIFAR-10 data from pickled numpy arrays and writes TFRecords.

Generates tf.train.Example protos and writes them to TFRecord files from the
python version of the CIFAR-10 dataset downloaded from
https://www.cs.toronto.edu/~kriz/cifar.html.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import os
import sys

import tarfile
from six.moves import cPickle as pickle
from six.moves import xrange  # pylint: disable=redefined-builtin
import tensorflow as tf

CIFAR_FILENAME = 'cifar-10-python.tar.gz'
CIFAR_DOWNLOAD_URL = 'https://www.cs.toronto.edu/~kriz/' + CIFAR_FILENAME
CIFAR_LOCAL_FOLDER = 'cifar-10-batches-py'


def download_and_extract(data_dir):
  # download CIFAR-10 if not already downloaded.
  tf.contrib.learn.datasets.base.maybe_download(CIFAR_FILENAME, data_dir,
                                                CIFAR_DOWNLOAD_URL)
  tarfile.open(os.path.join(data_dir, CIFAR_FILENAME),
               'r:gz').extractall(data_dir)


def _int64_feature(value):
  return tf.train.Feature(int64_list=tf.train.Int64List(value=[value]))


def _bytes_feature(value):
  return tf.train.Feature(bytes_list=tf.train.BytesList(value=[value]))


def _get_file_names():
  """Returns the file names expected to exist in the input_dir."""
  file_names = {}
  file_names['train'] = ['data_batch_%d' % i for i in xrange(1, 5)]
  file_names['validation'] = ['data_batch_5']
  file_names['eval'] = ['test_batch']
  return file_names


def read_pickle_from_file(filename):
  with tf.gfile.Open(filename, 'rb') as f:
    if sys.version_info >= (3, 0):
      data_dict = pickle.load(f, encoding='bytes')
    else:
      data_dict = pickle.load(f)
  return data_dict


import numpy as np
from fft_noise import mask_random, mask_radial, apply_mask


# mode: train validate eval
def convert_to_tfrecord(input_files, output_file, mode, args = None):
  """Converts a file to TFRecords."""
  print('Generating %s' % output_file)
  with tf.python_io.TFRecordWriter(output_file) as record_writer:
    for input_file in input_files:
      data_dict = read_pickle_from_file(input_file)
      data = data_dict[b'data']
      labels = data_dict[b'labels']

      # data -- a 10000x3072 numpy array of uint8s. Each row of the array stores a 32x32 colour image. The first 1024 entries contain the red channel values, the next 1024 the green, and the final 1024 the blue. The image is stored in row-major order, so that the first 32 entries of the array are the red channel values of the first row of the image.

      if args is not None and args.radial_fft_noise > 0.0:
        mask = mask_radial((32,32),args.radial_fft_noise)
        for i in range(len(data)):
          img_r,img_g,img_b = data[i,:].reshape([3,32,32])
          img_r = (apply_mask(img_r.astype(float) / 255.0, mask) * 255).astype(np.uint8)
          img_g = (apply_mask(img_g.astype(float) / 255.0, mask) * 255).astype(np.uint8)
          img_b = (apply_mask(img_b.astype(float) / 255.0, mask) * 255).astype(np.uint8)
          data[i,:1024]     = img_r.reshape([1024])
          data[i,1024:2048] = img_g.reshape([1024])
          data[i,2048:]     = img_b.reshape([1024])

      if args is not None and args.random_fft_noise > 0.0:
        mask = mask_random((32,32),args.random_fft_noise)
        for i in range(len(data)):
          img_r,img_g,img_b = data[i,:].reshape([3,32,32])
          img_r = (apply_mask(img_r.astype(float) / 255.0, mask) * 255).astype(np.uint8)
          img_g = (apply_mask(img_g.astype(float) / 255.0, mask) * 255).astype(np.uint8)
          img_b = (apply_mask(img_b.astype(float) / 255.0, mask) * 255).astype(np.uint8)
          data[i,:1024]     = img_r.reshape([1024])
          data[i,1024:2048] = img_g.reshape([1024])
          data[i,2048:]     = img_b.reshape([1024])

      num_entries_in_batch = len(labels)
      for i in range(num_entries_in_batch):
        example = tf.train.Example(features=tf.train.Features(
            feature={
                'image': _bytes_feature(data[i].tobytes()),
                'label': _int64_feature(labels[i])
            }))
        record_writer.write(example.SerializeToString())


def main(data_dir,args):
  print('Download from {} and extract.'.format(CIFAR_DOWNLOAD_URL))
  download_and_extract(data_dir)
  file_names = _get_file_names()
  input_dir = os.path.join(data_dir, CIFAR_LOCAL_FOLDER)
  for mode, files in file_names.items():
    input_files = [os.path.join(input_dir, f) for f in files]
    output_file = os.path.join(data_dir, mode + '.tfrecords')
    try:
      os.remove(output_file)
    except OSError:
      pass
    # Convert to tf.train.Example and write the to TFRecords.
    # mode: train validate eval
    if mode == 'train':
        convert_to_tfrecord(input_files, output_file, mode, args)
    else:
        convert_to_tfrecord(input_files, output_file, mode)
  print('Done!')


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument(
      '--data-dir',
      type=str,
      default='',
      help='Directory to download and extract CIFAR-10 to.')
  parser.add_argument('--radial_fft_noise',type=float,default=11.0)
  parser.add_argument('--random_fft_noise',type=float,default=0.1)

  args = parser.parse_args()
  main(args.data_dir,args)

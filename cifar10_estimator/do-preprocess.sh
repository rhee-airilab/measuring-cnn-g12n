:
set -x
mkdir -p data/1 data/2 data3
python generate_cifar10_tfrecords.py --data-dir=${PWD}/../data/cifar10-1
python generate_cifar10_tfrecords.py --data-dir=${PWD}/../data/cifar10-2 --radial_fft_noise=11.0
python generate_cifar10_tfrecords.py --data-dir=${PWD}/../data/cifar10-3 --random_fft_noise=0.1

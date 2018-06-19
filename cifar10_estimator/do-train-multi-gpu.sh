:
set -x
mkdir -p ../logdir/cifar10-[123] ../data/cifar10-[123]
# train batch size 128, 60000 samples = 469 batch, 100 epoch ~ 47000 steps
python -u cifar10_main.py --data-dir=${PWD}/../data/cifar10-1 \
                       --job-dir=${PWD}/../logdir/cifar10-1 \
                       --num-gpus=8 \
                       --eval-batch-size=200 \
                       --train-steps=65000
python -u cifar10_main.py --data-dir=${PWD}/../data/cifar10-2 \
                       --job-dir=${PWD}/../logdir/cifar10-2 \
                       --num-gpus=8 \
                       --eval-batch-size=200 \
                       --train-steps=65000
python -u cifar10_main.py --data-dir=${PWD}/../data/cifar10-3 \
                       --job-dir=${PWD}/../logdir/cifar10-3 \
                       --num-gpus=8 \
                       --eval-batch-size=200 \
                       --train-steps=65000

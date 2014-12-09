SM = ('knn', 'ilo-gmm', 'imle')
IM = ('random', 'discretized_progress')
BABBLING = ('motor', 'goal')
N = 25

pbs = """
#!/bin/sh

#PBS -o logs/grid/std/{log}.output
#PBS -e logs/grid/std/{log}.error
#PBS -l walltime=5:00:0
#PBS -N ik-learning-{im}-{bab}-{sm}-{i}

cd xp/ik-learning/ik-learning
python ik.py --interest-model {im} --babbling-mode {bab} --sensorimotor-model {sm} --iteration {i}

"""

from subprocess import call


if __name__ == '__main__':
    for im in IM:
        for bab in BABBLING:
            for sm in SM:
                if ((im == 'discretized_progress' and bab == 'motor') or (sm == 'imle')):
                    print 'Skipping', im, bab, sm
                    continue

                for i in range(1, N + 1):
                    log = 'ik-xp-{}-{}-with-{}-{}'.format(im, bab, sm, i)

                    with open('/tmp/ik.pbs', 'w') as f:
                        f.write(pbs.format(log=log, im=im, bab=bab, sm=sm, i=i))

                    call(["qsub", "/tmp/ik.pbs"])

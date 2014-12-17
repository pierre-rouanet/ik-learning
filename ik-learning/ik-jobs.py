import os

N = 100

xp_conf = {
    'scene': 'poppy-flying.ttt',

    'bab': 'goal',
    'im': {'name': 'discretized_progress', 'conf': {'x_card': 400, 'win_size': 10}},
    'sm': {'name': 'knn', 'conf': {'sigma_ratio': 1 / 6.}},

    'eval_at': [5, 10, 20, 30, 40, 50, 100, 150,
                200, 250, 300, 400, 500, 600, 700, 800, 900, 1000,
                1250, 1500, 1750, 2000, 3000, 4000, 5000],
    'tc': 'tc-150.npy',

    'log_folder': 'logs/gridsearch',
    'log': 'dp-goal-knn-default-conf',
}

pbs = """
#!/bin/sh

#PBS -l walltime=10:00:0
#PBS -N dp-knn-{i}

cd xp/ik-learning/ik-learning
python ik.py -c {config} -i {i}

"""

from subprocess import call


if __name__ == '__main__':
    avakas = 'AVAKAS' in os.environ

    if not avakas:
        xp_conf['eval_at'] = [2, 5]
        xp_conf['tc'] = 'tc-3.npy'
        N = 2

    conf = '/tmp/xp.conf'
    with open(conf, 'w') as f:
        f.write(str(xp_conf))

    for i in range(N):
        if avakas:
            with open('/tmp/ik.pbs', 'w') as f:
                f.write(pbs.format(config=conf, i=i))

            call(["qsub", "/tmp/ik.pbs"])

        else:
            call(["python", "ik.py", "-c", conf, "-i", str(i)])



    # for im in IM:
    #     for bab in BABBLING:
    #         for sm in SM:
    #             if ((im == 'discretized_progress' and bab == 'motor') or (sm == 'imle')):
    #                 print 'Skipping', im, bab, sm
    #                 continue
    #
    #             for i in range(1, N + 1):
    #                 log = 'ik-xp-{}-{}-with-{}-{}'.format(im, bab, sm, i)
    #
    #                 with open('/tmp/ik.pbs', 'w') as f:
    #                     f.write(pbs.format(log=log, im=im, bab=bab, sm=sm, i=i))
    #
    #                 call(["qsub", "/tmp/ik.pbs"])

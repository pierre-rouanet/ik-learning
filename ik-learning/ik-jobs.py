import os
import argparse

N = 100

pbs = """
#!/bin/sh

#PBS -o stds/{name}-{i}.output
#PBS -e stds/{name}-{i}.error
#PBS -l walltime=10:00:0
#PBS -N {name}-{i}

cd xp/ik-learning/ik-learning
python ik.py -c {config} -i {i}

"""

from subprocess import call


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--test', action='store_true', default=False)
    args = parser.parse_args()

    avakas = 'AVAKAS' in os.environ

    xp_name = 'rm-knn'

    with open('config/{}.py'.format(xp_name)) as f:
        xp_conf = eval(f.read())

    if args.test:
        xp_conf['eval_at'] = [2, 5]
        xp_conf['tc'] = 'tc-3.npy'
        N = 2

    conf = '/tmp/xp-{}.conf'.format(xp_name)
    with open(conf, 'w') as f:
        f.write(str(xp_conf))

    for i in range(N):
        if avakas:
            with open('/tmp/ik.pbs', 'w') as f:
                f.write(pbs.format(name=xp_name, config=conf, i=i))

            call(["qsub", "/tmp/ik.pbs"])

        else:
            call(["python", "ik.py", "-c", conf, "-i", str(i)])

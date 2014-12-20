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

    xp_name = 'dpg-knn'

    with open('config/{}.py'.format(xp_name)) as f:
        xp_conf = eval(f.read())

    if args.test:
        xp_conf['eval_at'] = [2, 5]
        xp_conf['tc'] = 'tc-3.npy'
        N = 2

    for x_card in map(lambda x: x ** 3, [2, 3, 5, 7, 10, 16]):
        for win_size in [5, 10, 20, 50, 75, 100, 200]:
            name = '{}-xcard-{}-winsize-{}'.format(xp_name, x_card, win_size)
            xp_conf['log'] = name
            xp_conf['im']['conf'] = {'x_card': x_card, 'win_size': win_size}
            print 'Starting {} xp using {}'.format(N, xp_conf)

            conf = os.path.join(os.getcwd(), 'tmp', 'xp-{}.conf'.format(name))
            with open(conf, 'w') as f:
                f.write(str(xp_conf))

            for i in range(N):
                if (not args.test) and avakas:
                    with open('/tmp/ik.pbs', 'w') as f:
                        f.write(pbs.format(name=xp_name, config=conf, i=i + 1))

                    call(["qsub", "/tmp/ik.pbs"])

                else:
                    call(["python", "ik.py", "-c", conf, "-i", str(i)])

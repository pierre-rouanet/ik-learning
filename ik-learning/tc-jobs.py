N = 100

pbs = """
#!/bin/sh

#PBS -o tc/std/tc-{i}.output
#PBS -e tc/std/tc-{i}.error
#PBS -l walltime=1:30:0
#PBS -N tc-{i}

cd xp/ik-learning/ik-learning
python tc.py --iteration {i}

"""

from subprocess import call


if __name__ == '__main__':
    for i in range(N):
        with open('/tmp/tc.pbs', 'w') as f:
            f.write(pbs.format(i=i))

        call(["qsub", "/tmp/tc.pbs"])

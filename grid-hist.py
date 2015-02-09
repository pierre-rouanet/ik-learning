import os

os.chdir('ik-learning/logs/gridsearch/')


from glob import glob

xps = {}

xps['random motor'] = len(glob('rm-*'))
xps['random goal'] = len(glob('rg-*'))
xps['dp goal default'] = len(glob('dpg-knn-default-*'))

for xcard in [2**3, 3**3, 5**3, 7**3, 10**3, 16**3]:
    for ws in [5, 10, 20, 40, 75, 100, 200]:
        xps['dp goal {} {}'.format(xcard, ws)] = \
            len(glob('dpg-knn-xcard-{}-winsize-{}-*.logs'.format(xcard, ws)))

for k, v in xps.items():
    print k, ':', v

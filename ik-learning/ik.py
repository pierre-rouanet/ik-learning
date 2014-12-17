import os
import time
import pickle
import argparse

from numpy import array, load

from pyvrep.xp import VrepXp

from explauto.agent import Agent
from explauto.utils import bounds_min_max
from explauto.experiment import Experiment
from explauto.interest_model import interest_models
# from explauto.sensorimotor_model.imle import ImleModel
from explauto.sensorimotor_model.ilo_gmm import IloGmm
from explauto.environment.environment import Environment
from explauto.sensorimotor_model.nearest_neighbor import NearestNeighbor


sms = {
    'knn': NearestNeighbor,
    'ilo-gmm': IloGmm,
}

motors = ['l_hip_x', 'l_hip_z', 'l_hip_y', 'l_knee_y', 'l_ankle_y']
alias = 'l_leg'

env_conf = {
    'motors': alias,
    'move_duration': 1.,
    'm_mins': array([-180.] * len(motors)),
    'm_maxs': array([180.] * len(motors)),
    's_mins': array([-.5, -.5, -.5]),
    's_maxs': array([.5, .5, .5]),
}

avakas = 'AVAKAS' in os.environ


class VrepEnvironment(Environment):
    def __init__(self, robot, motors, move_duration,
                 m_mins, m_maxs, s_mins, s_maxs):
        Environment.__init__(self, m_mins, m_maxs, s_mins, s_maxs)

        self.robot = robot
        self.motors = [m.name for m in getattr(self.robot, motors)]
        self.move_duration = move_duration

    def compute_motor_command(self, m_ag):
        m_env = bounds_min_max(m_ag, self.conf.m_mins, self.conf.m_maxs)
        return m_env

    def compute_sensori_effect(self, m_env):
        pos = dict(zip(self.motors, m_env))
        self.robot.goto_position(pos, self.move_duration, wait=True)

        time.sleep(.5)

        io = self.robot._controllers[0].io
        pos = io.get_object_position('foot_left_visual', 'base_link_visual')
        # rot = io.get_object_orientation('foot_left_visual', 'base_link_visual')

        return pos  # + rot

    def reset(self):
        self.robot.reset_simulation()


class LearningIkXp(VrepXp):
    def __init__(self, conf):
        VrepXp.__init__(self, 'poppy', conf['scene'])

        self.xp_conf = conf

    def run(self):
        env = VrepEnvironment(self.robot, **env_conf)

        # Create the Interest Model
        im_dims = env.conf.m_dims if self.xp_conf['bab'] == 'motor' else env.conf.s_dims
        im_cls, im_conf = interest_models[self.xp_conf['im']['name']]
        im_conf = im_conf['default']
        im_conf.update(self.xp_conf['im']['conf'])
        print 'Create IM', self.xp_conf['im']['name'], 'using', im_conf
        im = im_cls(env.conf, im_dims, **im_conf)

        # Create the SensoriMotor Model
        sm_cls = sms[self.xp_conf['sm']['name']]
        print 'Create SM', self.xp_conf['sm']['name'], 'using', self.xp_conf['sm']['conf']
        sm = sm_cls(env.conf, **self.xp_conf['sm']['conf'])

        ag = Agent(env.conf, sm, im)

        self.xp = Experiment(env, ag)
        self.xp.evaluate_at(self.xp_conf['eval_at'], load(self.xp_conf['tc']))
        self.xp.run()

    def save(self, f):
        pickle.dump(self.xp.log, f)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('-c', '--config', type=str, required=True)
    parser.add_argument('-i', '--iteration', type=int, required=True)

    args = parser.parse_args()

    with open(args.config) as f:
        xp_conf = eval(f.read())

    log = '{}-{}.logs'.format(xp_conf['log'], args.iteration)
    log_folder = xp_conf['log_folder']

    log_file = os.path.join(log_folder, log)

    if not os.path.exists(log_folder):
        os.mkdir(log_folder)

    if os.path.exists(log_file):
        raise ValueError('Log already exists ({})!'.format(log_file))

    xp = LearningIkXp(xp_conf)

    t0 = time.time()

    if avakas:
        xp.spawn(log_file, avakas=True)
    else:
        xp.spawn(log_file, gui=True)

    print 'Ellapsed time', time.time() - t0

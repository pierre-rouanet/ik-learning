import os
import time
import pickle
import argparse

from numpy import array, load

from pyvrep.xp import VrepXp

from explauto.agent import Agent
from explauto import InterestModel
from explauto.utils import bounds_min_max
from explauto.experiment import Experiment
# from explauto.sensorimotor_model.imle import ImleModel
from explauto.sensorimotor_model.ilo_gmm import IloGmm
from explauto.environment.environment import Environment
from explauto.sensorimotor_model.nearest_neighbor import NearestNeighbor

log_folder = 'logs'
scene = 'poppy-flying.ttt'

sms = {
    'knn': (NearestNeighbor, {'sigma_ratio': 1. / 16}),
    # 'imle': (ImleModel, {}),
    'ilo-gmm': (IloGmm, {}),
}

motors = ['l_hip_x', 'l_hip_z', 'l_hip_y', 'l_knee_y', 'l_ankle_y']
alias = 'l_leg'

conf = {
    'motors': alias,
    'move_duration': 1.,
    'm_mins': array([-180.] * len(motors)),
    'm_maxs': array([180.] * len(motors)),
    's_mins': array([-.5, -.5, -.5]),
    's_maxs': array([.5, .5, .5]),
}

eval_at = [5, 10]#TODO:, 20, 30, 40, 50, 100, 150,
        #    200, 250, 300, 400, 500, 600, 700, 800, 900, 1000]

tc = load('tc-25.npy')[:3] # TODO !


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
    def __init__(self, im, bab, sm):
        VrepXp.__init__(self, 'poppy', scene)

        self.im_name, self.babbling, self.sm_name = im, bab, sm

    def run(self):
        env = VrepEnvironment(self.robot, **conf)

        im_dims = env.conf.m_dims if self.babbling == 'motor' else env.conf.s_dims
        im = InterestModel.from_configuration(env.conf, im_dims, self.im_name)

        sm_cls, kwargs = sms[self.sm_name]
        sm = sm_cls(env.conf, **kwargs)

        ag = Agent(env.conf, sm, im)

        self.xp = Experiment(env, ag)
        self.xp.evaluate_at(eval_at, tc)
        self.xp.run()

    def save(self, f):
        pickle.dump(self.xp.log, f)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--interest-model', type=str, required=True,
                        choices=('random', 'discretized_progress'))

    parser.add_argument('--babbling-mode', type=str, required=True,
                        choices=('motor', 'goal'))

    parser.add_argument('--sensorimotor-model', type=str, required=True,
                        choices=('knn', 'ilo-gmm', 'imle'))

    parser.add_argument('--iteration', type=int, required=True)

    args = parser.parse_args()

    log = 'ik-xp-{}-{}-with-{}-{}.logs'.format(args.interest_model, args.babbling_mode,
                                               args.sensorimotor_model, args.iteration)

    log_file = os.path.join(log_folder, log)

    if not os.path.exists(log_folder):
        os.mkdir(log_folder)

    if os.path.exists(log_file):
        raise ValueError('Log already exists ({})!'.format(log_file))

    xp = LearningIkXp(args.interest_model,
                      args.babbling_mode,
                      args.sensorimotor_model)

    t0 = time.time()
    xp.spawn(log_file, gui=True)
    print 'Ellapsed time', time.time() - t0

import os
import time
import argparse

from numpy import array, save

from pyvrep.xp import VrepXp

from explauto.agent import Agent
from explauto import InterestModel
from explauto.utils import bounds_min_max, rand_bounds
from explauto.environment.environment import Environment
from explauto.sensorimotor_model.nearest_neighbor import NearestNeighbor

N = 1000

log_folder = 'tc'
scene = 'poppy-flying.ttt'

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
    def __init__(self):
        VrepXp.__init__(self, 'poppy', scene)

    def run(self):
        env = VrepEnvironment(self.robot, **conf)

        im = InterestModel.from_configuration(env.conf, env.conf.m_dims, 'random')
        sm = NearestNeighbor(env.conf, sigma_ratio=1. / 16.)

        ag = Agent(env.conf, sm, im)

        m_rand = rand_bounds(env.conf.m_bounds, n=N)

        self.tc = []

        for i, m in enumerate(m_rand):
            mov = ag.motor_primitive(m)
            s = env.compute_sensori_effect(mov)

            self.tc.append(s)

            env.robot.reset_simulation()

    def save(self, f):
        save(f, self.tc)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--iteration', type=int, required=True)
    args = parser.parse_args()

    log = 'tc-{}.npy'.format(args.iteration)

    log_file = os.path.join(log_folder, log)

    if not os.path.exists(log_folder):
        os.mkdir(log_folder)

    if os.path.exists(log_file):
        raise ValueError('Log already exists ({})!'.format(log_file))

    xp = LearningIkXp()

    t0 = time.time()
    if avakas:
        xp.spawn(log_file, avakas=True)
    else:
        xp.spawn(log_file, gui=True)
    print 'Ellapsed time', time.time() - t0

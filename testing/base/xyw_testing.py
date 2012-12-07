#! /usr/bin/env python
"""
This script tests some of the base functionalities of MORSE.
"""

import sys
import socket
import json
import math
from time import sleep
from morse.testing.testing import MorseTestCase
from pymorse import Morse

# Include this import to be able to use your test file as a regular 
# builder script, ie, usable with: 'morse [run|exec] base_testing.py
try:
    from morse.builder import *
except ImportError:
    pass

def send_speed(s, x, y, w, t):
    s.send(json.dumps({'x' : x, 'y' : y, 'w' : w}).encode())
    sleep(t)
    s.send(json.dumps({'x' : 0.0, 'y' : 0.0, 'w' : 0.0}).encode())

class XYW_Test(MorseTestCase):
    def setUpEnv(self):
        """ Defines the test scenario, using the Builder API.
        """
        robot = Robot('atrv')

        pose = Sensor('pose')
        pose.translate(z=-0.10) # atrv base is 10cm over ground
        robot.append(pose)
        pose.configure_mw('socket')

        motion = Actuator('xy_omega')
        robot.append(motion)
        motion.configure_mw('socket')
        motion.configure_service('socket')
        
        env = Environment('empty', fastmode = True)
        env.configure_service('socket')

    def test_xyw_controller(self):
        with Morse() as morse:

            precision=0.05
        
            # Read the start position, it must be (0.0, 0.0, 0.0)
            pose_stream = morse.stream('Pose')
            pose = pose_stream.get()
            for coord in pose.values():
                self.assertAlmostEqual(coord, 0.0, delta=precision)

            # v_w socket
            port = morse.get_stream_port('Motion_Controller')
            xyw_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            xyw_client.connect(('localhost', port))

            send_speed(xyw_client, 1.0, 0.0, 0.0, 2.0)

            pose = pose_stream.get()
            self.assertAlmostEqual(pose['x'], 2.0, delta=precision)
            self.assertAlmostEqual(pose['y'], 0.0, delta=precision)
            self.assertAlmostEqual(pose['z'], 0.0, delta=precision)
            self.assertAlmostEqual(pose['yaw'], 0.0, delta=precision)
            self.assertAlmostEqual(pose['pitch'], 0.0, delta=precision)
            self.assertAlmostEqual(pose['roll'], 0.0, delta=precision)

            send_speed(xyw_client, 0.0, -1.0, 0.0, 2.0)
            pose = pose_stream.get()
            self.assertAlmostEqual(pose['x'], 2.0, delta=precision)
            self.assertAlmostEqual(pose['y'], -2.0, delta=precision)
            self.assertAlmostEqual(pose['z'], 0.0, delta=precision)
            self.assertAlmostEqual(pose['yaw'], 0.0, delta=precision)
            self.assertAlmostEqual(pose['pitch'], 0.0, delta=precision)
            self.assertAlmostEqual(pose['roll'], 0.0, delta=precision)

            send_speed(xyw_client, -1.0, 1.0, 0.0, 2.0)

            pose = pose_stream.get()
            for coord in pose.values():
                self.assertAlmostEqual(coord, 0.0, delta=precision)

            send_speed(xyw_client, 1.0, 0.0, -math.pi/4.0, 2.0)
            pose = pose_stream.get()

            # for non-null w, we have r = v /  w
            self.assertAlmostEqual(pose['x'], 4.0/ math.pi , delta=precision)
            self.assertAlmostEqual(pose['y'], -4.0/ math.pi , delta=precision)
            self.assertAlmostEqual(pose['z'], 0.0, delta=precision)
            self.assertAlmostEqual(pose['yaw'], -math.pi/2.0, delta=precision)
            self.assertAlmostEqual(pose['pitch'], 0.0, delta=precision)
            self.assertAlmostEqual(pose['roll'], 0.0, delta=precision)

            send_speed(xyw_client, 0.5, 0.0, -math.pi/8.0, 12.0)

            pose = pose_stream.get()
            for coord in pose.values():
                self.assertAlmostEqual(coord, 0.0, delta=precision)

            send_speed(xyw_client, -2.0, 0.0, math.pi/2.0, 3.0)
            pose = pose_stream.get()
            self.assertAlmostEqual(pose['x'], 4.0/ math.pi , delta=0.1)
            self.assertAlmostEqual(pose['y'], -4.0/ math.pi , delta=0.1)
            self.assertAlmostEqual(pose['z'], 0.0, delta=0.1)
            self.assertAlmostEqual(pose['yaw'], -math.pi/2.0, delta=0.1)
            self.assertAlmostEqual(pose['pitch'], 0.0, delta=0.1)
            self.assertAlmostEqual(pose['roll'], 0.0, delta=0.1)


########################## Run these tests ##########################
if __name__ == "__main__":
    import unittest
    from morse.testing.testing import MorseTestRunner
    suite = unittest.TestLoader().loadTestsFromTestCase(XYW_Test)
    sys.exit(not MorseTestRunner().run(suite).wasSuccessful())


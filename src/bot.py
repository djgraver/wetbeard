import math

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket

from util.orientation import Orientation
from util.vec import Vec3


class MyBot(BaseAgent):

    def initialize_agent(self):
        # This runs once before the bot starts up, must be called initialize_agent
        self.controls = SimpleControllerState()

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        ball_location = Vec3(packet.game_ball.physics.location)
        
        my_car = packet.game_cars[self.index]
        car_location = Vec3(my_car.physics.location)

        car_to_ball = ball_location - car_location

        # Find the direction of our car using the Orientation class
        car_orientation = Orientation(my_car.physics.rotation)
        car_direction = car_orientation.forward
        
        # Get direction to steer
        steer_correction_radians = find_steer(car_direction, car_to_ball)
        steer_debug = str(steer_correction_radians)

        # From Blue side
        # ball_location.x +ve is Left
        # ball_location.y +ve is Orange (attacking)
        # ball_location.z is +76 above car at ground
        carloc_debug = "Car to Ball = x:" + str(int(car_location.x - ball_location.x)) + \
            " y:" + str(int(car_location.y - ball_location.y)) + \
                " z:" + str(int((car_location.z + 76.0) - ball_location.z))

        # Positive radians in the unit circle is a turn to the left.
        if steer_correction_radians > 1.9:
            turn = -1.0
            slide = 1
            boost = 1
            action_debug = "Hard L"
        elif steer_correction_radians < -1.9:
            turn = 1.0
            slide = 1
            boost = 1
            action_debug = "Hard R"
        elif steer_correction_radians > 0.06:
            turn = -1.0  # Negative value for a turn to the left.
            action_debug = "Turn L"
            slide = 0
            boost = 0
        elif steer_correction_radians < -0.06:
            turn = 1.0
            action_debug = "Turn R"
            slide = 0
            boost = 0
        else:
            turn = 0.0
            action_debug = "Straight"
            slide = 0
            boost = 0

        # Assign actions
        self.controls.throttle = 1.0
        self.controls.steer = turn
        self.controls.boost = boost
        self.controls.handbrake = slide

        # Output all debug data
        draw_debug(self.renderer, my_car, packet.game_ball, carloc_debug, steer_debug, action_debug)

        return self.controls

def find_steer(current: Vec3, ideal: Vec3) -> float:
    # Finds the angle from current to ideal vector in the xy-plane. Angle will be between -pi and +pi.

    # The in-game axes are left handed, so use -x
    current_in_radians = math.atan2(current.y, -current.x)
    ideal_in_radians = math.atan2(ideal.y, -ideal.x)

    diff = ideal_in_radians - current_in_radians

    # Make sure that diff is between -pi and +pi.
    if abs(diff) > math.pi:
        if diff < 0:
            diff += 2 * math.pi
        else:
            diff -= 2 * math.pi
    return diff


def draw_debug(renderer, car, ball, carloc_debug, steer_debug, action_debug):
    renderer.begin_rendering()
    # draw a line from the car to the ball
    #renderer.draw_line_3d(car.physics.location, ball.physics.location, renderer.white())
    # print the action that the bot is taking
    renderer.draw_string_2d(5, 5, 1, 1, carloc_debug, renderer.white())
    renderer.draw_string_2d(5, 25, 1, 1, steer_debug, renderer.white())
    renderer.draw_string_3d(car.physics.location, 1, 1, action_debug, renderer.white())
    renderer.end_rendering()

from typing import List, Tuple
from approxeng.input.selectbinder import ControllerResource
from approxeng.input.controllers import ControllerRequirement
import atexit
import time
import threading


# The number of seconds for which to search for a controller before giving up
CONTROLLER_SEARCH_TIME: int = 60


class Controller:

    def __init__(self):

        self.__is_listening: bool = True

        # Joystick axes

        self.ly: float = 0  # Left y-axis
        self.lx: float = 0  # Left x-axis
        self.ry: float = 0  # Right y-axis
        self.rx: float = 0  # Right x-axis
        self.lt: float = 0  # Left trigger
        self.rt: float = 0  # Right trigger

        # Button downs (whether they were pressed this frame)

        self.square_down: bool = False  # Square button
        self.triangle_down: bool = False  # Triangle button
        self.circle_down: bool = False  # Circle button
        self.cross_down: bool = False  # Cross button
        self.lb_down: bool = False  # Left bumper
        self.rb_down: bool = False  # Right bumper

        # Button hold times (in seconds)

        self.square_hold_time: float = 0
        self.triangle_hold_time: float = 0
        self.circle_hold_time: float = 0
        self.cross_hold_time: float = 0
        self.lb_hold_time: float = 0
        self.rb_hold_time: float = 0

        # Start listening thread

        self.__listening_thread = threading.Thread(
            target=self.__do_listen_thread,
            args=()
        )
        self.__listening_thread.start()

        # Add destruction to program termination

        atexit.register(self.__stop_listening)

    @property
    def square_is_pressed(self) -> bool:
        """Whether the square button is currently pressed"""
        return self.square_hold_time > 0

    @property
    def triangle_is_pressed(self) -> bool:
        """Whether the triangle button is currently pressed"""
        return self.triangle_hold_time > 0

    @property
    def circle_is_pressed(self) -> bool:
        """Whether the circle button is currently pressed"""
        return self.circle_hold_time > 0

    @property
    def cross_is_pressed(self) -> bool:
        """Whether the cross button is currently pressed"""
        return self.cross_hold_time > 0

    @property
    def lb_is_pressed(self) -> bool:
        """Whether the left bumper is currently pressed"""
        return self.lb_hold_time > 0

    @property
    def rb_is_pressed(self) -> bool:
        """Whether the right bumper is currently pressed"""
        return self.rb_hold_time > 0

    def __do_listen_thread(self) -> None:

        controller_search_start_time = time.time()

        controller_was_found: bool = False

        # Try to find a controller
        while (time.time() - controller_search_start_time <=
               CONTROLLER_SEARCH_TIME):

            try:

                with ControllerResource() as joystick:

                    controller_was_found = True
                    print("Joystick connected")

                    while joystick.connected:

                        # Axes

                        self.ly = joystick.ly
                        self.lx = joystick.lx
                        self.ry = joystick.ry
                        self.rx = joystick.rx
                        self.lt = joystick.lt
                        self.rt = joystick.rt

                        # Button downs

                        if joystick.square is not None:
                            self.square_hold_time = joystick.square
                        else:
                            self.square_hold_time = 0

                        if joystick.triangle is not None:
                            self.triangle_hold_time = joystick.triangle
                        else:
                            self.triangle_hold_time = 0

                        if joystick.circle is not None:
                            self.circle_hold_time = joystick.circle
                        else:
                            self.circle_hold_time = 0

                        if joystick.cross is not None:
                            self.cross_hold_time = joystick.cross
                        else:
                            self.cross_hold_time = 0

                        if joystick.l1 is not None:
                            self.lb_hold_time = joystick.l1
                        else:
                            self.lb_hold_time = 0

                        if joystick.r1 is not None:
                            self.rb_hold_time = joystick.r1
                        else:
                            self.rb_hold_time = 0

                        # Button presses

                        self.square_down = joystick.presses.square
                        self.triangle_down = joystick.presses.triangle
                        self.circle_down = joystick.presses.circle
                        self.cross_down = joystick.presses.cross
                        self.lb_down = joystick.presses.l1
                        self.rb_down = joystick.presses.r1

                    print("Joystick disconnected")

            except IOError:
                # Couldn't find controller. Wait a bit before trying again
                time.sleep(0.5)

        if not controller_was_found:
            print("Failed to find a controller, giving up")

    def __stop_listening(self) -> None:

        self.__is_listening = False

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
from matplotlib.animation import FuncAnimation

class CarSimulation:
    def __init__(self, pipe_conn, 
                 acceleration=0.1, 
                 deceleration=0.05, 
                 steering_angle_deg=5, 
                 max_speed=2.0, 
                 friction=0.01):

        self.pipe_conn = pipe_conn  # Connection to receive commands

        # Parameters
        self.acceleration = acceleration
        self.deceleration = deceleration
        self.steering_angle = np.deg2rad(steering_angle_deg)
        self.max_speed = max_speed
        self.friction = friction

        # Car state
        self.car_pos = np.array([0.0, 0.0])
        self.car_angle = 0.0
        self.car_speed = 0.0

        # Plot setup
        self.fig, self.ax = plt.subplots()
        self.ax.set_xlim(-20, 20)
        self.ax.set_ylim(-20, 20)
        self.ax.set_aspect('equal')
        self.ax.grid()

        # Car arrow (visual)
        self.car_arrow = FancyArrowPatch((0, 0), (1, 0), mutation_scale=20, color='blue')
        self.ax.add_patch(self.car_arrow)

        # Start animation
        self.ani = FuncAnimation(self.fig, self.animate, interval=50, blit=False)

    # --- Car Control Methods ---
    def accelerate(self, amount=0.1):
        self.acceleration = amount
        self.car_speed = min(self.car_speed + self.acceleration, self.max_speed)

    def brake(self, amount=0.1):
        self.deceleration = amount
        self.car_speed = max(self.car_speed - self.deceleration, -self.max_speed / 2)

    def steer_left(self, amount=5):
        if self.car_speed > 0:
            self.steering_angle = np.deg2rad(amount)
            self.car_angle -= self.steering_angle

    def steer_right(self, amount=5):
        if self.car_speed > 0:
            self.steering_angle = np.deg2rad(-amount)
            self.car_angle += self.steering_angle
    
    def emergency_stop(self):
        """Immediately stop the car."""
        self.brake(999)
        while True:
            if self.car_speed <= 0:
                self.car_speed = 0
                break
            self.update_car()
            print('EMERGENCY STOP: Car stopped...')
            raise SystemExit("Emergency stop triggered. Simulation ended.")

    # --- Animation Loop ---
    def animate(self, frame):

        # Read commands from Pipe (non-blocking)
        while self.pipe_conn.poll():
            cmd_dict = self.pipe_conn.recv()
            if cmd_dict.__len__() == 0:
                continue
            command, val = list(cmd_dict.items())[0]  # Get the command and value
            if command == 'accelerate':
                self.accelerate(val)
            elif command == 'brake':
                self.brake(val)
            elif command == 'steer_left':
                self.steer_left(val)
            elif command == 'steer_right':
                self.steer_right(val)
            elif command == 'ems':
                self.emergency_stop()
            elif command == 'exit':
                plt.close()  # Close the plot to end simulation

        # Apply friction
        if self.car_speed > 0:
            self.car_speed = max(self.car_speed - self.friction, 0)
        elif self.car_speed < 0:
            self.car_speed = min(self.car_speed + self.friction, 0)

        # Update position
        self.update_car()

        return self.car_arrow

    def update_car(self):

        # only steer if the car is moving
        direction = np.array([np.cos(self.car_angle), np.sin(self.car_angle)])
        self.car_pos += direction * self.car_speed
        self.car_angle == np.arctan(direction[1] / direction[0])

        # Update arrow
        self.car_arrow.set_positions(
            (self.car_pos[0], self.car_pos[1]),
            (self.car_pos[0] + direction[0], self.car_pos[1] + direction[1])
        )

        # Adjust plot view
        self.ax.set_xlim(self.car_pos[0] - 10, self.car_pos[0] + 10)
        self.ax.set_ylim(self.car_pos[1] - 10, self.car_pos[1] + 10)

    def run(self):
        plt.show()

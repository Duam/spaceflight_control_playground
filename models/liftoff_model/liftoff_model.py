#!/usr/bin/python3

import casadi as cas
import numpy as np

## 
# @class liftoff_model
# @brief Model of a 2d rocket during liftoff while 
#        considering very simple aerodynamics.
##
class liftoff_model:
  
    ## 
    # @brief Initialization procedure
    ##
    def __init__(self):
        
        # Universe parameters

        # Gravitational constant (m/s^2)
        self.g = 9.81

        # Spacecraft parameters

        # Distance from base to COM (m)
        self.L = 20.0
        # Distance from base to COP (m)
        self.l = 10.0
        # Maximum thrust (N)
        self.maxThrust = 300.0 * 10**3
        # Maximum gimbal angle in both directions (rad)
        self.maxGimbal = np.pi / 8
        # Total mass (kg)
        self.m = 20.0 * 10**3
        # Inertia tensor (kg*m^2)
        self.I = 1 * 10**3

        # Dynamics parameters

        # Number of states, disturbances, controls
        self.nx = 6 
        self.nd = 1
        self.nu = 2
        # Initial state
        self.x0 = cas.vertcat(
            0.0, # x-position
            0.0, # y-position
            0.0, # x-velocity
            0.0, # y-velocity
            0.0, # angle (measured from vertical axis)
            0.0  # angular velocity
        )

    
    ##
    # @brief The model dynamics
    # @param x (state)
    #    x-position (m)
    #    y-position (m)
    #    x-velocity (m/s)
    #    y-velocity (m/s)
    #    angle (rad)
    #    angular velocity (rad/s)
    # @param u (input)
    #    Thrust (N)
    #    Gimbal angle (rad)
    #    Wind force disturbance (N)
    # @return State derivative
    ##
    def dynamics(self, x, u):
        # Get states
        xPos = x[0]
        yPos = x[1]
        xVel = x[2]
        yVel = x[3]
        ang = x[4]
        angVel = x[5]

        # Get controls
        T = u[0]
        mu = u[1]

        # Get disturbing wind force (only in horizontal direction)
        F_W = u[2]

        # Compute some intermediate values
        sa = cas.sin(ang)
        ca = cas.cos(ang)
        sm = cas.sin(mu)
        cm = cas.cos(mu)

        # Compute the thruster forces
        '''F_T = T * cas.vertcat(
            sm * sa + cm * ca, 
            sm * ca - cm * sa
        )'''
        F_T = T * self.maxThrust * cas.vertcat( # <- Check this equation
            cm * sa - sm * ca,
            cm * ca + sm * sa
        )

        print(F_T)

        # Compute the gravitational force
        F_G = cas.vertcat(
            0,
            - self.m * self.g
        )

        # Compute the torque around base
        Torque = self.L * F_W * ca + self.l * F_G[1] * sa
        # TODO check this equation! thruster gimbal has no effect

        # Compute the linear accelerations
        xAcc = (F_T[0] + F_W) / self.m
        yAcc = (F_T[1] + F_G[1]) / self.m

        # Compute the angular acceleration
        angAcc = Torque / self.I

        # Stack the derivatives
        xdot = cas.vertcat(
            xVel,
            yVel,
            xAcc,
            yAcc,
            angVel,
            angAcc
        )

        return xdot


##
# Run this script to test the model and generate a trajectory
##
if __name__ == '__main__':

    import sys, os
    sys.path.append(os.path.realpath('../../'))
    sys.path.append(os.getcwd())

    # Import plotting library and runge kutta 4 integrator    
    import matplotlib.pyplot as plt
    from integrators.rk4step import rk4step_ode

    # Create a spacecraft instance
    spacecraft = liftoff_model()

    # Print some parameters
    print("Spacecraft parameters:")
    print("Grav. accel. g: " + str(spacecraft.g) + " m/s^2")
    print("Distance base to COM: " + str(spacecraft.L) + " m")
    print("Distance base to COP: " + str(spacecraft.l) + " m")
    print("Mass: " + str(spacecraft.m) + " kg")
    print("Max. thrust: " + str(spacecraft.maxThrust) + " N")
    print("Initial state: " + str(spacecraft.x0))
    print("Number of states: " + str(spacecraft.nx))
    print("Number of disturbances: " + str(spacecraft.nd))
    print("Number of controls: " + str(spacecraft.nu))

    # Simulation parameters
    T = 600.0
    N = 100
    DT = T/N

    # Integration parameters 
    nn = 10     # Integrator steps per step
    h = DT/nn   # Step size of integrator step

    # Create system model with CasADi
    x = cas.MX.sym('x', spacecraft.nx, 1)
    u = cas.MX.sym('u', spacecraft.nu + spacecraft.nd, 1)
    f = cas.Function('f', [x,u], [spacecraft.dynamics(x,u)])
    
    # Discretize spacecraft dynamics using rk4
    Xk = x
    for k in range(nn):
        Xk = rk4step_ode(f, Xk, u, h)
    
    F = cas.Function('F', [x,u], [Xk], ['x','u'], ['xk'])

    # Choose controls for simulation
    wind_forces = np.zeros((N, spacecraft.nd))
    controls = np.zeros((N, spacecraft.nu))
    controls[:,0] = 0.7 * np.ones(N)
    controls[50:60,1] = 0.01 * np.ones(10)

    us = np.append(controls, wind_forces, axis=1)

    # Test evaluation of the ODE
    print(us[0,:])
    xdot_test = spacecraft.dynamics(spacecraft.x0, us[0,:])
    print(xdot_test)

    # Simulate the system
    xs = cas.DM.zeros((N, spacecraft.nx))
    xs[0,:] = spacecraft.x0

    for k in range(1,N):
        xs[k,:] = F(xs[k-1,:], us[k-1,:])

    xs = xs.full()

    # Prepare plotting
    tAxis = np.linspace(0, T-DT, N)
    plt.figure(1)

    # Plot
    plt.subplot(321)
    plt.plot(tAxis, xs[:,0])
    plt.ylabel('x-pos [m]')

    plt.subplot(322)
    plt.plot(tAxis, xs[:,1])
    plt.ylabel('y-pos [m]')

    plt.subplot(323)
    plt.plot(tAxis, xs[:,2])
    plt.ylabel('x-vel [m/s]')

    plt.subplot(324)
    plt.plot(tAxis, xs[:,3])
    plt.ylabel('y-vel [m/s]')

    plt.subplot(325)
    plt.plot(tAxis, xs[:,4])
    plt.ylabel('angle [rad]')

    plt.subplot(326)
    plt.plot(tAxis, xs[:,5])
    plt.ylabel('angular vel. [rad/s]')

    plt.show()
#!/usr/bin/python3

##
# @file orbit_animator.py
# @author Paul Daum
# @brief Takes a trajectory of position and velocities and tries
#        to make a nice animation out of it.
##


import sys, os
sys.path.append(os.path.realpath('../'))
sys.path.append(os.getcwd())

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import models.kepler_orbit.kepler_orbit as orbit

##
# @class orbit_animator
# @brief TODO
##
class orbit_animator:

    ##
    # @brief Initialization procedure
    # @param params Plotting parameters dictionary
    # @param figNum Number of the figure (default = 0)
    ##s
    def __init__(self, params, figNum = 0):
        
        # Horizon length and sample number
        self.T = params['T']
        self.N = params['N']

        # Are the trajectories in cartesian coordinates?
        self.coordsAreCartesian = params['isCartesian']

        # If they're cartesian, take them as they are
        if (self.coordsAreCartesian):
            self.xPositions = params['xPositions']
            self.yPositions = params['yPositions']
            self.xVelocities = params['xVelocities']
            self.yVelocities = params['yVelocities']
            self.xForces = params['xForces']
            self.yForces = params['yForces']

        # If they're polar, convert them
        else:
            rhos = params['rhos']
            thetas = params['thetas']
            rhoDots = params['rhoDots']
            thetaDots = params['thetaDots']
            rhoForces = params['rhoForces']
            thetaForces = params['thetaForces']

            # Stack them up into xs_pol, us_pol TODO
            # Convert into cartesian coordinates TODO

        # Configure figure
        margin = 2
        self.fig = plt.figure(figNum)
        self.ax = self.fig.add_subplot(
            111, 
            autoscale_on = False, 
            xlim = (np.amin(self.xPositions)-margin, np.amax(self.xPositions)+margin),
            ylim = (np.amin(self.yPositions)-margin, np.amax(self.yPositions)+margin)
        )
        self.ax.grid()


    ##
    # @brief Initializes all objects in the plot. Is used by
    #        matplotlib.animation
    ##
    def animation_init(self):
        # Line plot for the trajectory
        self.trajectory, = self.ax.plot([], [], 'o-', lw=2)
        self.trajectory.set_data([], [])
        return self.trajectory

    ## 
    # @brief Updates all the objects in the plot. Is used by 
    #        matplotlib.animation
    # @param i Index of the data
    ## 
    def animation_main(self,i):
        lineX = [self.xPositions[i], self.xPositions[i-1]]
        lineY = [self.yPositions[i], self.yPositions[i-1]]
        self.trajectory.set_data(lineX, lineY)
        return self.trajectory

    ##
    # @brief Creates the animation and shows it
    ## 
    def run(self, fps, saveFile = False, fileName = 'anim.mp4'):

        # Create the animation object
        anim = animation.FuncAnimation(
            fig = self.fig,
            func = self.animation_main,
            frames = np.arange(1,self.N),
            interval = 100/fps,
            init_func = self.animation_init
        )

        # Save to file if needed
        if(saveFile):
            anim.save(fileName, fps)

        # Show animation
        plt.show()


##
# Execute this script to test the animator
##
if __name__ == '__main__':

    # Create a trajectory
    T = 10.0
    N = 10

    xPoses = [0,1,2,3,4,5,6,7,8,9] 
    yPoses = [9,8,7,6,5,4,3,2,1,0]
    xVelos = [1,1,1,1,1,1,1,1,1,1]
    yVelos = [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1]
    xForces = [0,0,0,0,0,0,0,0,0,0]
    yForces = [0,0,0,0,0,0,0,0,0,0]

    # Save trajectory in a dictionary
    params = {}
    params['T'] = T
    params['N'] = N
    params['isCartesian'] = True
    params['xPositions'] = xPoses
    params['yPositions'] = yPoses
    params['xVelocities'] = xVelos
    params['yVelocities'] = yVelos
    params['xForces'] = xForces
    params['yForces'] = yForces

    # Create animator
    animator = orbit_animator(params)

    # Run animator
    animator.run(10)
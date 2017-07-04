# code-snippets
This repository contains some of my code-snippets.

## genbox.py:
This python script is inspired by Nek5000's genbox tool for simple mesh generation.  
I want to use it to create a simple mesh for roughness simulations. Therefore, periodic boundary conditions and internal BCs need to be prescribed in multiple boxes.

## mem_req.py:
Gives an approximation of the memory requirements for a Nek5000 simulation according to the formula stated in the user guide.

## pts.py:
This script can be used to create a point distribution which clusters at one end.

## watch_cfl.bash
Script to plot the cfl number over time step.

## watch_dpdz.bash
Script to plot the pressure gradient over time step.

## calc_mean.py
Script to extract only the required time/timestep between steps 30 and 95 for a run of nsteps=103 and taking the mean.

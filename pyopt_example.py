#!/usr/bin/env python
'''
Solves Rosenbrock's Unconstrained Problem.

    min 	100*(x2-x1^2)**2 + (1-x1)^2
    s.t.:	-10 <= xi <= 10,  i = 1,2
    
    f* = 0 , x* = [1, 1]
'''
from numpy.random import random
from numpy import sqrt, array
from copy import deepcopy
# from joblib import Parallel, delayed
from openmdao.api import Problem
from workflow_cheap import LCOE
import time

prob = Problem()
# print clock(), "Before defining model"
prob.model = LCOE()
# print clock(), "Before setup"
prob.setup()

def objfunc(x):
    prob['indep2.downwind_spacing'] = x[0]
    prob['indep2.crosswind_spacing'] = x[1]
    prob['indep2.odd_row_shift_spacing'] = x[2]
    prob['indep2.layout_angle'] = x[3]
    prob.run_model()
    f = prob['analysis.lcoe'][0]
    g = [0.0] * 2
    g[0] = prob['constraint_boundary.magnitude_violations'][0]
    g[1] = prob['constraint_distance.magnitude_violations'][0]

    return f, g, 0
# =============================================================================
# Standard Python modules
# =============================================================================
import os, sys, time
import pdb

# =============================================================================
# Extension modules
# =============================================================================
#from pyOpt import *
from pyOpt import Optimization
from pyOpt import PSQP
# from pyOpt import SLSQP
from pyOpt import CONMIN
# from pyOpt import COBYLA
# from pyOpt import SOLVOPT
# from pyOpt import KSOPT
from pyOpt import NSGA2
from pyOpt import SDPEN


# =============================================================================
# 
# =============================================================================
    

# =============================================================================
# 
# ============================================================================= 
opt_prob = Optimization('Rosenbrock Unconstraint Problem',objfunc)
opt_prob.addVar('x1','c',lower=570.0,upper=2500.0,value=1440.0)
opt_prob.addVar('x2','c',lower=570.0,upper=2500.0,value=1440.0)
opt_prob.addVar('x3','c',lower=0.0,upper=1250.0,value=0.0)
opt_prob.addVar('x4','c',lower=0.0,upper=180.0,value=0.0)
opt_prob.addObj('f')
opt_prob.addCon('g1','i')
opt_prob.addCon('g2','i')
print opt_prob

# Instantiate Optimizer (PSQP) & Solve Problem
# sdpen = SDPEN()
# sdpen.setOption('iprint',-1)
# sdpen(opt_prob)
# print opt_prob.solution(0)

# # Instantiate Optimizer (SLSQP) & Solve Problem
# # slsqp = SLSQP()
# # slsqp.setOption('IPRINT',-1)
# # slsqp(opt_prob,sens_type='FD')
# # print opt_prob.solution(1)

# # Instantiate Optimizer (CONMIN) & Solve Problem
# conmin = CONMIN()
# conmin.setOption('IPRINT',0)
# conmin(opt_prob,sens_type='FD	')
# print opt_prob.solution(1)

# Instantiate Optimizer (COBYLA) & Solve Problem
# cobyla = COBYLA()
# cobyla.setOption('IPRINT',0)
# cobyla(opt_prob)
# print opt_prob.solution(2)

# # Instantiate Optimizer (SOLVOPT) & Solve Problem
# solvopt = SOLVOPT()
# solvopt.setOption('iprint',-1)
# solvopt(opt_prob,sens_type='FD')
# print opt_prob.solution(2)

# # Instantiate Optimizer (KSOPT) & Solve Problem
# ksopt = KSOPT()
# ksopt.setOption('IPRINT',0)
# ksopt(opt_prob,sens_type='FD')
# print opt_prob.solution(2)

# Instantiate Optimizer (NSGA2) & Solve Problem
nsga2 = NSGA2()
nsga2.setOption('PrintOut',0)
nsga2(opt_prob)
print opt_prob.solution(0)

# # Instantiate Optimizer (SDPEN) & Solve Problem
# psqp = PSQP()
# psqp.setOption('IPRINT',0)
# psqp(opt_prob,sens_type='FD')
# print opt_prob.solution(3)
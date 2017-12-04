import numpy as np

from openmdao.api import Problem, ScipyOptimizer
from openmdao.api import pyOptSparseDriver
from workflow_cheap import LCOE
from farm_description import NT

prob = Problem()
model = prob.model = LCOE()
prob.setup()

print(prob['indep2.layout'])
prob.run_model()
print(prob['analysis.lcoe'])
prob.run_driver()

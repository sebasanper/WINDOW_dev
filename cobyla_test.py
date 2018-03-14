from scipy.optimize import minimize

def obj(x):
	return - sum(x)

def con1(x):
	return 3.0 - x[0]

con1d = {'type':'ineq', 'fun':con1}

def con2(x):
	return 2.0 - x[1]

con2d = {'type':'ineq', 'fun':con2}

def con3(x):
	return 1.0 - x[2]

con3d = {'type':'ineq', 'fun':con3}

const = (con1d, con2d, con3d)

x1 = [0.0, 0.0, 0.0]

a = minimize(obj, x0=x1, method='COBYLA', constraints=const)

print a

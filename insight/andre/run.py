from SEQIJR import SEQIJR
from FileReader import FileReader
#from ParameterEstimator import ParameterEstimator
import numpy as np

covid19_filename = 'COVID-19-geographic-disbtribution-worldwide-2020-03-16.xls'
population_filename = 'PopulationByCountry.xlsx'

country = 'Sweden'

files = FileReader(covid19_filename, population_filename)

x_confirmed = files.create_t_vector(country)
y_confirmed = files.cases(country) / files.population(country)

beta = 3.1199625350407327
epsilon_E = 0.2
epsilon_Q = 0.1
epsilon_J = 0.05
kappa_E = 0.41102957279843333
kappa_Q = 0.9978517538943866
kappa_J = 0.8293967574315196
gamma_Q = 0.05
gamma_J = 0.09867516179498347
alpha_I = 1.2773689908243377
alpha_J = 0.9622421703799159

model = SEQIJR(beta, epsilon_E, epsilon_Q, epsilon_J,
                 kappa_E, kappa_Q, kappa_J,
                 gamma_Q, gamma_J,
                 alpha_I, alpha_J)

N = 1

J_0 = min(y_confirmed)
I_0 = 2 * J_0
E_0 = 4 * J_0
Q_0 = 0
R_0 = 0

y_0 = np.array([N - E_0 - Q_0 - I_0 - J_0 - R_0,
                E_0,
                Q_0,
                I_0,
                J_0,
                J_0], dtype=float).transpose()

P = 100
t_start = min(files.create_t_vector(country))
t_end = max(files.create_t_vector(country)) + P

h = 1 / 2
x, S_p, E_p, Q_p, I_p, J_p, L_p = model.prediction(y_0, t_start, t_end, h)
# R_p = N - S_p - E_p - Q_p - I_p - J_p
print(L_p)

m = int(max(files.create_t_vector(country)) / h)
y_1 = np.array([S_p[m],
                E_p[m],
                Q_p[m],
                I_p[m],
                J_p[m],
                L_p[m]], dtype=float).transpose()

model.gamma_Q = .2
t_start2 = max(files.create_t_vector(country))
x2, S_p2, E_p2, Q_p2, I_p2, J_p2, L_p2 = model.prediction(y_1, t_start2, t_end, h)
print(L_p2)

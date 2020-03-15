# André Gerbaulet & Robin Sandström
#
# Based on models from "Mathematical Models in Population Biology and Epidemiology" by F. Brauer and C. Castillo-Chavez
#
# The SIR model with disease death will be modelled as N = S + I + R
#
# Assumed that people go from (susceptible state) to (infective state) to (removed state)
#
# N - Population size
# S - The number of people susceptible to the disease
# I - The number of infective people
# R - The number of previously infected people people removed from the disease, either by immunization or death
#
# S, I, R is assumed to follow the differential equation: N = S + I + R
#
# S' = - beta(N) * S * I              People going to infective state
# I' = beta(N) * S * I - alpha * I    People coming from susceptible state & people going to removed state
# N' = - (1 - f) * alpha * I          People leaving the population (death)
#
# beta(N) = C(N) / N,    C(N) = lambda * N^a,    a = 0.05

import numpy as np
import xlrd

class SIR_model:
    def __init__(self, covid19_filename, population_filename, country, steps=100, min_cases=100):
        self.covid19 = self.read_covid19_file(covid19_filename)
        self.populations = self.read_population_file(population_filename)
        self.country = country
        self.steps = steps

        self.cases_confirmed = self.covid19[country][0][self.covid19[country][0] >= min_cases]
        self.deaths_confirmed = self.covid19[country][1][self.covid19[country][0] >= min_cases]
        self.n = np.shape(self.cases_confirmed)[0]    # Number of measurements
        self.x_confirmed = np.arange(self.n)

        self.alpha = 0.5
        self.theta = 0.5
        self.gamma = 1 # 5 * 10**(-2)
        self.a = 0.05
        self.f = 0.99

    # Returns dictionary on the form {'Sweden' : [np.array(# smittade), np.array(# döda)]}
    def read_covid19_file(self, filename):
        workbook = xlrd.open_workbook(filename)
        worksheet = workbook.sheet_by_index(0)
        current_country = ''
        dictionary = {}
        for row in range(1, worksheet.nrows):
            temp_country = worksheet.cell_value(row, 1)
            if temp_country == current_country:
                cases = np.append(cases, np.array([worksheet.cell_value(row, 2)], dtype=int), 0)
                deaths = np.append(deaths, np.array([worksheet.cell_value(row, 3)], dtype=int), 0)
            else:
                if current_country != '':
                    dictionary[current_country] = [np.cumsum(np.flip(cases)), np.cumsum(np.flip(deaths))]
                cases = np.array([worksheet.cell_value(row, 2)], dtype=int)
                deaths = np.array([worksheet.cell_value(row, 3)], dtype=int)
                current_country = temp_country
        return dictionary

    # Returns dictionary on the form {'Sweden' : int(population size)}
    def read_population_file(self, filename):
        workbook = xlrd.open_workbook(filename)
        worksheet = workbook.sheet_by_index(0)
        dictionary = {}
        for row in range(1, worksheet.nrows):
            dictionary[worksheet.cell_value(row, 0)] = int(worksheet.cell_value(row, 1))
        return dictionary

    # Used in SIR model: infection rate, higher beta => more infections
    def beta(self, N, p):
        return p[1] * (N**(p[4] - 1))

    # Makes one step using Euler method
    def next_step(self, SIN, dt, p):
        SINp = np.array([[- self.beta(SIN[2], p) * SIN[0] * SIN[1]],
                         [self.beta(SIN[2], p) * SIN[0] * SIN[1] - p[0] * SIN[1]],
                         [- (1 - p[3]) * p[0] * SIN[1]]]).transpose()
        return SIN + dt * SINp

    # Takes M step with Eulers method
    def prediction(self, p, P=0, SIN_0=None):
        f = p[3]
        if SIN_0 is None:
            N_0 = p[2] * self.populations[self.country]
            I_0 = min(self.cases_confirmed)
            R_0 = 0
            SIN_0 = np.array([[N_0 - I_0 - R_0],
                              [I_0],
                              [N_0 - (1 - f) * R_0]])
            T = self.n + P
        else:
            T = P
        x = np.arange(self.steps + 1) / self.steps * T
        dt = T/self.steps
        SIN = np.zeros((3, self.steps + 1))
        SIN[:, 0] = SIN_0.transpose()
        for i in range(self.steps):
            SIN[:, i+1] = self.next_step(SIN[:, i], dt, p)
        return [x, SIN]

    # Calculates the residuals of fitted curve vs. measured points
    def get_residuals(self, x, y, x_hat, y_hat):
        n = np.shape(x)[0]
        m = np.shape(x_hat)[0]
        r = np.zeros(n, dtype=float)
        for i in range(n):
            for j in range(m-1):
                if x_hat[j] == x[i]:
                    r[i] = y[i] - y_hat[j]
                    break
                elif (x_hat[j] < x[i]) and (x_hat[j+1] > x[i]):
                    w = (x_hat[j+1] - x[i]) / (x_hat[j+1] - x_hat[j])
                    r[i] = y[i] - (w * y_hat[j] + (1 - w) * y_hat[j+1])
                    break
        return r

    def estimate_mean_second_derivative(self, y, dt=1):
        s = np.shape(y)[0]
        sd = np.zeros(s-2)
        for i in range(s-2):
            sd[i] = (y[i+2] - 2 * y[i+1] + y[i]) / (dt**2)
        return np.mean(sd)

    def minimize_parameters(self):
        gamma_values = np.power(10, -np.arange(100+1)/20)
        alpha_min = 0
        theta_min = 0
        gamma_min = 1
        rss_min = np.inf
        for gamma in gamma_values:
            alpha = .5
            theta = .5
            d_alpha = 0.25
            for i in range(10):
                d_theta = 0.25
                for j in range(10):
                    p = np.array([alpha, theta, gamma, f, a])
                    prediction = self.prediction(p)
                    x_prediction = prediction[0]
                    SIN = prediction[1]
                    S = SIN[0, :]
                    N = SIN[2, :]
                    res = sir.get_residuals(sir.x_confirmed, sir.cases_confirmed, x_prediction, N - S)
                    if np.mean(res) == 0:
                        break
                    elif np.mean(res) < 0:
                        theta -= d_theta
                        d_theta *= 0.5
                    else:
                        theta += d_theta
                        d_theta *= 0.5
                asd = self.estimate_mean_second_derivative(res)
                if asd == 0:
                    break
                elif asd < 0:
                    alpha += d_alpha
                    d_alpha *= 0.5
                else:
                    alpha -= d_alpha
                    d_alpha *= 0.5
            p = np.array([alpha, theta, gamma, f, a])
            rss = self.get_rss(p)

            print(rss)
            if rss < rss_min:
                alpha_min = alpha
                theta_min = theta
                gamma_min = gamma
                rss_min = rss
        return [alpha_min, theta_min, gamma_min]

    def get_rss(self, p):
        prediction = self.prediction(p)
        x_prediction = prediction[0]
        SIN = prediction[1]
        S = SIN[0, :]
        I = SIN[1, :]
        N = SIN[2, :]
        R = N - S - I
        res = self.get_residuals(self.x_confirmed, self.cases_confirmed, x_prediction, I + R)
        rss = np.dot(res, res)
        return rss

    def brute_force_parameters(self, Q):
        alpha_min = 0
        q_min = 0
        v = np.arange(Q + 1) / (Q)
        rss_min = 1000000000
        for i in range(Q+1):
            if i % 10 == 0:
                print(i)
            alpha = v[i]
            for j in range(Q+1):
                q = v[j]
                p = np.array([alpha, q, self.gamma, self.f, self.a])
                rss = self.get_rss(p)
                if rss < rss_min:
                    rss_min = rss
                    alpha_min = alpha
                    q_min = q
        return np.array([alpha_min, q_min], dtype=float)

    def get_curve(self, par, f, a, P):
        p = np.array([par[0], par[1], par[2], f, a])

        prediction = self.prediction(p, P)
        x_prediction = prediction[0]
        SIN = prediction[1]
        S = SIN[0, :]
        I = SIN[1, :]
        N = SIN[2, :]
        R = N - S - I
        #res = self.get_residuals(sir.x_confirmed, sir.cases_confirmed, x_prediction, I + R)
        #plt.plot(sir.x_confirmed, sir.cases_confirmed, 'bo', fillstyle='none')
        #plt.plot(x_prediction, I + R)
        # plt.plot(sir.x_confirmed, res, 'bo', fillstyle='none')
        # plt.plot([min(x_prediction), max(x_prediction)], [0, 0])
        #plt.show()
        data = []

        last_int = 0

        for i in range(len(I)):
            data.append({
                    'bx': x_prediction[i],
                    'by': I[i] + R[i]
            })

        for i in range(len(self.x_confirmed)):
            data.append({
                    'ax': int(self.x_confirmed[i]),
                    'ay': int(self.cases_confirmed[i])
            })
        return data

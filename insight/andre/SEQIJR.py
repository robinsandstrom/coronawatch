import numpy as np
from datetime import datetime, timedelta

class SEQIJR:
    def __init__(self, N=1, Pi=0, mu=0, b=1,
                 e_E=.2, e_Q=.1, e_J=.05,
                 g_1=.5, g_2=.5,
                 s_1=.5, s_2=.5,
                 k_1=.5, k_2=.5,
                 d_1=0, d_2=0):
        self.N = N
        self.Pi = Pi
        self.mu = mu
        self.b = b
        self.e_E = e_E
        self.e_Q = e_Q
        self.e_J = e_J
        self.g_1 = g_1
        self.g_2 = g_2
        self.s_1 = s_1
        self.s_2 = s_2
        self.k_1 = k_1
        self.k_2 = k_2
        self.d_1 = d_1
        self.d_2 = d_2

    def derivative(self, y):
        # S:0, E:1, Q:2, I:3, J:4, R:5
        Sp = self.Pi - self.b * y[0] * (y[3] + self.e_E * y[1] + self.e_Q * y[2] + self.e_J * y[4]) / self.N - self.mu * y[0]
        Ep = self.b * y[0] * (y[3] + self.e_E * y[1] + self.e_Q * y[2] + self.e_J * y[4]) / self.N - (self.g_1 + self.k_1 + self.mu) * y[1]
        Qp = self.g_1 * y[1] - (self.k_2 + self.mu) * y[2]
        Ip = self.k_1 * y[1] - (self.g_2 + self.d_1 + self.s_1 + self.mu) * y[3]
        Jp = self.g_2 * y[3] + self.k_2 * y[2] - (self.s_2 + self.d_2 + self.mu) * y[4]
        Rp = self.s_1 * y[3] + self.s_1 * y[4] - self.mu * y[5]
        aJp = self.g_2 * y[3] + self.k_2 * y[2]
        aIJp = self.k_1 * y[1] + self.k_2 * y[2]
        aDp = self.d_1 * y[3] + self.d_2 * y[4]
        return np.array([Sp, Ep, Qp, Ip, Jp, Rp, aJp, aIJp, aDp], dtype=float).transpose()

    def next_iteration(self, y, h):
        # Uses RK4
        k_1 = self.derivative(y)
        k_2 = self.derivative(y + k_1 * h / 2)
        k_3 = self.derivative(y + k_2 * h / 2)
        k_4 = self.derivative(y + k_3 * h)
        return y + (k_1 + 2 * k_2 + 2 * k_3 + k_4) * h / 6

    def prediction(self, y_0, t_start, t_end, h):
        n = int((t_end - t_start) / h)
        x = t_start + np.arange(n + 1) / n * (t_end - t_start)
        y = np.zeros((9, n+1))
        y[:, 0] = y_0
        for i in range(n):
            y[:, i+1] = self.next_iteration(y[:, i], h)
        S_pred = y[0, :]
        E_pred = y[1, :]
        Q_pred = y[2, :]
        I_pred = y[3, :]
        J_pred = y[4, :]
        R_pred = y[5, :]
        aJ_pred = y[6, :]
        aIJ_pred = y[7, :]
        aD_pred = y[8, :]
        return x, S_pred, E_pred, Q_pred, I_pred, J_pred, R_pred, aJ_pred, aIJ_pred, aD_pred

    def R_0(self):
        D_1 = self.k_1 + self.mu
        D_2 = self.d_1 + self.s_1 + self.mu
        if (D_1 == 0) or (D_2 == 0):
            return np.inf
        else:
            R_0 = self.b * (self.e_E / D_1 + self.k_1 / (D_1 * D_2))
            return R_0

    def R_c(self):
        D_1 = self.g_1 + self.k_1 + self.mu
        D_2 = self.g_2 + self.d_1 + self.s_1 + self.mu
        D_3 = self.s_2 + self.d_2 + self.mu
        D_4 = self.mu + self.k_2
        if (D_1 == 0) or (D_2 == 0) or (D_3 == 0) or (D_4 == 0):
            return np.inf
        else:
            R_c = self.b * (self.e_E / D_1 +
                            self.k_1 / (D_1 * D_2) +
                            self.e_Q * self.g_1 / (D_1 * D_4) +
                            self.e_J * self.k_1 * self.g_2 / (D_1 * D_2 * D_3) +
                            self.e_J * self.g_1 * self.k_2 / (D_1 * D_3 * D_4))
            return R_c

    @staticmethod
    def integrate(y, h):
        n = np.shape(y)[0]
        integral = np.zeros(n)
        for i in range(n-1):
            integral[i+1] = integral[i] + (y[i] + y[i+1]) * h / 2
        return integral

    def calc(self, country, files, P):
        x_confirmed = files.create_t_vector(country)
        y_confirmed = files.cases(country)
        d_confirmed = files.deaths(country)


        S_0 = self.N
        E_0 = 0
        Q_0 = 0
        I_0 = 1
        J_0 = 0
        R_0 = 0
        aJ_0 = 0
        aIJ_0 = 1
        aD_0 = 0

        y_0 = np.array([S_0,
                        E_0,
                        Q_0,
                        I_0,
                        J_0,
                        R_0,
                        aJ_0,
                        aIJ_0,
                        aD_0], dtype=float).transpose()

        h = 1 / 5
        x_1, S_p_1, E_p_1, Q_p_1, I_p_1, J_p_1, R_p_1, aJ_p_1, aIJ_p_1, aD_p_1 = self.prediction(y_0, 0, 365, h)

        m = np.argmax(aIJ_p_1 > min(y_confirmed))

        y_0 = np.array([S_p_1[m],
                        E_p_1[m],
                        Q_p_1[m],
                        I_p_1[m],
                        J_p_1[m],
                        R_p_1[m],
                        aJ_p_1[m],
                        aIJ_p_1[m],
                        aD_p_1[m]], dtype=float).transpose()


        t_start = min(files.create_t_vector(country))
        t_end = max(files.create_t_vector(country)) + P

        x, S_p, E_p, Q_p, I_p, J_p, R_p, aJ_p, aIJ_p, aD_p = self.prediction(y_0, t_start, t_end, h)

        last_int = 0
        no_of_seconds = int(x[-1])*24*60*60
        time_interval = no_of_seconds/len(x)

        d = datetime.now().replace(hour=0, minute=0) - timedelta(len(x_confirmed))
        dates_prognosis = []

        for i in range(len(I_p)):
            dates_prognosis.append(d)
            d+=timedelta(seconds=time_interval)

        d = datetime.now().replace(hour=0, minute=0) - timedelta(len(x_confirmed))
        dates_measured = []

        for i in range(len(x_confirmed)):
            dates_measured.append(d)
            d+=timedelta(days=1)



        return {
                'dates_prognosis': dates_prognosis,
                'dates_measured': dates_measured,
                'cases_confirmed': y_confirmed.tolist(),
                'deaths_confirmed': d_confirmed.tolist(),
                'no_measurement': [],
                'steps': x.tolist(),
                'susceptibles': S_p.tolist(),
                'exposed': E_p.tolist(),
                'quarantined': Q_p.tolist(),
                'infective': I_p.tolist(),
                'hospital_care': (0.01*I_p).tolist(),
                'intensive_care': (0.02*I_p).tolist(),
                'isolated': J_p.tolist(),
                'removed': R_p.tolist(),
                'accumulated_isolated': aJ_p.tolist(),
                'accumulated_isolated_infective': aIJ_p.tolist(),
                'accumulated_deaths': aD_p.tolist(),
                'key_figures': {
                    'RSS_aij': 0,
                    'RSS_deaths': 0,
                    'R0': self.R_0(),
                    'RC': self.R_c(),
                    'max_level': 0
                }
                }

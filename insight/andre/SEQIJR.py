import numpy as np

class SEQIJR:
    def __init__(self, beta=1, epsilon_E=.5, epsilon_Q=.5, epsilon_J=.5,
                 kappa_E=.5, kappa_Q=.5, kappa_J=.5,
                 gamma_Q=.5, gamma_J=.5,
                 alpha_I=.5, alpha_J=.5):
        self.beta = beta
        self.epsilon_E = epsilon_E      # 0 <= epsilon_E <= 1
        self.epsilon_Q = epsilon_Q
        self.epsilon_J = epsilon_J
        self.kappa_E = kappa_E
        self.kappa_Q = kappa_Q
        self.kappa_J = kappa_J
        self.gamma_Q = gamma_Q
        self.gamma_J = gamma_J
        self.alpha_I = alpha_I
        self.alpha_J = alpha_J

    def derivative(self, y):
        # S:0, E:1, Q:2, I:3, J:4
        Sp = - self.beta * y[0] * (self.epsilon_E * y[1] +
                                   self.epsilon_E * self.epsilon_Q * y[2] +
                                   self.epsilon_J * y[4])
        Ep = self.beta * y[0] * (self.epsilon_E * y[1] +
                                 self.epsilon_E * self.epsilon_Q * y[2] +
                                 self.epsilon_J * y[4]) - (self.kappa_E + self.gamma_Q) * y[1]
        Qp = self.gamma_Q * y[1] - self.kappa_J * y[2]
        Ip = self.kappa_E * y[1] - (self.alpha_I + self.gamma_J) * y[3]
        Jp = self.kappa_Q * y[2] + self.gamma_J * y[3] - self.alpha_J * y[4]
        Lp = self.kappa_Q * y[2] + self.gamma_J * y[3]
        return np.array([Sp, Ep, Qp, Ip, Jp, Lp], dtype=float).transpose()

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
        y = np.zeros((6, n+1))
        y[:, 0] = y_0
        for i in range(n):
            y[:, i+1] = self.next_iteration(y[:, i], h)
        S_pred = y[0, :]
        E_pred = y[1, :]
        Q_pred = y[2, :]
        I_pred = y[3, :]
        J_pred = y[4, :]
        L_pred = y[5, :]
        return x, S_pred, E_pred, Q_pred, I_pred, J_pred, L_pred

    def R_c(self, N=1):
        D_1 = self.gamma_Q + self.kappa_E
        D_2 = self.gamma_J + self.alpha_I
        R_c = self.beta * N * (self.epsilon_E / D_1 + self.beta * self.kappa_E / (D_1 * D_2) +
                               self.epsilon_Q * self.epsilon_E * self.gamma_Q / (D_1 *self.kappa_Q) +
                               self.epsilon_J * self.kappa_E * self.gamma_J / (self.alpha_J * D_1 * D_2) +
                               self.epsilon_J * self.gamma_Q / (self.gamma_J * D_1))
        return R_c

    def integrate(self, y, h):
        n = np.shape(y)[0]
        integral = np.zeros(n)
        for i in range(n-1):
            integral[i+1] = integral[i] + (y[i] + y[i+1]) * h / 2
        return integral

"""
model_SIM_iterative.py

This solves model SIM from G&L Chapter 3, using an iterative
approach. This is based on Matlab code found at ...

This modeling approach gives us a base line for calibrating the
symbolic methodology.


% Parameters
theta = 0.2;        % tax rate
alpha1 = 0.6;       % marginal propensity to consume from dispoable income
alpha2 = 0.4;       % marginal propensity to consume from assets

% Endogenous Variables - preallocated
C = zeros(T,1);     % Consumption
H = zeros(T,1);     % Stock of wealth
Y = zeros(T,1);     % Gross Output/Income (expenditure defition)
YD = zeros(T,1);    % Disposable income
tax = zeros(T,1);   % Tax revenue

dHs = zeros(T,1);   % Financial assets - supply  flow
dHh = zeros(T,1);   % Financial assets - holding flow
dH  = zeros(T,1);   % Financial assets - actual change

% Exogenous Variable - preallocated
G = 20*ones(T,1);   % Government expenditure



fprintf('\n');
fprintf('___________________________________________________________________\n');
fprintf('      | Income  |Disposable |   Tax   |Consumption|   Financial    |\n');
fprintf(' iter.|         |  Income   | Revenue |           | stock    flows |\n');
fprintf('  [t] |  [Y]    |   [YD]    |  [tax]  |    [C]    |  [H]      [dH] |\n');
fprintf('------|---------|-----------|---------|-----------|----------------|\n');



for t = 2:T
    YI = G(t) + alpha2*H(t-1);    % Income Definition of Total Output
                                  % (3.11A) & (3.4) YS = W*N

    % Recursion to find goods market equilibrium (Y == YI)
    % (Thanks to Siavash Radpour for this approach)
    while abs(Y(t)-YI) > 0.00001
        Y(t) = YI;

        tax(t) = theta*Y(t);
        YD(t)  = Y(t) - tax(t);                                     % (3.5)
        C(t)   = alpha1*YD(t) + alpha2*H(t-1);                      % (3.7)
        YI     = C(t) + G(t);                                       % (3.10)
    end
        % flows of financial assets
        dHs(t) = G(t) - tax(t);                                     % (3.8) Fiscal deficit
        dHh(t) = YD(t) - C(t);                                      % (3.9)
        dH(t)  = dHs(t);  %= dHh(t)                                 % redundant

    % Update stock of financial wealth
    H(t) = H(t-1) + dH(t);

% Display
fprintf(' %3d  |  %6.2f |   %6.2f  |  %5.2f  |   %6.2f  | %6.2f  %6.2f |', t, ...
      Y(t), YD(t), tax(t), C(t), H(t), dH(t));
fprintf('\n')
end


"""


class ModelSIMiterative(object):
    def __init__(self):
        self.T = 1
        self.theta = 0.2  # taxrate
        self.alpha1 = 0.6  # marginal propensity
        self.alpha2 = 0.4  # marginal
        self.time_axis = [0., ]
        self.C = [0., ]  # Stock of wealth
        self.H = [80., ]  # Stock of wealth
        self.Y = [0., ]  # Gross Output/Income (expenditure defition)
        self.YD = [0., ]  # Disposable income
        self.tax = [0., ]  # Tax revenue
        self.dHs = [0., ]  # Financial assets - supply  flow
        self.dHh = [0., ]  # Financial assets - holding flow
        self.dH = [0., ]  # Financial assets - actual change
        # Exogenous variable - preallocate...
        self.G = [20., ] * 5 + [25., ] * 60  # Government expenditure

    def RunStep(self):
        """
        Calculate the next step
        :return:
        """
        if self.T >= len(self.G):
            raise StopIteration
        # First get the variables that are lagged or exogenous
        T = self.T
        G = self.G[T]
        H_LAG = self.H[T - 1]
        # Start solving
        GUESS_Y = 0.
        Y = 1.
        cnt = 0
        while abs(GUESS_Y - Y) > .001:
            Y = GUESS_Y
            tax = self.theta * Y
            YD = Y - tax
            C = self.alpha1 * YD + self.alpha2 * H_LAG
            GUESS_Y = C + G
            cnt += 1
            if cnt == 1000:  # pragma: no cover
                raise ValueError('Algorithm did not converge...')

        dHs = G - tax
        dHh = YD - C
        dH = dHs
        H = H_LAG + dH
        self.T += 1
        time_axis = self.T
        # Rather than assign the variables manually, use an eval...
        for var in ('C', 'H', 'Y', 'YD', 'tax', 'dHs', 'dHh', 'dH', 'time_axis'):
            cmd = 'self.X.append(X)'.replace('X', var)
            eval(cmd)

    def RunMethod2(self):
        init_vector = (0., 0., 0., 0., 0., 0., 0., 0., self.G[self.T], self.H[self.T - 1])
        err = 1.
        cnt = 0
        while err > .001:
            new_vector = self.Iterator(init_vector)
            err = 0.
            for i in range(0, len(new_vector)):
                err += abs(init_vector[i] - new_vector[i])
            cnt += 1
            init_vector = new_vector
            if cnt > 100:  # pragma: no cover
                raise ValueError('No convergence!')
        self.T += 1
        time_axis = self.T
        tax, YD, C, Y, dHs, dHh, dH, H, G, H_LAG = new_vector
        for var in ('C', 'H', 'Y', 'YD', 'tax', 'dHs', 'dHh', 'dH', 'time_axis'):
            cmd = 'self.X.append(X)'.replace('X', var)
            eval(cmd)

    def Iterator(self, valz_in):
        tax, YD, C, Y, dHs, dHh, dH, H, G, H_LAG = valz_in
        tax_n = self.theta * Y
        YD_n = Y - tax
        C_n = self.alpha1 * YD + self.alpha2 * H_LAG
        Y_n = C + G
        dHs_n = G - tax
        dHh_n = YD - C
        dH_n = dHs
        H_n = H_LAG + dH
        H_LAG_n = H_LAG
        G_n = G
        return tax_n, YD_n, C_n, Y_n, dHs_n, dHh_n, dH_n, H_n, G_n, H_LAG_n

    def main(self):
        while True:
            try:
                self.RunStep()
            except StopIteration:
                return


"""
output\unittest_output_2.py

Machine-generated model code


"""



class SFCModel(object):
    """
    Model

    Implements the following system of equations.

    Endogenous variables and parameters
    ===================================
    x = y + 2,
    y = alpha * x + dummy,
    alpha = .5.
    Where lagged variables are:
    LAG_x(t) = x(t-1),
    
    
    Exogenous Variables
    ===================
    dummy,

    """
    def __init__(self):
        self.MaxIterations = 400
        self.MaxTime = 3
        # Current time step. Call this "STEP" and not time so that users
        # can create a custom time axis variable.
        self.STEP = 0
        self.Err_Tolerance = .001
        self.x = [0., ]
        self.y = [0., ]
        self.alpha = [.5, ]
        self.dummy = [0., 1., 2.]
        #  Make sure exogenous variables are not longer than time frame
        self.dummy = self.dummy[0:4]


    def Iterator(self, in_vec):
        x, y, alpha, LAG_x, dummy = in_vec 
        NEW_x = y + 2
        NEW_y = alpha * x + dummy
        NEW_alpha = .5
        NEW_LAG_x = LAG_x
        NEW_dummy = dummy
        return NEW_x, NEW_y, NEW_alpha, NEW_LAG_x, NEW_dummy


    def main(self):
        while self.STEP < self.MaxTime:
            self.RunOneStep()

    def RunOneStep(self):
        self.STEP += 1
        x = self.x[-1]
        y = self.y[-1]
        alpha = self.alpha[-1]
        LAG_x = self.x[self.STEP -1]
        dummy = self.dummy[self.STEP]

        orig_vector = (x, y, alpha, LAG_x, dummy)
        err = 1.
        cnt = 0
        while err > self.Err_Tolerance:
            new_vector = self.Iterator(orig_vector)
            err = self.CalcError(orig_vector, new_vector)
            orig_vector = new_vector
            cnt += 1
            if cnt > self.MaxIterations:
                raise ValueError('No Convergence!')
        x = orig_vector[0]
        self.x.append(x)
        y = orig_vector[1]
        self.y.append(y)
        alpha = orig_vector[2]
        self.alpha.append(alpha)


    @staticmethod
    def CalcError(vec1, vec2):
        err = 0.
        for val1, val2 in zip(vec1, vec2):
            err += abs(val1 - val2)
        return err


if __name__ == '__main__':
    obj = SFCModel()
    obj.main()



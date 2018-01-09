class EnergyMin():
    def __init__(self, x_min=0, x_max=100, y_min=0, y_max=100, grid_spacing=0.2):
        import numpy as np
        import matplotlib.pyplot as plt
        import scipy.optimize as opt

        #Defining mins, maxes, and ranges
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max
        self.x_range = abs(x_max - x_min)
        self.y_range = abs(y_max - y_min)
        #Grid Spacing
        self.grid_spacing = grid_spacing
        #Defining x and y arrays
        self.x = np.arange(x_min, x_max, grid_spacing)
        self.y = np.arange(x_min, y_max, grid_spacing)
        self.z = None
        #Place Holder Array for Energy Landscape Additions
        self.wells = []
        #Place Holder Array for Ball Positions
        self.ball_pos = []

    def add_well(self, x0, y0, width=10, depth=10):
        import numpy as np
        #Meshgrid for the Energy Landscape
        xx, yy = np.meshgrid(self.x, self.y)
        #Add a Gaussian Well centered at (x0, y0)
        #with the specified Depth and Width
        z = -depth*(np.power(np.e,-((xx-x0)**2 + (yy-y0)**2)/(2*width)))
        #Add the well to the Energy Landscape Array
        self.wells.append(z)

    def add_landscape_feature(self, function):
        import numpy as np
        #Set xx and yy as the energy landscape plane variables
        xx, yy = np.meshgrid(self.x, self.y)
        #Define the function on top of the plane according to user input
        z = eval(function)
        self.wells.append(z)

    def plot_landscape(self, contours=10):
        import numpy as np
        import matplotlib.pyplot as plt

        #Add up all the Wells to form the Energy Landscape
        #if it hasn't already been done
        if self.z == None:
            self.combine_wells()
        #Setup the Ball Positions for plotting
        ball_pos_x = [el[0] for el in self.ball_pos]
        ball_pos_y = [el[1] for el in self.ball_pos]

        #Setup colors to show progression through time
        colors = np.linspace(0,1,len(self.ball_pos))
        #Create 9''x7'' figure
        plt.figure(figsize=(9, 7))
        #Plot the Energy Landscape with a colorbar to the side
        plt.contourf(self.x, self.y, self.z, contours)
        plt.colorbar()
        #Plot the Path of the Ball if it exists
        if not len(self.ball_pos) == 0:
            plt.scatter(ball_pos_x, ball_pos_y, c=colors, cmap='spring', s=2)
        plt.show()

    def add_ball(self, xb=1, yb=1):
        import numpy as np
        self.ball_pos.append(np.array([float(xb),float(yb)]))

    def combine_wells(self):
        import numpy as np
        #Create an empty array for the Total Energy Landscape
        z_tot = np.zeros((len(self.x), len(self.y)))
        #Sum up the value of each well at each Point in the Lanscape
        for el in self.wells:
            for i in range(len(self.x)):
                for j in range(len(self.y)):
                    z_tot[i][j] += el[i][j]
        #Set the Total Energy Lanscape Values to z
        self.z = z_tot

    def steepest_descent(self, step_size=0.8, max_iter=100, tolerance=0.0001):
        import numpy as np
        #Reset the ball position
        self.ball_pos = [self.ball_pos[0]]
        #Combine the wells to form the Total Energy Lanscape
        self.combine_wells()

        #Initializing the counter
        ct = 0
        #Defining the gradient
        NegGradY, NegGradX = np.negative(np.gradient(self.z))
        #Setting the last ball position
        prev_x_idx, prev_y_idx = [int(round(self.ball_pos[-1][0]/self.grid_spacing)),
                                  int(round(self.ball_pos[-1][1]/self.grid_spacing))]
        #Taking the first step
        step_dir = [NegGradX[prev_y_idx][prev_x_idx], NegGradY[prev_y_idx][prev_x_idx]]
        step_dir = step_size*(step_dir/np.linalg.norm(step_dir))
        self.ball_pos.append(np.sum([self.ball_pos[-1], step_dir], axis=0))
        #Let's get things going...
        while ct < max_iter:
            #Propose new move in the same direction as before
            prev_x_idx, prev_y_idx = [int(round(self.ball_pos[-1][0]/self.grid_spacing)),
                                      int(round(self.ball_pos[-1][1]/self.grid_spacing))]
            trial_pos = np.sum([self.ball_pos[-1], step_dir], axis=0)
            trial_idx = [int(round(trial_pos[0]/self.grid_spacing)),
                        int(round(trial_pos[1]/self.grid_spacing))]
            trial_en = self.z[trial_idx[1]][trial_idx[0]]
            prev_en = self.z[prev_y_idx][prev_x_idx]
            #Check to see if minimum reached
            if trial_en < prev_en:
                #If so, append the new ball position and at to count:
                self.ball_pos.append(trial_pos)
                ct += 1
            #If if has, try one perpendicular direction
            else:
                #To go perpendicular, swap x and y and negate one of them
                perp_dir = np.array([-step_dir[1], step_dir[0]])
                #Trial position and index
                trial_pos = np.sum([self.ball_pos[-1], perp_dir], axis=0)
                trial_idx = [int(round(trial_pos[0]/self.grid_spacing)),
                            int(round(trial_pos[1]/self.grid_spacing))]
                trial_en = self.z[trial_idx[1]][trial_idx[0]]
                prev_en = self.z[prev_y_idx][prev_x_idx]
                if trial_en < prev_en:
                    #If so, append the new ball position:
                    self.ball_pos.append(trial_pos)
                    step_dir = perp_dir
                    ct += 1
                #If that didn't work, try the other perpendicular direction
                #(one has to work) and add to the count
                else:
                    perp_dir = np.negative(perp_dir)
                    self.ball_pos.append(np.sum([self.ball_pos[-1], perp_dir], axis=0))
                    step_dir = perp_dir
                    ct +=1
            #Now check to see if the pecentage change in energy is
            #less than the tolerance
            if (trial_en - prev_en)/prev_en < tolerance:
                print("Steps needed to reach minimum: {}".format(str(ct)))
                break

    def line_search(self, tolerance=0.01):
        import numpy as np

        self.ball_pos = [self.ball_pos[0]]

        self.combine_wells()

        #Initializing the counter
        ct = 0
        #Defining the gradient
        NegGradY, NegGradX = np.negative(np.gradient(self.z))
        #Setting the last ball position
        init_x_idx, init_y_idx = [int(round(self.ball_pos[-1][0]/self.grid_spacing)),
                                  int(round(self.ball_pos[-1][1]/self.grid_spacing))]
        #Setting the direction of the first step
        step_dir = np.array([NegGradX[init_y_idx][init_x_idx], NegGradY[init_y_idx][init_x_idx]])
        step_dir = (1//np.linalg.norm(step_dir))*step_dir
        #Generating the first pair of points
        ##dist = abs(float(min(self.x_range, self.y_range)*(1/20.0)))
        #Set the initial point for the line search
        init_pt = self.ball_pos[-1]
        keep_going = True
        while keep_going:
            test_pts = [np.sum([init_pt, step_dir], axis=0),
                        np.sum([init_pt, 2.0*step_dir], axis=0)]
            test_x_idx_1, test_y_idx_1 = [int(test_pts[0][0]/self.grid_spacing),
                                          int(test_pts[0][1]/self.grid_spacing)]
            test_x_idx_2, test_y_idx_2 = [int(test_pts[1][0]/self.grid_spacing),
                                          int(test_pts[1][1]/self.grid_spacing)]
            if self.z[test_y_idx_2][test_x_idx_2] < self.z[test_y_idx_1][test_x_idx_1]:
                init_pt = test_pts[-1]
            else:
                keep_going = False

        x_pts = [init_pt[0], test_pts[0][0], test_pts[1][0]]
        y_pts = [init_pt[1], test_pts[0][1], test_pts[1][1]]
        fn_values = [self.z[init_y_idx][init_y_idx],
                     self.z[test_y_idx_1][test_x_idx_1],
                     self.z[test_y_idx_2][test_x_idx_2]]
        ax, bx, cx = np.polyfit(np.array(x_pts), np.array(fn_values), 2)
        ay, by, xy = np.polyfit(np.array(y_pts), np.array(fn_values), 2)
        min_pt = np.array([float(-bx/(2*ax)), float(-by/(2*ay))])
        energy_change = 1
        while energy_change > tolerance:
            x_pts.append(min_pt[0])
            y_pts.append(min_pt[1])
            last_x_idx, last_y_idx = [int(x_pts[-1]/self.grid_spacing),
                                      int(y_pts[-1]/self.grid_spacing)]
            fn_values.append(self.z[last_y_idx][last_x_idx])
            ax, bx, cx = np.polyfit(np.array(x_pts), np.array(fn_values), 2)
            ay, by, xy = np.polyfit(np.array(y_pts), np.array(fn_values), 2)
            min_pt = np.array([float(-bx/(2*ax)), float(-by/(2*ay))])
            min_x_idx, min_y_idx = [int(min_pt[0]/self.grid_spacing),
                                    int(min_pt[1]/self.grid_spacing)]
            energy_change = float(abs((self.z[min_y_idx][min_x_idx] - fn_values[-1])/fn_values[-1]))

        for i in range(len(x_pts)):
            self.ball_pos.append(np.array([x_pts[i], y_pts[i]]))

    def conjugate_gradient(self, max_iter=100, init_step_size=1, tolerance=0.0001):
        import numpy as np
        #Reset the ball position
        self.ball_pos = [self.ball_pos[0]]
        #Reconstruct the eneryg landscape
        self.combine_wells()

        #Initializing the counter
        ct = 0
        #Defining the gradient
        NegGradY, NegGradX = np.negative(np.gradient(self.z))
        #Setting the last ball position
        prev_x_idx, prev_y_idx = [int(round(self.ball_pos[-1][0]/self.grid_spacing)),
                                  int(round(self.ball_pos[-1][1]/self.grid_spacing))]
        #The step direction is determined by the (normalized) negative gradient
        step_dir = [NegGradX[prev_y_idx][prev_x_idx], NegGradY[prev_y_idx][prev_x_idx]]
        step_dir = init_step_size*(step_dir/np.linalg.norm(step_dir))
        self.ball_pos.append(np.sum([self.ball_pos[-1], step_dir], axis=0))
        while ct < max_iter:
            #Propose new move in the same direction as before
            prev_x_idx, prev_y_idx = [int(round(self.ball_pos[-1][0]/self.grid_spacing)),
                                      int(round(self.ball_pos[-1][1]/self.grid_spacing))]
            trial_pos = np.sum([self.ball_pos[-1], step_dir], axis=0)
            trial_idx = [int(round(trial_pos[0]/self.grid_spacing)),
                         int(round(trial_pos[1]/self.grid_spacing))]
            trial_en = self.z[trial_idx[1]][trial_idx[0]]
            prev_en = self.z[prev_y_idx][prev_x_idx]
            #Check to see if minimum reached
            if trial_en < prev_en:
                #If not, append the new ball position and at to count:
                self.ball_pos.append(trial_pos)
                ct += 1
                #Check to see if the percentage energy change is less than the tolerance
                if (trial_en - prev_en)/prev_en < tolerance:
                    print("Steps needed to reach minimum: {}".format(str(ct)))
                    break
            #If so, go in the direction determined by gamma
            else:
                #See lecture notebook for information on how gamma is defined
                prev_force = np.array([NegGradX[prev_y_idx][prev_x_idx], NegGradY[prev_y_idx][prev_x_idx]])
                trial_force = np.array([NegGradX[trial_idx[1]][trial_idx[0]], NegGradY[trial_idx[1]][trial_idx[0]]])
                diff_force = (trial_force - prev_force)
                gamma = np.dot(diff_force, trial_force)/np.dot(trial_force, trial_force)
                step_dir = np.sum([trial_force, gamma*step_dir], axis=0)
                self.ball_pos.append(np.sum([self.ball_pos[-1], step_dir], axis=0))
                ct += 1
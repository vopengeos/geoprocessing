import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('./Data/csv/gps_noise_2.csv') 
df.head(1000)
lat = np.array([df.latitude])
print(lat)

long = np.array([df.longitude])
print(long)
print(len(long[0]))

for i in range(len(long)):
    print(long[i][0])

for i in range(len(lat[0])):
    print(lat[0][i])

print(len(lat[0]))
print(len(long[0]))

#length of the arrays. the arrays should always have the same length
lng=len(lat[0])
print(lng)

for index in range(lng):
    print(lat[0][index])
print(long[0][index])


for index in range (lng):
    np.array((lat[0][index], long[0][index]))

coord1 = [list(i) for i in zip (lat[0],long[0])]
print(coord1)

from pylab import *
from numpy import *
import matplotlib.pyplot as plt

class Kalman:
    def __init__(self, ndim):
        self.ndim    = ndim
        self.Sigma_x = eye(ndim)*1e-4     # Process noise (Q)
        self.A       = eye(ndim)           # Transition matrix which 
# predict state for next time step (A)
        self.H       = eye(ndim)           # Observation matrix (H)
        self.mu_hat  = 0                    # State vector (X)
        self.cov     = eye(ndim)*0.01            # Process Covariance (P)
        self.R       = .001    # Sensor noise covariance matrix / 
# measurement error (R)

    def update(self, obs):

        # Make prediction
        self.mu_hat_est = dot(self.A,self.mu_hat)
        self.cov_est = dot(self.A,dot(self.cov,transpose(self.A))) + self.Sigma_x

        # Update estimate
        self.error_mu = obs - dot(self.H,self.mu_hat_est)
        self.error_cov = dot(self.H,dot(self.cov,transpose(self.H))) + self.R
        self.K = dot(dot(self.cov_est,transpose(self.H)),linalg.inv(self.error_cov))
        self.mu_hat = self.mu_hat_est + dot(self.K,self.error_mu)
        if ndim>1:
            self.cov = dot((eye(self.ndim) - 
dot(self.K,self.H)),self.cov_est)
        else:
            self.cov = (1-self.K)*self.cov_est 

if __name__ == "__main__":      
    #print "***** 1d ***********"
    ndim = 1
    nsteps = 3
    k = Kalman(ndim)    
    mu_init=array([54.907134])
    cov_init=0.001*ones((ndim))
    obs = random.normal(mu_init,cov_init,(ndim, nsteps))
    for t in range(ndim,nsteps):
        k.update(obs[:,t])
        print ("Actual: ", obs[:, t], "Prediction: ", k.mu_hat_est)

coord_output=[]

for coordinate in coord1:
    temp_list=[]
    ndim = 2
    nsteps = 100
    k = Kalman(ndim)    
    mu_init=np.array(coordinate)
    cov_init=0.0001*ones((ndim))
    obs = zeros((ndim, nsteps))
    for t in range(nsteps):
        obs[:, t] = random.normal(mu_init,cov_init)
    for t in range(ndim,nsteps):
        k.update(obs[:,t])
        print ("Actual: ", obs[:, t], "Prediction: ", k.mu_hat_est[0])
    temp_list.append(obs[:, t])
    temp_list.append(k.mu_hat_est[0])
    
    print("temp list")
    print(temp_list)
    coord_output.append(temp_list)

for coord_pair in coord_output:
    print(coord_pair[0])
    print(coord_pair[1])
    print("--------")

# print(line_actual)
# print(coord_output)


df2= pd.DataFrame(coord_output)
print(df2)

Actual = df2[0] 
Prediction = df2[1]
# print (Actual)
# print(Prediction)


Actual_df = pd.DataFrame(Actual)
Prediction_df = pd.DataFrame(Prediction)
# print(Actual_df)
# print(Prediction_df)


Actual_coord = pd.DataFrame(Actual_df[0].to_list(), columns = ['latitude','longitude'])
Actual_coord.to_csv('./Data/csv/gps_noise_2_Actual_noise.csv')

Prediction_coord = pd.DataFrame(Prediction_df[1].to_list(), columns = 
['latitude', 'longitude'])
Prediction_coord.to_csv('./Data/csv/gps_noise_2_prediction_noise.csv')

# print (Actual_coord)
# print (Prediction_coord)

Actual_coord.plot(kind='scatter',x='longitude',y='latitude',color='red')
plt.show()
Prediction_coord.plot(kind='scatter',x='longitude',y='latitude',
color='green')
plt.show()
import numpy as np
import matplotlib.pyplot as plt

def kalman_filter(z, process_variance, measurement_variance):
    # Initial state guess
    x_hat = 0.0
    # Initial estimate of error covariance
    P = 1.0

    # Kalman gain
    K = 0.0

    # Lists to store results for plotting
    x_hat_list = []
    P_list = []

    for measurement in z:
        # Prediction step
        x_hat_minus = x_hat
        P_minus = P + process_variance

        # Update step
        K = P_minus / (P_minus + measurement_variance)
        x_hat = x_hat_minus + K * (measurement - x_hat_minus)
        P = (1 - K) * P_minus

        # Store results for plotting
        x_hat_list.append(x_hat)
        P_list.append(P)

    return x_hat_list, P_list

# Generate synthetic GPS data with noise
np.random.seed(42)
true_values = np.linspace(0, 10, 100)
measurements = true_values + np.random.normal(0, 1, 100)

# Tune these parameters based on your specific scenario
process_variance = 0.1
measurement_variance = 1.0

# Apply Kalman filter
filtered_values, _ = kalman_filter(measurements, process_variance, measurement_variance)

# Plot the results
plt.plot(true_values, label='True Values', linestyle='dashed')
plt.scatter(range(len(measurements)), measurements, label='Noisy Measurements', marker='x')
plt.plot(filtered_values, label='Filtered Values', linestyle='dotted')
plt.legend()
plt.show()
# Import libraries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.stats.diagnostic import acorr_ljungbox
import statsmodels.api as sm

# For reproducibility
np.random.seed(42)

# (A) Data Simulation
T = 200
phi = 0.6
theta = -0.4

# Simulate ARIMA(1,1,1): ∇Zt = ϕ Zt−1 + εt + θ εt−1
e = np.random.normal(0, 1, T + 1)
Z_diff = np.zeros(T + 1)

for t in range(1, T + 1):
    Z_diff[t] = phi * Z_diff[t - 1] + e[t] + theta * e[t - 1]

Z = np.cumsum(Z_diff[1:])     # Original series
Z_diff = np.diff(Z)           # First difference

# Plot the time series and its first difference
plt.figure(figsize=(14, 5))

plt.subplot(1, 2, 1)
plt.plot(Z, label="Zt")
plt.title("Simulated ARIMA(1,1,1) Time Series")
plt.legend()

plt.subplot(1, 2, 2)
plt.plot(Z_diff, color='orange', label="ΔZt")
plt.title("First Difference of the Series")
plt.legend()

plt.tight_layout()
plt.show()

# (B) ACF and PACF of Zt
plt.figure(figsize=(8, 4))
plot_acf(Z, lags=40)
plt.title("ACF of Original Series")
plt.tight_layout()
plt.show()

plt.figure(figsize=(8, 4))
plot_pacf(Z, lags=40, method='ywm')
plt.title("PACF of Original Series")
plt.tight_layout()
plt.show()

# (C) Fit ARIMA(1,1,1) Model
model = ARIMA(Z, order=(1, 1, 1))
results = model.fit()

print(results.summary())
print("\nAIC of model:", results.aic)

# (D) Residual Diagnostics
residuals = results.resid

# Plot residuals and ACF of residuals
fig, axes = plt.subplots(1, 2, figsize=(12, 4))

axes[0].plot(residuals)
axes[0].set_title("Residuals")

plot_acf(residuals, lags=40, ax=axes[1])
axes[1].set_title("ACF of Residuals")

plt.tight_layout()
plt.show()

# Ljung-Box test
ljung = acorr_ljungbox(residuals, lags=[10], return_df=True)
print("\nLjung-Box Test (lag=10):")
print(ljung)

# Residual Normality Checks
sns.histplot(residuals, kde=True)
plt.title("Histogram of Residuals")
plt.show()

sm.qqplot(residuals, line='s')
plt.title("QQ Plot of Residuals")
plt.show()

# (E) Forecast Next 10 Points
forecast = results.get_forecast(steps=10)
pred = forecast.predicted_mean
conf_int = forecast.conf_int(alpha=0.05)

# Ensure correct indexing
conf_array = np.asarray(conf_int)

# Plot forecast
plt.figure(figsize=(10, 5))
plt.plot(Z, label="Observed")
plt.plot(np.arange(len(Z), len(Z) + 10), pred, label="Forecast", color='red')
plt.fill_between(np.arange(len(Z), len(Z) + 10),
                 conf_array[:, 0], conf_array[:, 1], color='pink', alpha=0.3)
plt.title("10-Step Forecast with 95% CI")
plt.legend()
plt.show()

# Forecast Table
forecast_df = pd.DataFrame({
    'Forecast': pred,
    'Lower 95%': conf_array[:, 0],
    'Upper 95%': conf_array[:, 1]
})
print("\nForecast Table:")
print(forecast_df)
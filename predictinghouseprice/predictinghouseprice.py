import pandas as pd
from sklearn.linear_model import LinearRegression

df = pd.DataFrame({
    'area sqft' : [1200, 1400, 1600, 1700, 1850],
    'rooms' : [3,4,3,5,4],
    'distance' : [5,3,8,2,4],
    'age' : [10,3,20,15,7],
    'price': [120,150,130,180,170]
})

X1 = df[['area sqft']]
X2 = df[['rooms']]
X3 = df[['distance']]
X4 = df[['age']]
X5 = df[['area sqft', 'rooms', 'distance', 'age']]
y = df['price']

model1 = LinearRegression().fit(X1, y)
model2 = LinearRegression().fit(X2, y) 
model3 = LinearRegression().fit(X3, y)
model4 = LinearRegression().fit(X4, y)
model5 = LinearRegression().fit(X5, y)
model_all = LinearRegression().fit(X5, y)

print("R^2 for area sqft:", model1.score(X1, y))
print("R^2 for rooms:", model2.score(X2, y))
print("R^2 for distance:", model3.score(X3, y)) 
print("R^2 for age:", model4.score(X4, y))
print("R^2 for all features:", model5.score(X5, y))
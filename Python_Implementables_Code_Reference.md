# Python-Implementable ML Concepts — Code Reference

Prepared: November 11, 2025


> Compact, copy-paste-ready Python snippets for common ML exam topics. Each section shows a minimal, runnable example using standard libraries.

---

## 🐍 Key Python Libraries

```python
# Core scientific stack
import numpy as np
import pandas as pd
from scipy import stats

# Plotting
import matplotlib.pyplot as plt  # Avoid seaborn if instructions prohibit it

# Machine Learning
from sklearn import datasets, model_selection, metrics
from sklearn.preprocessing import StandardScaler, MinMaxScaler, OneHotEncoder, LabelEncoder, PolynomialFeatures
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer

# Models
from sklearn.linear_model import LinearRegression, LogisticRegression, Lasso, SGDClassifier, SGDRegressor
from sklearn.naive_bayes import GaussianNB, MultinomialNB, BernoulliNB
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, GradientBoostingClassifier, GradientBoostingRegressor
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.feature_selection import SelectKBest, f_classif, VarianceThreshold, RFE
from sklearn.metrics import (accuracy_score, f1_score, precision_score, recall_score,
                             confusion_matrix, ConfusionMatrixDisplay, r2_score,
                             mean_squared_error, mean_absolute_error, silhouette_score, log_loss)
from sklearn.model_selection import (train_test_split, cross_val_score, KFold, StratifiedKFold,
                                     LeaveOneOut, GridSearchCV, RandomizedSearchCV)

# Time series (statsmodels)
import statsmodels.api as sm
from statsmodels.tsa.arima.model import ARIMA
```

---

## 🧠 Supervised Learning Algorithms

### Linear Regression
```python
X, y = datasets.load_diabetes(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42)
model = LinearRegression().fit(X_train, y_train)
pred = model.predict(X_test)
print("R2:", r2_score(y_test, pred))
```

### Multiple Linear Regression
```python
# Same as LinearRegression with multiple columns
df = pd.DataFrame(X_train).assign(y=y_train)
model = LinearRegression().fit(X_train, y_train)
print(model.coef_, model.intercept_)
```

### Lasso Regression (L1)
```python
X, y = datasets.load_diabetes(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=0)
model = Lasso(alpha=0.01).fit(X_train, y_train)
print("Non-zero features:", np.sum(model.coef_ != 0))
```

### Logistic Regression
```python
X, y = datasets.load_breast_cancer(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=0, stratify=y)
pipe = Pipeline([("scaler", StandardScaler()), ("clf", LogisticRegression(max_iter=2000))])
pipe.fit(X_train, y_train)
print("Accuracy:", pipe.score(X_test, y_test))
```

### Multinomial Logistic Regression
```python
X, y = datasets.load_iris(return_X_y=True)
pipe = Pipeline([("scaler", StandardScaler()), ("clf", LogisticRegression(multi_class="multinomial", max_iter=2000))])
scores = cross_val_score(pipe, X, y, cv=5)
print("CV mean accuracy:", scores.mean())
```

### Naive Bayes (Gaussian, Multinomial, Bernoulli)
```python
# GaussianNB on continuous features
X, y = datasets.load_iris(return_X_y=True)
print("GaussianNB:", cross_val_score(GaussianNB(), X, y, cv=5).mean())

# MultinomialNB for counts
X_counts = np.random.poisson(1.0, size=(200, 20))
y = np.random.randint(0, 2, size=200)
print("MultinomialNB:", cross_val_score(MultinomialNB(), X_counts, y, cv=5).mean())

# BernoulliNB for binary features
X_bin = (np.random.rand(200, 20) > 0.7).astype(int)
y = np.random.randint(0, 2, size=200)
print("BernoulliNB:", cross_val_score(BernoulliNB(), X_bin, y, cv=5).mean())
```

### Decision Trees (CART) - Classifier
```python
X, y = datasets.load_breast_cancer(return_X_y=True)
clf = DecisionTreeClassifier(random_state=0, max_depth=4)
scores = cross_val_score(clf, X, y, cv=5)
print("DecisionTree (CART) mean accuracy:", scores.mean())
```

### Decision Trees - Regressor
```python
X, y = datasets.load_diabetes(return_X_y=True)
reg = DecisionTreeRegressor(random_state=0, max_depth=4).fit(X, y)
print("R2:", cross_val_score(reg, X, y, cv=5, scoring="r2").mean())
```

### Random Forests
```python
X, y = datasets.load_breast_cancer(return_X_y=True)
rf = RandomForestClassifier(n_estimators=200, random_state=0)
print("RF accuracy:", cross_val_score(rf, X, y, cv=5).mean())
```

### Gradient Boosting
```python
X, y = datasets.load_breast_cancer(return_X_y=True)
gb = GradientBoostingClassifier(random_state=0)
print("GB accuracy:", cross_val_score(gb, X, y, cv=5).mean())
```

### Gradient Descent (SGDClassifier/Regressor)
```python
X, y = datasets.load_breast_cancer(return_X_y=True)
pipe = Pipeline([("scaler", StandardScaler()), ("sgd", SGDClassifier(loss="log_loss", max_iter=2000, tol=1e-3, random_state=0))])
print("SGDClassifier accuracy:", cross_val_score(pipe, X, y, cv=5).mean())

Xr, yr = datasets.load_diabetes(return_X_y=True)
sgd_reg = Pipeline([("scaler", StandardScaler()), ("sgd", SGDRegressor(max_iter=2000, tol=1e-3, random_state=0))])
print("SGDRegressor R2:", cross_val_score(sgd_reg, Xr, yr, cv=5, scoring="r2").mean())
```

### K-Nearest Neighbors (KNN)
```python
X, y = datasets.load_iris(return_X_y=True)
knn = KNeighborsClassifier(n_neighbors=5)
print("KNN accuracy:", cross_val_score(knn, X, y, cv=5).mean())
```

### Time-Series Models (ARIMA)
```python
# Simple ARIMA on synthetic series
np.random.seed(0)
y = np.cumsum(np.random.normal(size=200))  # random walk
model = ARIMA(y, order=(1,1,1)).fit()
print(model.summary().tables[0])
```

### Weighted Least Squares (WLS)
```python
# WLS with heteroscedastic noise
np.random.seed(0)
X = np.column_stack([np.ones(100), np.linspace(0, 10, 100)])
beta = np.array([1.0, 2.0])
sigma = np.linspace(1, 3, 100)
y = X @ beta + np.random.normal(scale=sigma)

w = 1 / (sigma**2)
wls = sm.WLS(y, X, weights=w).fit()
print(wls.summary().tables[0])
```

---

## 🧩 Unsupervised Learning Algorithms

### K-Means Clustering + Elbow WCSS
```python
X, _ = datasets.make_blobs(n_samples=400, centers=4, cluster_std=1.0, random_state=0)
wcss = []
for k in range(1, 10):
    km = KMeans(n_clusters=k, n_init=10, random_state=0).fit(X)
    wcss.append(km.inertia_)
plt.figure()
plt.plot(range(1, 10), wcss, marker="o")
plt.xlabel("k"); plt.ylabel("WCSS"); plt.title("Elbow Method")
plt.show()
```

### Hierarchical Clustering
```python
X, _ = datasets.make_blobs(n_samples=200, centers=3, cluster_std=1.2, random_state=0)
hc = AgglomerativeClustering(n_clusters=3, linkage="ward").fit(X)
print("Labels shape:", hc.labels_.shape)
```

### PCA (Dimensionality Reduction)
```python
X, y = datasets.load_iris(return_X_y=True)
pca = PCA(n_components=2).fit_transform(X)
print("PCA shape:", pca.shape)
```

### t-SNE (Visualization)
```python
X, y = datasets.load_digits(return_X_y=True)
emb = TSNE(n_components=2, learning_rate="auto", init="pca", random_state=0).fit_transform(X)
print("t-SNE shape:", emb.shape)
```

### Anomaly Detection (IsolationForest / LOF)
```python
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor

X, _ = datasets.make_blobs(n_samples=300, centers=1, cluster_std=1.0, random_state=0)
X[::30] += 8.0  # inject outliers

print("IsolationForest outlier ratio:",
      (IsolationForest(random_state=0).fit_predict(X) == -1).mean())

print("LOF outlier ratio:",
      (LocalOutlierFactor(n_neighbors=20).fit_predict(X) == -1).mean())
```

---

## 🛠 Preprocessing & Feature Engineering

### Handling Missing Values (Imputation)
```python
df = pd.DataFrame({"a":[1,np.nan,3], "b":[4,5,np.nan]})
imp = SimpleImputer(strategy="mean")
filled = imp.fit_transform(df)
print(filled)
```

### Scaling (Standardization / Min-Max)
```python
X = np.array([[1., 10.], [2., 0.], [3., 5.]])
print("StandardScaler:\n", StandardScaler().fit_transform(X))
print("MinMaxScaler:\n", MinMaxScaler().fit_transform(X))
```

### Encoding Categorical Variables
```python
X = pd.DataFrame({"cat":["red","blue","red"], "num":[1,2,3]})
ct = ColumnTransformer([("onehot", OneHotEncoder(handle_unknown="ignore"), ["cat"])],
                       remainder="passthrough")
print(ct.fit_transform(X).toarray())
```

### CountVectorizer (Bag-of-Words) and TF-IDF
```python
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
docs = ["cats like milk", "dogs like bones", "cats and dogs"]
print("BoW shape:", CountVectorizer().fit_transform(docs).shape)
print("TF-IDF shape:", TfidfVectorizer().fit_transform(docs).shape)
```

### KBinsDiscretizer (Binning)
```python
from sklearn.preprocessing import KBinsDiscretizer
X = np.array([[0.5],[1.5],[2.5],[3.5]])
binner = KBinsDiscretizer(n_bins=2, encode="ordinal", strategy="uniform")
print(binner.fit_transform(X).ravel())
```

### Covariance Matrix & Pearson Correlation
```python
X = np.random.randn(100, 3)
print("Covariance:\n", np.cov(X, rowvar=False))
df = pd.DataFrame(X, columns=list("abc"))
print("Pearson corr:\n", df.corr())
```

### Euclidean Distance
```python
from sklearn.metrics.pairwise import euclidean_distances
A = np.array([[0,0],[1,1],[2,2]])
print(euclidean_distances(A, A))
```

### Feature Selection (SelectKBest), Variance Threshold, RFE
```python
X, y = datasets.load_breast_cancer(return_X_y=True)
skb = SelectKBest(score_func=f_classif, k=10).fit(X, y)
print("KBest mask:", skb.get_support().sum())

vt = VarianceThreshold(threshold=0.0).fit(X)
print("Kept features after VT:", vt.get_support().sum())

est = LogisticRegression(max_iter=2000)
rfe = RFE(estimator=est, n_features_to_select=10).fit(X, y)
print("RFE kept:", rfe.get_support().sum())
```

### Polynomial Features & Interaction Terms
```python
X = np.array([[1,2],[3,4],[5,6]])
poly = PolynomialFeatures(degree=2, include_bias=False)
print(poly.fit_transform(X))
```

### Log Transformation
```python
x = np.array([1, 2, 10, 100], dtype=float)
print(np.log(x))
```

### Date/Time Parts Extraction
```python
s = pd.to_datetime(pd.Series(["2025-01-15 12:34:56", "2025-07-01 08:00:00"]))
df = pd.DataFrame({"ts": s})
df["year"] = df["ts"].dt.year
df["month"] = df["ts"].dt.month
df["hour"] = df["ts"].dt.hour
print(df)
```

### Bootstrap Samples (with replacement)
```python
from sklearn.utils import resample
X = np.arange(10)
boot = resample(X, replace=True, n_samples=10, random_state=0)
print(boot)
```

### ML Pipeline
```python
X, y = datasets.load_breast_cancer(return_X_y=True)
num_idx = slice(0, X.shape[1])  # all numeric
pre = ColumnTransformer([("scale", StandardScaler(), num_idx)])
pipe = Pipeline([("pre", pre), ("clf", LogisticRegression(max_iter=2000))])
print("CV accuracy:", cross_val_score(pipe, X, y, cv=5).mean())
```

### Summary Statistics
```python
df = pd.DataFrame(np.random.randn(100, 3), columns=["a","b","c"])
print(df.describe())
```

---

## 📊 Model Evaluation (Metrics)

### Classification: Accuracy, Precision, Recall, F1, Confusion Matrix
```python
X, y = datasets.load_breast_cancer(return_X_y=True)
X_tr, X_te, y_tr, y_te = train_test_split(X, y, stratify=y, random_state=0)
clf = RandomForestClassifier(random_state=0).fit(X_tr, y_tr)
pred = clf.predict(X_te)
print("Accuracy:", accuracy_score(y_te, pred))
print("Precision:", precision_score(y_te, pred))
print("Recall:", recall_score(y_te, pred))
print("F1:", f1_score(y_te, pred))
cm = confusion_matrix(y_te, pred)
disp = ConfusionMatrixDisplay(confusion_matrix=cm)
disp.plot()
plt.show()
```

### Regression: MSE, RMSE, MAE, R2, RSS
```python
X, y = datasets.load_diabetes(return_X_y=True)
X_tr, X_te, y_tr, y_te = train_test_split(X, y, random_state=0)
reg = RandomForestRegressor(random_state=0).fit(X_tr, y_tr)
pred = reg.predict(X_te)
mse = mean_squared_error(y_te, pred)
print("MSE:", mse)
print("RMSE:", mean_squared_error(y_te, pred, squared=False))
print("MAE:", mean_absolute_error(y_te, pred))
print("R2:", r2_score(y_te, pred))
print("RSS:", mse * len(y_te))
```

### Log-Loss (Cross-Entropy)
```python
X, y = datasets.load_breast_cancer(return_X_y=True)
X_tr, X_te, y_tr, y_te = train_test_split(X, y, stratify=y, random_state=0)
proba = LogisticRegression(max_iter=2000).fit(X_tr, y_tr).predict_proba(X_te)
print("Log-loss:", log_loss(y_te, proba))
```

### Silhouette Score (Clustering quality)
```python
X, _ = datasets.make_blobs(n_samples=300, centers=3, random_state=0)
labels = KMeans(n_clusters=3, n_init=10, random_state=0).fit_predict(X)
print("Silhouette:", silhouette_score(X, labels))
```

### Chi-square Test (Independence)
```python
from scipy.stats import chi2_contingency
table = np.array([[10, 20, 30],
                  [6,  9,  17]])
chi2, p, dof, exp = chi2_contingency(table)
print("chi2:", chi2, "p:", p, "dof:", dof)
```

### F-Test (ANOVA)
```python
from scipy.stats import f_oneway
g1 = np.random.randn(30) + 0.0
g2 = np.random.randn(30) + 0.5
g3 = np.random.randn(30) - 0.5
stat, p = f_oneway(g1, g2, g3)
print("ANOVA F:", stat, "p:", p)
```

### AIC / BIC (statsmodels)
```python
X, y = datasets.load_diabetes(return_X_y=True)
X = sm.add_constant(X)
ols = sm.OLS(y, X).fit()
print("AIC:", ols.aic, "BIC:", ols.bic)
```

---

## 🧪 Model Selection & Validation

### Train/Test Split (Holdout)
```python
X, y = datasets.load_iris(return_X_y=True)
X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, stratify=y, random_state=0)
print(X_tr.shape, X_te.shape)
```

### K-Fold and Stratified K-Fold
```python
X, y = datasets.load_breast_cancer(return_X_y=True)
print("KFold:", cross_val_score(LogisticRegression(max_iter=2000), X, y, cv=KFold(n_splits=5, shuffle=True, random_state=0)).mean())
print("StratifiedKFold:", cross_val_score(LogisticRegression(max_iter=2000), X, y, cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=0)).mean())
```

### Leave-One-Out Cross-Validation (LOOCV)
```python
X, y = datasets.load_iris(return_X_y=True)
loo = LeaveOneOut()
scores = cross_val_score(LinearRegression(), X, y, cv=loo)
print("LOOCV mean score:", scores.mean())
```

### Grid Search
```python
X, y = datasets.load_breast_cancer(return_X_y=True)
pipe = Pipeline([("scaler", StandardScaler()), ("clf", LogisticRegression(max_iter=2000))])
param_grid = {"clf__C":[0.01, 0.1, 1, 10], "clf__penalty":["l2"], "clf__solver":["lbfgs"]}
gs = GridSearchCV(pipe, param_grid, cv=5, n_jobs=None).fit(X, y)
print("Best params:", gs.best_params_, "Best score:", gs.best_score_)
```

### Randomized Search
```python
from scipy.stats import loguniform
X, y = datasets.load_breast_cancer(return_X_y=True)
pipe = Pipeline([("scaler", StandardScaler()), ("clf", LogisticRegression(max_iter=2000))])
param_dist = {"clf__C": loguniform(1e-3, 1e+3)}
rs = RandomizedSearchCV(pipe, param_distributions=param_dist, n_iter=20, cv=5, random_state=0).fit(X, y)
print("Best params:", rs.best_params_, "Best score:", rs.best_score_)
```

### Forward/Backward Selection (simple manual sketch)
```python
# Forward selection sketch using cross_val_score as objective
from itertools import combinations

X, y = datasets.load_breast_cancer(return_X_y=True)
best_feats, best_score = [], -np.inf
features = range(X.shape[1])
for k in range(1, 6):
    for combo in combinations(features, k):
        score = cross_val_score(LogisticRegression(max_iter=2000),
                                X[:, combo], y, cv=5).mean()
        if score > best_score:
            best_score, best_feats = score, combo
print("Forward best k<=5:", best_feats, best_score)
```

### Probability Threshold Tuning
```python
X, y = datasets.load_breast_cancer(return_X_y=True)
X_tr, X_te, y_tr, y_te = train_test_split(X, y, stratify=y, random_state=0)
lr = LogisticRegression(max_iter=2000).fit(X_tr, y_tr)
proba = lr.predict_proba(X_te)[:,1]
threshold = 0.3
pred = (proba >= threshold).astype(int)
print("Precision:", precision_score(y_te, pred), "Recall:", recall_score(y_te, pred))
```

### Recursive Feature Elimination (RFE)
```python
X, y = datasets.load_breast_cancer(return_X_y=True)
est = LogisticRegression(max_iter=2000)
rfe = RFE(estimator=est, n_features_to_select=10).fit(X, y)
print("Selected indices:", np.where(rfe.get_support())[0])
```

---

## Appendix: Quick Utilities

### Residuals and Diagnostic Plot (Regression)
```python
X, y = datasets.load_diabetes(return_X_y=True)
X_tr, X_te, y_tr, y_te = train_test_split(X, y, random_state=0)
reg = LinearRegression().fit(X_tr, y_tr)
pred = reg.predict(X_te)
resid = y_te - pred
plt.figure()
plt.scatter(pred, resid)
plt.axhline(0)
plt.xlabel("Predicted"); plt.ylabel("Residuals"); plt.title("Residual Plot")
plt.show()
```

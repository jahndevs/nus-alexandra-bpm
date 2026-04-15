import numpy as np
from sklearn.svm import SVR
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.multioutput import MultiOutputRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, root_mean_squared_error


# train support vector regressor to predict SBP and DBP from extracted features
def train(X, y, kernel="rbf", C=10.0, epsilon=0.5, test_size=0.2, random_state=42):
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=test_size, random_state=random_state)

    # svr is scale-sensitive, so standardize features and wrap for multi-output
    model = Pipeline([
        ("scaler", StandardScaler()),
        ("svr", MultiOutputRegressor(SVR(kernel=kernel, C=C, epsilon=epsilon))),
    ])

    model.fit(X_tr, y_tr)
    preds = model.predict(X_te)

    metrics = {
        "mae_sbp": mean_absolute_error(y_te[:, 0], preds[:, 0]),
        "mae_dbp": mean_absolute_error(y_te[:, 1], preds[:, 1]),
        "rmse_sbp": root_mean_squared_error(y_te[:, 0], preds[:, 0]),
        "rmse_dbp": root_mean_squared_error(y_te[:, 1], preds[:, 1]),
    }

    return model, metrics


def predict(model, features):
    x = np.array(list(features.values())).reshape(1, -1)
    sbp, dbp = model.predict(x)[0]

    return sbp, dbp


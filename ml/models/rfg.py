import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, root_mean_squared_error

# train random forest regressor to predict SBP and DBP from from extracted features
def train(X, y, n_estimators=200, test_size=0.2, random_state=42):
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=test_size, random_state=random_state)

    model = RandomForestRegressor(n_estimators=n_estimators, random_state=random_state, n_jobs=-1)

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
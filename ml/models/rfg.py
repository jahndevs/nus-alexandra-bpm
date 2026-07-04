import numpy as np
from sklearn.ensemble import RandomForestRegressor


# fit random forest regressor predicting [SBP, DBP] from beat features
def train(X, y, n_estimators=300, random_state=42):
    model = RandomForestRegressor(
        n_estimators=n_estimators,
        random_state=random_state,
        n_jobs=-1,
    )
    model.fit(X, y)
    return model


def predict(model, features):
    x = np.array(list(features.values())).reshape(1, -1)
    sbp, dbp = model.predict(x)[0]
    return sbp, dbp

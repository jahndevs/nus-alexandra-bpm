import numpy as np
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.multioutput import MultiOutputRegressor


# fit histogram gradient boosting regressor predicting [SBP, DBP] from beat
# features.
def train(
    X,
    y,
    max_iter=300,
    learning_rate=0.05,
    max_leaf_nodes=31,
    min_samples_leaf=20,
    l2_regularization=0.0,
    random_state=42,
):
    base = HistGradientBoostingRegressor(
        max_iter=max_iter,
        learning_rate=learning_rate,
        max_leaf_nodes=max_leaf_nodes,
        min_samples_leaf=min_samples_leaf,
        l2_regularization=l2_regularization,
        random_state=random_state,
    )
    model = MultiOutputRegressor(base, n_jobs=-1)
    model.fit(X, y)
    return model


def predict(model, features):
    x = np.array(list(features.values())).reshape(1, -1)
    sbp, dbp = model.predict(x)[0]
    return sbp, dbp

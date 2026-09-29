import numpy as np

class LinearRegression:
    """
    Linear Regression model implemented with NumPy (Ordinary Least Squares).
    Provides exact same scikit-learn API: fit(X, y), predict(X), coef_, intercept_.
    """
    def __init__(self):
        self.coef_ = np.array([0.0])
        self.intercept_ = 0.0

    def fit(self, X, y):
        x_flat = np.array(X, dtype=float).flatten()
        y_flat = np.array(y, dtype=float).flatten()
        if len(x_flat) > 1:
            slope, intercept = np.polyfit(x_flat, y_flat, 1)
            self.coef_ = np.array([float(slope)])
            self.intercept_ = float(intercept)
        else:
            self.coef_ = np.array([0.0])
            self.intercept_ = float(y_flat[0]) if len(y_flat) > 0 else 0.0
        return self

    def predict(self, X):
        x_flat = np.array(X, dtype=float).flatten()
        return (x_flat * self.coef_[0]) + self.intercept_


def predict_future_score(results_data):
    """
    Uses Linear Regression to forecast the next mock test percentage score.
    results_data: list of dicts with keys:
    ['result_id', 'exam_id', 'exam_name', 'score', 'total_questions', 'percentage', 'test_date']
    """
    if not results_data or len(results_data) < 2:
        return {
            "has_prediction": False,
            "tests_evaluated": len(results_data) if results_data else 0,
            "min_required": 2,
            "predicted_percentage": None,
            "predicted_range": None,
            "readiness_index": None,
            "confidence": "Low",
            "message": "Not enough test history available for a reliable prediction. Complete at least 2 mock tests to unlock AI score prediction.",
            "historical_points": []
        }

    # Extract historical scores in chronological order (oldest to newest)
    scores = [float(r["percentage"]) for r in reversed(results_data)]
    n = len(scores)

    # Prepare features: X = attempt numbers (1, 2, ..., n)
    X = np.array(range(1, n + 1)).reshape(-1, 1)
    y = np.array(scores)

    # Train linear regression model
    model = LinearRegression()
    model.fit(X, y)

    # Predict for next attempt (n + 1)
    next_attempt = np.array([[n + 1]])
    predicted_raw = float(model.predict(next_attempt)[0])

    # Weighted blend with recent exponential moving average for robust prediction
    weights = np.exp(np.linspace(-1, 0, n))
    weights /= weights.sum()
    ema = float(np.sum(y * weights))

    # Blended prediction (60% regression trend, 40% weighted average)
    blended_prediction = (0.6 * predicted_raw) + (0.4 * ema)

    # Clamp prediction between 5% and 99%
    predicted_score = round(max(5.0, min(99.0, float(blended_prediction))), 1)

    # Prediction confidence & uncertainty margin
    std_dev = float(np.std(scores)) if n > 2 else 5.0
    margin = round(min(12.0, max(3.0, std_dev * 0.8)), 1)
    low_bound = round(max(0.0, predicted_score - margin), 1)
    high_bound = round(min(100.0, predicted_score + margin), 1)

    if n >= 5:
        confidence = "High"
    elif n >= 3:
        confidence = "Moderate"
    else:
        confidence = "Preliminary (2 Tests)"

    # Compute Exam Readiness Index (0-100%)
    readiness_index = round(min(100.0, (predicted_score * 0.7) + (min(n, 10) * 3.0)), 1)

    # Educational explanation
    slope_val = float(model.coef_[0])
    trend_direction = "improving" if slope_val > 0.5 else ("declining" if slope_val < -0.5 else "steady")
    explanation = (
        f"Based on linear regression modeling over your {n} test attempts, "
        f"your score trajectory is currently {trend_direction}. "
        f"We project your next mock test score to be around {predicted_score}% "
        f"(expected range: {low_bound}% – {high_bound}%)."
    )

    historical_points = [
        {"attempt": i + 1, "score": round(scores[i], 1)}
        for i in range(n)
    ]

    return {
        "has_prediction": True,
        "tests_evaluated": n,
        "predicted_percentage": predicted_score,
        "predicted_range": f"{low_bound}% – {high_bound}%",
        "low_bound": low_bound,
        "high_bound": high_bound,
        "readiness_index": readiness_index,
        "confidence": confidence,
        "trend_slope": round(slope_val, 2),
        "message": explanation,
        "historical_points": historical_points
    }

import numpy as np
import pandas as pd

def analyze_student_performance(results_data):
    """
    Analyzes historical test results for a student.
    results_data: list of dicts with keys:
    ['result_id', 'exam_id', 'exam_name', 'score', 'total_questions', 'percentage', 'test_date']
    """
    if not results_data:
        return {
            "has_data": False,
            "total_tests": 0,
            "avg_score": 0,
            "avg_percentage": 0,
            "highest_percentage": 0,
            "lowest_percentage": 0,
            "latest_percentage": 0,
            "trend": "Insufficient Data",
            "trend_badge": "neutral",
            "insights": ["Complete your first mock test to see your AI-powered performance analysis."],
            "exam_breakdown": [],
            "weak_areas": [],
            "strong_areas": []
        }

    df = pd.DataFrame(results_data)
    # Ensure columns exist and have numeric values
    df["percentage"] = pd.to_numeric(df["percentage"], errors="coerce").fillna(0.0)
    df["score"] = pd.to_numeric(df["score"], errors="coerce").fillna(0)
    df["total_questions"] = pd.to_numeric(df["total_questions"], errors="coerce").fillna(1)

    total_tests = len(df)
    avg_percentage = float(df["percentage"].mean())
    highest_percentage = float(df["percentage"].max())
    lowest_percentage = float(df["percentage"].min())
    latest_percentage = float(df["percentage"].iloc[0])  # If results_data is sorted by date desc

    # Performance Trend Calculation
    if total_tests >= 3:
        # chronological order for trend
        chronological_scores = df["percentage"].values[::-1]
        x = np.arange(len(chronological_scores))
        # Linear slope
        slope, _ = np.polyfit(x, chronological_scores, 1)
        if slope > 1.5:
            trend = "Improving"
            trend_badge = "positive"
            trend_insight = f"Your performance is on an upward trajectory (+{slope:.1f}% per test average). Excellent consistency!"
        elif slope < -1.5:
            trend = "Needs Attention"
            trend_badge = "warning"
            trend_insight = "Your recent test scores show a slight dip. We recommend revising earlier topics and practicing timed quizzes."
        else:
            trend = "Stable"
            trend_badge = "neutral"
            trend_insight = "Your average score is steady. Try solving higher difficulty questions to break through your current score ceiling."
    elif total_tests == 2:
        diff = df["percentage"].iloc[0] - df["percentage"].iloc[1]
        if diff > 0:
            trend = "Improving"
            trend_badge = "positive"
            trend_insight = f"Your latest score improved by {diff:.1f}% compared to your previous attempt."
        elif diff < 0:
            trend = "Declining"
            trend_badge = "warning"
            trend_insight = f"Your latest score dropped by {abs(diff):.1f}%. Review your incorrect answers to identify knowledge gaps."
        else:
            trend = "Consistent"
            trend_badge = "neutral"
            trend_insight = "Your score remained unchanged across consecutive tests. Aim for targeted practice to gain higher accuracy."
    else:
        trend = "Initial Assessment"
        trend_badge = "neutral"
        trend_insight = "First test recorded. Take at least 2-3 more mock tests to enable advanced multi-test trend analytics."

    # Exam-wise performance breakdown
    exam_groups = df.groupby("exam_name")
    exam_breakdown = []
    weak_areas = []
    strong_areas = []

    for name, group in exam_groups:
        exam_avg = float(group["percentage"].mean())
        exam_count = len(group)
        exam_high = float(group["percentage"].max())
        exam_breakdown.append({
            "exam_name": name,
            "attempts": exam_count,
            "avg_percentage": round(exam_avg, 1),
            "highest_percentage": round(exam_high, 1)
        })
        if exam_avg < 60:
            weak_areas.append(name)
        elif exam_avg >= 75:
            strong_areas.append(name)

    # Sort breakdown by attempts descending
    exam_breakdown.sort(key=lambda x: x["attempts"], reverse=True)

    # Generate Educational Insights
    insights = [trend_insight]
    if weak_areas:
        insights.append(f"Focus Area: Prioritize practice for {', '.join(weak_areas)} where your current average is below 60%.")
    if strong_areas:
        insights.append(f"Strength Area: You have demonstrated strong competency in {', '.join(strong_areas)} (>= 75% accuracy).")
    if avg_percentage >= 80:
        insights.append("Exam Readiness: Excellent! You are maintaining high readiness for your competitive exams.")
    elif avg_percentage >= 60:
        insights.append("Exam Readiness: Moderate readiness. Dedicate 30 minutes daily to mock test question reviews.")
    else:
        insights.append("Exam Readiness: Foundational stage. Focus on concept clarity and structured topic-wise revision.")

    return {
        "has_data": True,
        "total_tests": total_tests,
        "avg_percentage": round(avg_percentage, 1),
        "highest_percentage": round(highest_percentage, 1),
        "lowest_percentage": round(lowest_percentage, 1),
        "latest_percentage": round(latest_percentage, 1),
        "trend": trend,
        "trend_badge": trend_badge,
        "insights": insights,
        "exam_breakdown": exam_breakdown,
        "weak_areas": weak_areas,
        "strong_areas": strong_areas
    }

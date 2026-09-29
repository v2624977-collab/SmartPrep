import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from ai.analytics import analyze_student_performance
from ai.planner import generate_study_plan
from ai.prediction import predict_future_score

sample_data = [
    {"result_id": 5, "exam_id": 1, "exam_name": "TANCET", "score": 4, "total_questions": 5, "percentage": 80.0, "test_date": "2026-08-28"},
    {"result_id": 4, "exam_id": 1, "exam_name": "TANCET", "score": 3, "total_questions": 5, "percentage": 60.0, "test_date": "2026-08-28"},
    {"result_id": 3, "exam_id": 2, "exam_name": "GATE", "score": 2, "total_questions": 5, "percentage": 40.0, "test_date": "2026-08-27"},
    {"result_id": 2, "exam_id": 1, "exam_name": "TANCET", "score": 4, "total_questions": 5, "percentage": 80.0, "test_date": "2026-08-27"},
]

analytics = analyze_student_performance(sample_data)
planner = generate_study_plan(analytics)
prediction = predict_future_score(sample_data)

print("AI Test - Analytics avg:", analytics["avg_percentage"], "trend:", analytics["trend"])
print("AI Test - Planner type:", planner["plan_type"], "primary focus:", planner["primary_subject"])
print("AI Test - Prediction score:", prediction["predicted_percentage"], "confidence:", prediction["confidence"])

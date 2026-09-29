def generate_study_plan(performance_data, target_exam_name=None, daily_hours=2):
    """
    Generates a personalized 7-day weekly schedule.
    performance_data: dict from analyze_student_performance
    """
    has_data = performance_data.get("has_data", False)
    weak_areas = performance_data.get("weak_areas", [])
    strong_areas = performance_data.get("strong_areas", [])
    avg_percentage = performance_data.get("avg_percentage", 0)

    # Primary focus subject
    if target_exam_name and target_exam_name != "All":
        primary_subject = target_exam_name
    elif weak_areas:
        primary_subject = weak_areas[0]
    elif performance_data.get("exam_breakdown"):
        primary_subject = performance_data["exam_breakdown"][0]["exam_name"]
    else:
        primary_subject = "Core Quantitative & Analytical Skills"

    secondary_subject = "Logical Reasoning & General Studies"
    if len(weak_areas) > 1:
        secondary_subject = weak_areas[1]
    elif strong_areas:
        secondary_subject = strong_areas[0]

    plan_type = "Personalized Adaptive Plan" if has_data else "Foundational Beginner Roadmap"

    schedule = [
        {
            "day": "Monday",
            "focus": f"{primary_subject} – Core Concepts",
            "duration": f"{daily_hours} Hours",
            "tasks": [
                "Review foundational theory, formulas, and definitions.",
                "Solve 15-20 textbook conceptual problems.",
                "Note down common doubt questions for weekend review."
            ],
            "tag": "Theory & Concepts"
        },
        {
            "day": "Tuesday",
            "focus": f"{secondary_subject} – Problem Solving",
            "duration": f"{daily_hours} Hours",
            "tasks": [
                "Practice high-frequency question patterns.",
                "Work on short-cut methods and mental calculation tricks.",
                "Complete a 15-minute speed quiz."
            ],
            "tag": "Practice"
        },
        {
            "day": "Wednesday",
            "focus": f"{primary_subject} – Advanced Problems & Weak Topics",
            "duration": f"{daily_hours} Hours",
            "tasks": [
                "Tackle difficult and multi-step problems.",
                "Revisit questions answered incorrectly in past mock tests.",
                "Create a one-page summary cheat-sheet."
            ],
            "tag": "Deep Dive"
        },
        {
            "day": "Thursday",
            "focus": "Verbal Ability, Reading Comprehension & General Awareness",
            "duration": f"{daily_hours} Hours",
            "tasks": [
                "Read analytical articles, vocabulary lists, and grammar rules.",
                "Practice 2 reading comprehension passages with time limits.",
                "Review key current affairs and static general knowledge."
            ],
            "tag": "Verbal & GK"
        },
        {
            "day": "Friday",
            "focus": "Sectional Speed Drill & Formula Revision",
            "duration": f"{daily_hours} Hours",
            "tasks": [
                "Rapid revision of all mathematical formulas and theorems.",
                "Take a 20-minute timed sectional test.",
                "Identify speed bottlenecks and question selection strategy."
            ],
            "tag": "Speed Drill"
        },
        {
            "day": "Saturday",
            "focus": "Full-Length Mock Test & Simulation",
            "duration": f"{daily_hours + 1} Hours",
            "tasks": [
                "Attempt a full-length SmartPrep Mock Test in strict exam environment.",
                "Do NOT pause or refer to notes during the test.",
                "Review immediate test analysis score and question explanations."
            ],
            "tag": "Mock Exam"
        },
        {
            "day": "Sunday",
            "focus": "In-Depth Mock Analysis & Weekly Reflection",
            "duration": f"{daily_hours} Hours",
            "tasks": [
                "Analyze every incorrect and unanswered question from Saturday's test.",
                "Categorize mistakes: Conceptual error, calculation slip, or time pressure.",
                "Plan learning targets for the upcoming week."
            ],
            "tag": "Analysis & Reset"
        }
    ]

    return {
        "plan_type": plan_type,
        "primary_subject": primary_subject,
        "secondary_subject": secondary_subject,
        "daily_hours": daily_hours,
        "avg_percentage": avg_percentage,
        "schedule": schedule
    }

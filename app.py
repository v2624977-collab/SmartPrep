import os
import base64
import tempfile
import functools
import secrets
import hashlib
from datetime import datetime, timedelta
from dotenv import load_dotenv
import pymysql
import pymysql.cursors

# Ensure .env is loaded from the project directory
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
load_dotenv(dotenv_path=env_path)

from flask import Flask, render_template, request, session, redirect, url_for, flash, g
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
from email_service import send_welcome_email, send_password_reset_email, send_result_email

from ai.analytics import analyze_student_performance
from ai.planner import generate_study_plan
from ai.prediction import predict_future_score

# ---------------- CREATE FLASK APP ----------------
app = Flask(__name__)
app.secret_key = "smartprep_secret_key"

# ---------------- MYSQL CONFIGURATION ----------------
app.config["MYSQL_HOST"] = Config.MYSQL_HOST
app.config["MYSQL_PORT"] = int(getattr(Config, "MYSQL_PORT", 3306))
app.config["MYSQL_USER"] = Config.MYSQL_USER
app.config["MYSQL_PASSWORD"] = Config.MYSQL_PASSWORD
app.config["MYSQL_DB"] = Config.MYSQL_DB
app.config["MYSQL_SSL_CA"] = getattr(Config, "MYSQL_SSL_CA", "")
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

# ---------------- AIVEN MYSQL SSL HELPER ----------------
def get_mysql_ssl_config():
    ca_value = app.config.get("MYSQL_SSL_CA", "")

    if not ca_value:
        return None

    ca_value = str(ca_value).strip()

    # If MYSQL_SSL_CA is a local certificate file path
    if os.path.isfile(ca_value):
        return {
            "ca": ca_value,
            "check_hostname": True
        }

    # If the environment variable contains the actual PEM certificate
    if "-----BEGIN CERTIFICATE-----" in ca_value:
        ca_data = ca_value
    else:
        # Otherwise treat it as Base64 encoded certificate
        try:
            ca_data = base64.b64decode(ca_value).decode("utf-8")
        except Exception:
            ca_data = ""

    if "-----BEGIN CERTIFICATE-----" not in ca_data:
        return None

    # Vercel/serverless environments allow temporary files
    ca_path = os.path.join(tempfile.gettempdir(), "aiven-ca.pem")

    with open(
        ca_path,
        "w",
        encoding="utf-8",
        newline="\n"
    ) as certificate_file:
        certificate_file.write(ca_data)

    return {
        "ca": ca_path,
        "check_hostname": True
    }

# ---------------- PURE PYTHON MYSQL WRAPPER ----------------
class MySQL:
    def __init__(self, flask_app=None):
        self.app = flask_app
        if flask_app is not None:
            self.init_app(flask_app)

    def init_app(self, flask_app):
        @flask_app.teardown_appcontext
        def close_db(exception=None):
            conn = getattr(g, '_mysql_conn', None)
            if conn is not None:
                try:
                    conn.close()
                except Exception:
                    pass

    @property
    def connection(self):
        if not hasattr(g, '_mysql_conn') or g._mysql_conn is None or not g._mysql_conn.open:
            connection_config = {
                "host": app.config.get("MYSQL_HOST", "localhost"),
                "port": int(app.config.get("MYSQL_PORT", 3306)),
                "user": app.config.get("MYSQL_USER", "root"),
                "password": app.config.get("MYSQL_PASSWORD", ""),
                "database": app.config.get("MYSQL_DB", "smartprep"),
                "cursorclass": pymysql.cursors.DictCursor,
                "autocommit": False,
                "charset": "utf8mb4",
                "connect_timeout": 15,
                "read_timeout": 30,
                "write_timeout": 30
            }

            ssl_config = get_mysql_ssl_config()

            if ssl_config:
                connection_config["ssl"] = ssl_config
            elif "aivencloud.com" in str(
                app.config.get("MYSQL_HOST", "")
            ).lower():
                raise RuntimeError(
                    "Aiven MySQL requires SSL. Please configure MYSQL_SSL_CA."
                )

            g._mysql_conn = pymysql.connect(**connection_config)
        return g._mysql_conn

# ---------------- INITIALIZE MYSQL ----------------
mysql = MySQL(app)


# ======================================================
# AUTHENTICATION DECORATORS
# ======================================================

def login_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if "student_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if "admin_id" not in session:
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return decorated_function


# ======================================================
# 1. HOME & PUBLIC ROUTES
# ======================================================

@app.route("/")
def home():
    return render_template("index.html")


# ======================================================
# 2. STUDENT AUTHENTICATION & PROFILE
# ======================================================

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        fullname = request.form.get("fullname", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        # Form validation
        if not fullname or not email or not password:
            return render_template("register.html", error="Please fill in all required fields.")

        if password != confirm_password:
            return render_template("register.html", error="Passwords do not match. Please try again.")

        if len(password) < 6:
            return render_template("register.html", error="Password must be at least 6 characters long.")

        hashed_password = generate_password_hash(password)

        try:
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT * FROM student WHERE email=%s", (email,))
            existing_user = cursor.fetchone()

            if existing_user:
                cursor.close()
                return render_template("register.html", error="Email is already registered. Please login or use another email.")

            cursor.execute(
                "INSERT INTO student(full_name, email, password) VALUES(%s, %s, %s)",
                (fullname, email, hashed_password)
            )
            mysql.connection.commit()
            student_id = cursor.lastrowid
            cursor.close()

            # Trigger welcome email asynchronously
            try:
                login_url = request.host_url.rstrip("/") + url_for("login")
                send_welcome_email(to_email=email, student_name=fullname, login_url=login_url)
            except Exception as email_err:
                print(f"[WELCOME EMAIL ERROR] {email_err}")

            session["student_id"] = student_id
            session["student_name"] = fullname
            session["student_email"] = email

            return redirect(url_for("dashboard"))
        except Exception as e:
            return render_template("register.html", error=f"Registration error: {str(e)}")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            return render_template("login.html", error="Please enter both email and password.")

        try:
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT * FROM student WHERE email=%s", (email,))
            user = cursor.fetchone()
            cursor.close()

            if user and check_password_hash(user["password"], password):
                session["student_id"] = user["student_id"]
                session["student_name"] = user["full_name"]
                session["student_email"] = user["email"]
                return redirect(url_for("dashboard"))
            else:
                return render_template("login.html", error="Invalid Email or Password. Please check your credentials.")
        except Exception as e:
            return render_template("login.html", error=f"Database error: {str(e)}")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("student_id", None)
    session.pop("student_name", None)
    session.pop("student_email", None)
    return redirect(url_for("login"))


@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()

        if not email:
            return render_template("forgot_password.html", error="Please enter your email address.")

        generic_message = "If an account exists for this email, a password reset link has been sent."

        try:
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT student_id, full_name, email FROM student WHERE email=%s", (email,))
            student = cursor.fetchone()

            if student:
                raw_token = secrets.token_urlsafe(32)
                token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
                expires_at = datetime.now() + timedelta(minutes=30)

                cursor.execute("""
                    INSERT INTO password_reset_token (student_id, token_hash, expires_at, used)
                    VALUES (%s, %s, %s, 0)
                """, (student["student_id"], token_hash, expires_at))
                mysql.connection.commit()

                # Dispatch reset email
                try:
                    reset_url = request.host_url.rstrip("/") + url_for("reset_password", token=raw_token)
                    send_password_reset_email(
                        to_email=student["email"],
                        student_name=student["full_name"],
                        reset_url=reset_url
                    )
                except Exception as email_err:
                    print(f"[RESET EMAIL ERROR] {email_err}")

            cursor.close()
            return render_template("forgot_password.html", success=generic_message)
        except Exception as e:
            return render_template("forgot_password.html", error=f"An error occurred: {str(e)}")

    return render_template("forgot_password.html")


@app.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    if not token:
        return render_template("reset_password.html", invalid_token=True)

    token_hash = hashlib.sha256(token.strip().encode()).hexdigest()

    try:
        cursor = mysql.connection.cursor()
        cursor.execute("""
            SELECT id, student_id, expires_at, used
            FROM password_reset_token
            WHERE token_hash=%s
        """, (token_hash,))
        reset_entry = cursor.fetchone()

        if not reset_entry or reset_entry["used"] or reset_entry["expires_at"] < datetime.now():
            cursor.close()
            return render_template("reset_password.html", invalid_token=True)

        if request.method == "POST":
            new_password = request.form.get("password", "")
            confirm_password = request.form.get("confirm_password", "")

            if not new_password or not confirm_password:
                cursor.close()
                return render_template("reset_password.html", error="Please fill in both password fields.")

            if new_password != confirm_password:
                cursor.close()
                return render_template("reset_password.html", error="Passwords do not match. Please try again.")

            if len(new_password) < 6:
                cursor.close()
                return render_template("reset_password.html", error="Password must be at least 6 characters long.")

            hashed_password = generate_password_hash(new_password)

            # Update student password
            cursor.execute("UPDATE student SET password=%s WHERE student_id=%s", (hashed_password, reset_entry["student_id"]))
            # Mark token as used
            cursor.execute("UPDATE password_reset_token SET used=1 WHERE id=%s", (reset_entry["id"],))
            mysql.connection.commit()
            cursor.close()

            return render_template("reset_password.html", success="Your password has been successfully reset! You can now login with your new password.")

        cursor.close()
        return render_template("reset_password.html")
    except Exception as e:
        return render_template("reset_password.html", error=f"An error occurred: {str(e)}")


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    student_id = session["student_id"]
    cursor = mysql.connection.cursor()

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        current_password = request.form.get("current_password", "")
        new_password = request.form.get("new_password", "")
        confirm_new_password = request.form.get("confirm_new_password", "")

        cursor.execute("SELECT * FROM student WHERE student_id=%s", (student_id,))
        student = cursor.fetchone()

        if not student:
            cursor.close()
            return redirect(url_for("login"))

        if not full_name:
            cursor.close()
            return render_template("profile.html", student=student, error="Full Name cannot be empty.")

        # Update name if changed
        if full_name != student["full_name"]:
            cursor.execute("UPDATE student SET full_name=%s WHERE student_id=%s", (full_name, student_id))
            mysql.connection.commit()
            session["student_name"] = full_name
            student["full_name"] = full_name

        # Update password if requested
        if new_password:
            if not current_password or not check_password_hash(student["password"], current_password):
                cursor.close()
                return render_template("profile.html", student=student, error="Current password is incorrect.")

            if new_password != confirm_new_password:
                cursor.close()
                return render_template("profile.html", student=student, error="New passwords do not match.")

            if len(new_password) < 6:
                cursor.close()
                return render_template("profile.html", student=student, error="New password must be at least 6 characters.")

            hashed_new = generate_password_hash(new_password)
            cursor.execute("UPDATE student SET password=%s WHERE student_id=%s", (hashed_new, student_id))
            mysql.connection.commit()

        cursor.close()
        return render_template("profile.html", student=student, success="Profile updated successfully!")

    # GET Request
    cursor.execute("SELECT * FROM student WHERE student_id=%s", (student_id,))
    student = cursor.fetchone()

    cursor.execute("SELECT COUNT(*) AS total_tests FROM result WHERE student_id=%s", (student_id,))
    test_count_res = cursor.fetchone()
    total_tests = test_count_res["total_tests"] if test_count_res else 0
    cursor.close()

    return render_template("profile.html", student=student, total_tests=total_tests, student_name=session["student_name"])


# ======================================================
# 3. STUDENT DASHBOARD & PROGRESS
# ======================================================

def get_quiz_difficulty_meta(quiz_name):
    if "Practice Quiz 1" in quiz_name:
        return {"level": "Easy", "badge_class": "pill-green", "color": "#10B981", "icon": "fa-seedling"}
    elif "Practice Quiz 2" in quiz_name:
        return {"level": "Easy to Moderate", "badge_class": "pill-cyan", "color": "#06B6D4", "icon": "fa-gauge"}
    elif "Practice Quiz 3" in quiz_name:
        return {"level": "Moderate", "badge_class": "pill-yellow", "color": "#F59E0B", "icon": "fa-bolt"}
    elif "Practice Quiz 4" in quiz_name:
        return {"level": "Moderate to Difficult", "badge_class": "pill-orange", "color": "#F97316", "icon": "fa-fire"}
    elif "Practice Quiz 5" in quiz_name:
        return {"level": "Difficult", "badge_class": "pill-red", "color": "#EF4444", "icon": "fa-brain"}
    return {"level": "Standard", "badge_class": "pill-blue", "color": "#38BDF8", "icon": "fa-pen-to-square"}


@app.route("/dashboard")
@login_required
def dashboard():
    student_id = session["student_id"]
    cursor = mysql.connection.cursor()

    # Get available exams with dynamic question count
    cursor.execute("""
        SELECT e.exam_id, e.exam_name, e.description,
               COALESCE(e.duration_minutes, 30) AS duration_minutes,
               COUNT(q.question_id) AS question_count
        FROM exam e
        LEFT JOIN question q ON e.exam_id = q.exam_id
        GROUP BY e.exam_id, e.exam_name, e.description, e.duration_minutes
        ORDER BY e.exam_id ASC
    """)
    all_exams = cursor.fetchall()

    # Separate primary competitive exams and practice quizzes
    primary_exams = [e for e in all_exams if "Practice Quiz" not in e["exam_name"]]
    all_practice_quizzes = [e for e in all_exams if "Practice Quiz" in e["exam_name"]]

    for q in all_practice_quizzes:
        meta = get_quiz_difficulty_meta(q["exam_name"])
        q["difficulty"] = meta["level"]
        q["badge_class"] = meta["badge_class"]
        q["color"] = meta["color"]
        q["icon"] = meta["icon"]

    # Match each primary exam with its respective 5 practice quizzes
    for pe in primary_exams:
        exam_name = pe["exam_name"]
        prefix = exam_name.split()[0]
        pe_quizzes = [q for q in all_practice_quizzes if q["exam_name"].startswith(exam_name) or q["exam_name"].startswith(prefix)]
        pe["practice_quizzes"] = pe_quizzes
        pe["first_quiz_id"] = pe_quizzes[0]["exam_id"] if pe_quizzes else pe["exam_id"]
        pe["total_practice_count"] = sum(q["question_count"] for q in pe_quizzes)

    # Legacy compatibility variable for TANCET
    tancet_practice_quizzes = [q for q in all_practice_quizzes if "TANCET" in q["exam_name"].upper()]

    # Get student test history for statistics and charts
    cursor.execute("""
        SELECT r.result_id, r.exam_id, e.exam_name, r.score,
               COALESCE(r.total_questions, (SELECT COUNT(*) FROM question WHERE question.exam_id = r.exam_id)) AS total_questions,
               COALESCE(r.percentage, ROUND((r.score / NULLIF((SELECT COUNT(*) FROM question WHERE question.exam_id = r.exam_id), 0)) * 100, 1)) AS percentage,
               DATE_FORMAT(r.test_date, '%%d-%%b-%%Y %%H:%%i') AS test_date
        FROM result r
        JOIN exam e ON r.exam_id = e.exam_id
        WHERE r.student_id = %s
        ORDER BY r.test_date DESC
    """, (student_id,))
    results = cursor.fetchall()
    cursor.close()

    # Performance Analytics for Dashboard
    analytics = analyze_student_performance(results)

    # Prepare chart data (Score history in chronological order)
    chart_labels = []
    chart_scores = []
    if results:
        for res in reversed(results[:10]):  # Last 10 tests
            chart_labels.append(f"{res['exam_name']} ({res['test_date'][:11]})")
            chart_scores.append(float(res["percentage"]))

    return render_template(
        "dashboard.html",
        exams=all_exams,
        primary_exams=primary_exams,
        all_practice_quizzes=all_practice_quizzes,
        tancet_practice_quizzes=tancet_practice_quizzes,
        results=results[:5],  # Recent 5 results
        total_results_count=len(results),
        analytics=analytics,
        chart_labels=chart_labels,
        chart_scores=chart_scores,
        student_name=session["student_name"]
    )


# ======================================================
# 4. EXAM DETAILS & MOCK TEST
# ======================================================

@app.route("/exam/<int:exam_id>")
@login_required
def exam_details(exam_id):
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT e.exam_id, e.exam_name, e.description,
               COALESCE(e.duration_minutes, 30) AS duration_minutes,
               COUNT(q.question_id) AS question_count
        FROM exam e
        LEFT JOIN question q ON e.exam_id = q.exam_id
        WHERE e.exam_id = %s
        GROUP BY e.exam_id, e.exam_name, e.description, e.duration_minutes
    """, (exam_id,))
    exam = cursor.fetchone()

    if not exam:
        cursor.close()
        return render_template("404.html", message="Exam not found."), 404

    # Determine base exam name and query associated practice quizzes
    exam_name = exam["exam_name"]
    if "Practice Quiz" in exam_name:
        base_name = exam_name.split(" Practice Quiz")[0].strip()
    else:
        base_name = exam_name.strip()

    prefix = base_name.split()[0]  # E.g., 'TANCET', 'GATE', 'TNPSC', 'SSC', 'CAT'

    cursor.execute("""
        SELECT e.exam_id, e.exam_name, e.description,
               COALESCE(e.duration_minutes, 30) AS duration_minutes,
               COUNT(q.question_id) AS question_count
        FROM exam e
        LEFT JOIN question q ON e.exam_id = q.exam_id
        WHERE (e.exam_name LIKE %s OR e.exam_name LIKE %s) AND e.exam_name LIKE '%%Practice Quiz%%'
        GROUP BY e.exam_id, e.exam_name, e.description, e.duration_minutes
        ORDER BY e.exam_id ASC
    """, (f"{base_name}%", f"{prefix}%"))
    practice_quizzes = cursor.fetchall()

    for pq in practice_quizzes:
        meta = get_quiz_difficulty_meta(pq["exam_name"])
        pq["difficulty"] = meta["level"]
        pq["badge_class"] = meta["badge_class"]
        pq["color"] = meta["color"]
        pq["icon"] = meta["icon"]

    cursor.close()

    total_practice_questions = sum(pq["question_count"] for pq in practice_quizzes) if practice_quizzes else exam["question_count"]

    return render_template(
        "exam_details.html",
        exam=exam,
        base_name=base_name,
        question_count=exam["question_count"],
        total_practice_questions=total_practice_questions,
        practice_quizzes=practice_quizzes,
        student_name=session["student_name"]
    )


@app.route("/test/<int:exam_id>")
@login_required
def start_exam(exam_id):
    cursor = mysql.connection.cursor()

    # Get exam details
    cursor.execute("""
        SELECT exam_id, exam_name, description, COALESCE(duration_minutes, 30) AS duration_minutes
        FROM exam WHERE exam_id=%s
    """, (exam_id,))
    exam = cursor.fetchone()

    # Get questions for this exam (WITHOUT exposing correct_answer)
    cursor.execute("""
        SELECT question_id, question_text, option_a, option_b, option_c, option_d
        FROM question
        WHERE exam_id=%s
        ORDER BY question_id ASC
    """, (exam_id,))
    questions = cursor.fetchall()
    cursor.close()

    if not exam:
        return render_template("404.html", message="Exam not found."), 404

    if not questions:
        return render_template(
            "exam_details.html",
            exam=exam,
            question_count=0,
            error="No questions are currently available for this exam. Please check back later.",
            student_name=session["student_name"]
        )

    return render_template(
        "test.html",
        exam=exam,
        questions=questions,
        total_questions=len(questions),
        duration_minutes=exam["duration_minutes"],
        student_name=session["student_name"]
    )


@app.route("/submit-test/<int:exam_id>", methods=["POST"])
@login_required
def submit_test(exam_id):
    student_id = session["student_id"]
    cursor = mysql.connection.cursor()

    # Get exam info
    cursor.execute("SELECT exam_id, exam_name FROM exam WHERE exam_id=%s", (exam_id,))
    exam = cursor.fetchone()

    # Get questions with correct answers
    cursor.execute("""
        SELECT question_id, question_text, option_a, option_b, option_c, option_d, correct_answer
        FROM question
        WHERE exam_id=%s
        ORDER BY question_id ASC
    """, (exam_id,))
    questions = cursor.fetchall()

    if not questions:
        cursor.close()
        return redirect(url_for("dashboard"))

    score = 0
    unanswered = 0
    total_questions = len(questions)
    answer_review = []

    for q in questions:
        qid = q["question_id"]
        selected_answer = request.form.get(f"question_{qid}")
        correct = q["correct_answer"]

        option_map = {
            "A": q["option_a"],
            "B": q["option_b"],
            "C": q["option_c"],
            "D": q["option_d"]
        }

        if not selected_answer:
            unanswered += 1
            status = "Unanswered"
            selected_display = "Not Answered"
        else:
            sel_letter = selected_answer.strip().upper()
            sel_text = option_map.get(sel_letter, "")
            selected_display = f"{sel_letter}) {sel_text}" if sel_text else sel_letter
            if sel_letter == correct.strip().upper():
                score += 1
                status = "Correct"
            else:
                status = "Wrong"

        corr_letter = correct.strip().upper()
        corr_text = option_map.get(corr_letter, "")
        correct_display = f"{corr_letter}) {corr_text}" if corr_text else corr_letter

        answer_review.append({
            "question_id": qid,
            "question_text": q["question_text"],
            "option_a": q["option_a"],
            "option_b": q["option_b"],
            "option_c": q["option_c"],
            "option_d": q["option_d"],
            "selected_answer": selected_answer,
            "selected_display": selected_display,
            "correct_answer": correct,
            "correct_display": correct_display,
            "status": status
        })

    wrong_answers = total_questions - score - unanswered
    percentage = round((score / total_questions) * 100, 2) if total_questions > 0 else 0.0

    # Save to database with total_questions & percentage
    cursor.execute("""
        INSERT INTO result(student_id, exam_id, score, total_questions, percentage)
        VALUES(%s, %s, %s, %s, %s)
    """, (student_id, exam_id, score, total_questions, percentage))
    mysql.connection.commit()
    cursor.close()

    # Trigger test result notification email asynchronously
    try:
        student_name = session.get("student_name", "Student")
        student_email = session.get("student_email")
        if not student_email:
            st_cursor = mysql.connection.cursor()
            st_cursor.execute("SELECT email, full_name FROM student WHERE student_id=%s", (student_id,))
            st_info = st_cursor.fetchone()
            st_cursor.close()
            if st_info:
                student_email = st_info["email"]
                student_name = st_info["full_name"]

        if student_email:
            test_date = datetime.now().strftime("%d %B %Y, %I:%M %p")
            results_url = request.host_url.rstrip("/") + url_for("results")
            send_result_email(
                to_email=student_email,
                student_name=student_name,
                exam_name=exam["exam_name"],
                score=score,
                total_questions=total_questions,
                percentage=percentage,
                correct=score,
                wrong=wrong_answers,
                unanswered=unanswered,
                test_date=test_date,
                results_url=results_url
            )
    except Exception as email_err:
        print(f"[RESULT EMAIL ERROR] {email_err}")

    return render_template(
        "result.html",
        exam=exam,
        score=score,
        total_questions=total_questions,
        percentage=percentage,
        correct_answers=score,
        wrong_answers=wrong_answers,
        unanswered=unanswered,
        answer_review=answer_review,
        exam_id=exam_id,
        student_name=session["student_name"]
    )


# ======================================================
# 5. RESULT HISTORY
# ======================================================

@app.route("/results")
@login_required
def results():
    student_id = session["student_id"]
    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT r.result_id, e.exam_name, r.score,
               COALESCE(r.total_questions, (SELECT COUNT(*) FROM question WHERE question.exam_id = r.exam_id)) AS total_questions,
               COALESCE(r.percentage, ROUND((r.score / NULLIF((SELECT COUNT(*) FROM question WHERE question.exam_id = r.exam_id), 0)) * 100, 1)) AS percentage,
               DATE_FORMAT(r.test_date, '%%d-%%b-%%Y %%H:%%i') AS formatted_date
        FROM result r
        JOIN exam e ON r.exam_id = e.exam_id
        WHERE r.student_id = %s
        ORDER BY r.test_date DESC
    """, (student_id,))
    results_list = cursor.fetchall()
    cursor.close()

    return render_template(
        "results.html",
        results=results_list,
        student_name=session["student_name"]
    )


# ======================================================
# 6. AI PERFORMANCE ANALYSIS
# ======================================================

@app.route("/performance")
@login_required
def performance():
    student_id = session["student_id"]
    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT r.result_id, r.exam_id, e.exam_name, r.score,
               COALESCE(r.total_questions, (SELECT COUNT(*) FROM question WHERE question.exam_id = r.exam_id)) AS total_questions,
               COALESCE(r.percentage, ROUND((r.score / NULLIF((SELECT COUNT(*) FROM question WHERE question.exam_id = r.exam_id), 0)) * 100, 1)) AS percentage,
               DATE_FORMAT(r.test_date, '%%d-%%b-%%Y') AS test_date
        FROM result r
        JOIN exam e ON r.exam_id = e.exam_id
        WHERE r.student_id = %s
        ORDER BY r.test_date DESC
    """, (student_id,))
    results_data = cursor.fetchall()
    cursor.close()

    analytics = analyze_student_performance(results_data)

    return render_template(
        "performance.html",
        analytics=analytics,
        student_name=session["student_name"]
    )


# ======================================================
# 7. PERSONALIZED STUDY PLANNER
# ======================================================

@app.route("/study-planner")
@login_required
def study_planner():
    student_id = session["student_id"]
    target_exam = request.args.get("exam", None)

    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT r.result_id, r.exam_id, e.exam_name, r.score,
               COALESCE(r.total_questions, (SELECT COUNT(*) FROM question WHERE question.exam_id = r.exam_id)) AS total_questions,
               COALESCE(r.percentage, ROUND((r.score / NULLIF((SELECT COUNT(*) FROM question WHERE question.exam_id = r.exam_id), 0)) * 100, 1)) AS percentage,
               DATE_FORMAT(r.test_date, '%%d-%%b-%%Y') AS test_date
        FROM result r
        JOIN exam e ON r.exam_id = e.exam_id
        WHERE r.student_id = %s
        ORDER BY r.test_date DESC
    """, (student_id,))
    results_data = cursor.fetchall()

    cursor.execute("SELECT exam_id, exam_name FROM exam ORDER BY exam_name ASC")
    all_exams = cursor.fetchall()
    cursor.close()

    analytics = analyze_student_performance(results_data)
    plan = generate_study_plan(analytics, target_exam_name=target_exam)

    return render_template(
        "study_planner.html",
        plan=plan,
        all_exams=all_exams,
        selected_exam=target_exam,
        student_name=session["student_name"]
    )


# ======================================================
# 8. ML SCORE PREDICTION
# ======================================================

@app.route("/predict-score")
@login_required
def predict_score():
    student_id = session["student_id"]
    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT r.result_id, r.exam_id, e.exam_name, r.score,
               COALESCE(r.total_questions, (SELECT COUNT(*) FROM question WHERE question.exam_id = r.exam_id)) AS total_questions,
               COALESCE(r.percentage, ROUND((r.score / NULLIF((SELECT COUNT(*) FROM question WHERE question.exam_id = r.exam_id), 0)) * 100, 1)) AS percentage,
               DATE_FORMAT(r.test_date, '%%d-%%b-%%Y') AS test_date
        FROM result r
        JOIN exam e ON r.exam_id = e.exam_id
        WHERE r.student_id = %s
        ORDER BY r.test_date DESC
    """, (student_id,))
    results_data = cursor.fetchall()
    cursor.close()

    prediction = predict_future_score(results_data)

    return render_template(
        "predict_score.html",
        prediction=prediction,
        student_name=session["student_name"]
    )


# ======================================================
# 9. ADMIN MODULE
# ======================================================

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM admin WHERE username=%s", (username,))
        admin_user = cursor.fetchone()
        cursor.close()

        if admin_user and check_password_hash(admin_user["password"], password):
            session["admin_id"] = admin_user["admin_id"]
            session["admin_username"] = admin_user["username"]
            return redirect(url_for("admin_dashboard"))
        else:
            return render_template("admin/login.html", error="Invalid Admin credentials. Access denied.")

    return render_template("admin/login.html")


@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_id", None)
    session.pop("admin_username", None)
    return redirect(url_for("admin_login"))


@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    cursor = mysql.connection.cursor()

    cursor.execute("SELECT COUNT(*) AS count FROM student")
    total_students = cursor.fetchone()["count"]

    cursor.execute("SELECT COUNT(*) AS count FROM exam")
    total_exams = cursor.fetchone()["count"]

    cursor.execute("SELECT COUNT(*) AS count FROM question")
    total_questions = cursor.fetchone()["count"]

    cursor.execute("SELECT COUNT(*) AS count FROM result")
    total_tests = cursor.fetchone()["count"]

    # Recent Results
    cursor.execute("""
        SELECT r.result_id, s.full_name, e.exam_name, r.score,
               COALESCE(r.total_questions, (SELECT COUNT(*) FROM question WHERE question.exam_id = r.exam_id)) AS total_questions,
               COALESCE(r.percentage, ROUND((r.score / NULLIF((SELECT COUNT(*) FROM question WHERE question.exam_id = r.exam_id), 0)) * 100, 1)) AS percentage,
               DATE_FORMAT(r.test_date, '%d-%b-%Y %H:%i') AS test_date
        FROM result r
        JOIN student s ON r.student_id = s.student_id
        JOIN exam e ON r.exam_id = e.exam_id
        ORDER BY r.test_date DESC
        LIMIT 6
    """)
    recent_results = cursor.fetchall()
    cursor.close()

    for r in recent_results:
        if hasattr(r.get("test_date"), "strftime"):
            r["test_date"] = r["test_date"].strftime("%d-%b-%Y %H:%M")

    return render_template(
        "admin/dashboard.html",
        total_students=total_students,
        total_exams=total_exams,
        total_questions=total_questions,
        total_tests=total_tests,
        recent_results=recent_results,
        admin_username=session["admin_username"]
    )


# --- ADMIN STUDENTS ---
@app.route("/admin/students")
@admin_required
def admin_students():
    search = request.args.get("q", "").strip()
    cursor = mysql.connection.cursor()

    if search:
        cursor.execute("""
            SELECT s.student_id, s.full_name, s.email,
                   DATE_FORMAT(s.created_at, '%%d-%%b-%%Y') AS joined_date,
                   (SELECT COUNT(*) FROM result WHERE result.student_id = s.student_id) AS tests_taken
            FROM student s
            WHERE s.full_name LIKE %s OR s.email LIKE %s
            ORDER BY s.student_id DESC
        """, (f"%{search}%", f"%{search}%"))
    else:
        cursor.execute("""
            SELECT s.student_id, s.full_name, s.email,
                   DATE_FORMAT(s.created_at, '%d-%b-%Y') AS joined_date,
                   (SELECT COUNT(*) FROM result WHERE result.student_id = s.student_id) AS tests_taken
            FROM student s
            ORDER BY s.student_id DESC
        """)

    students = cursor.fetchall()
    cursor.close()

    for s in students:
        if hasattr(s.get("joined_date"), "strftime"):
            s["joined_date"] = s["joined_date"].strftime("%d-%b-%Y")

    return render_template(
        "admin/students.html",
        students=students,
        search=search,
        admin_username=session["admin_username"]
    )


# --- ADMIN EXAMS ---
@app.route("/admin/exams")
@admin_required
def admin_exams():
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT e.exam_id, e.exam_name, e.description,
               COALESCE(e.duration_minutes, 30) AS duration_minutes,
               COUNT(q.question_id) AS question_count
        FROM exam e
        LEFT JOIN question q ON e.exam_id = q.exam_id
        GROUP BY e.exam_id, e.exam_name, e.description, e.duration_minutes
        ORDER BY e.exam_id ASC
    """)
    exams = cursor.fetchall()
    cursor.close()

    return render_template("admin/exams.html", exams=exams, admin_username=session["admin_username"])


@app.route("/admin/exams/add", methods=["GET", "POST"])
@admin_required
def admin_add_exam():
    if request.method == "POST":
        exam_name = request.form.get("exam_name", "").strip()
        description = request.form.get("description", "").strip()
        duration = request.form.get("duration_minutes", 30)

        if not exam_name:
            return render_template("admin/exam_form.html", action="Add", error="Exam name is required.")

        try:
            duration = int(duration)
        except ValueError:
            duration = 30

        cursor = mysql.connection.cursor()
        cursor.execute(
            "INSERT INTO exam(exam_name, description, duration_minutes) VALUES(%s, %s, %s)",
            (exam_name, description, duration)
        )
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for("admin_exams"))

    return render_template("admin/exam_form.html", action="Add", exam={}, admin_username=session["admin_username"])


@app.route("/admin/exams/edit/<int:exam_id>", methods=["GET", "POST"])
@admin_required
def admin_edit_exam(exam_id):
    cursor = mysql.connection.cursor()

    if request.method == "POST":
        exam_name = request.form.get("exam_name", "").strip()
        description = request.form.get("description", "").strip()
        duration = request.form.get("duration_minutes", 30)

        if not exam_name:
            cursor.close()
            return render_template("admin/exam_form.html", action="Edit", exam={"exam_id": exam_id, "exam_name": exam_name, "description": description, "duration_minutes": duration}, error="Exam name cannot be empty.")

        try:
            duration = int(duration)
        except ValueError:
            duration = 30

        cursor.execute(
            "UPDATE exam SET exam_name=%s, description=%s, duration_minutes=%s WHERE exam_id=%s",
            (exam_name, description, duration, exam_id)
        )
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for("admin_exams"))

    cursor.execute("SELECT * FROM exam WHERE exam_id=%s", (exam_id,))
    exam = cursor.fetchone()
    cursor.close()

    if not exam:
        return redirect(url_for("admin_exams"))

    return render_template("admin/exam_form.html", action="Edit", exam=exam, admin_username=session["admin_username"])


@app.route("/admin/exams/delete/<int:exam_id>", methods=["POST"])
@admin_required
def admin_delete_exam(exam_id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM exam WHERE exam_id=%s", (exam_id,))
    mysql.connection.commit()
    cursor.close()
    return redirect(url_for("admin_exams"))


# --- ADMIN QUESTIONS ---
@app.route("/admin/questions")
@admin_required
def admin_questions():
    exam_filter = request.args.get("exam_id", "")
    cursor = mysql.connection.cursor()

    cursor.execute("SELECT exam_id, exam_name FROM exam ORDER BY exam_name ASC")
    exams = cursor.fetchall()

    if exam_filter:
        cursor.execute("""
            SELECT q.question_id, q.exam_id, e.exam_name, q.question_text,
                   q.option_a, q.option_b, q.option_c, q.option_d, q.correct_answer
            FROM question q
            JOIN exam e ON q.exam_id = e.exam_id
            WHERE q.exam_id=%s
            ORDER BY q.question_id ASC
        """, (exam_filter,))
    else:
        cursor.execute("""
            SELECT q.question_id, q.exam_id, e.exam_name, q.question_text,
                   q.option_a, q.option_b, q.option_c, q.option_d, q.correct_answer
            FROM question q
            JOIN exam e ON q.exam_id = e.exam_id
            ORDER BY q.exam_id ASC, q.question_id ASC
        """)

    questions = cursor.fetchall()
    cursor.close()

    return render_template(
        "admin/questions.html",
        questions=questions,
        exams=exams,
        selected_exam=exam_filter,
        admin_username=session["admin_username"]
    )


@app.route("/admin/questions/add", methods=["GET", "POST"])
@admin_required
def admin_add_question():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT exam_id, exam_name FROM exam ORDER BY exam_name ASC")
    exams = cursor.fetchall()

    if request.method == "POST":
        exam_id = request.form.get("exam_id")
        question_text = request.form.get("question_text", "").strip()
        option_a = request.form.get("option_a", "").strip()
        option_b = request.form.get("option_b", "").strip()
        option_c = request.form.get("option_c", "").strip()
        option_d = request.form.get("option_d", "").strip()
        correct_answer = request.form.get("correct_answer", "").strip().upper()

        if not exam_id or not question_text or not option_a or not option_b or not option_c or not option_d or not correct_answer:
            cursor.close()
            return render_template("admin/question_form.html", action="Add", exams=exams, question=request.form, error="All question fields are required.")

        cursor.execute("""
            INSERT INTO question (exam_id, question_text, option_a, option_b, option_c, option_d, correct_answer)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (exam_id, question_text, option_a, option_b, option_c, option_d, correct_answer))
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for("admin_questions", exam_id=exam_id))

    cursor.close()
    return render_template("admin/question_form.html", action="Add", exams=exams, question={}, admin_username=session["admin_username"])


@app.route("/admin/questions/edit/<int:question_id>", methods=["GET", "POST"])
@admin_required
def admin_edit_question(question_id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT exam_id, exam_name FROM exam ORDER BY exam_name ASC")
    exams = cursor.fetchall()

    if request.method == "POST":
        exam_id = request.form.get("exam_id")
        question_text = request.form.get("question_text", "").strip()
        option_a = request.form.get("option_a", "").strip()
        option_b = request.form.get("option_b", "").strip()
        option_c = request.form.get("option_c", "").strip()
        option_d = request.form.get("option_d", "").strip()
        correct_answer = request.form.get("correct_answer", "").strip().upper()

        if not exam_id or not question_text or not option_a or not option_b or not option_c or not option_d or not correct_answer:
            cursor.close()
            return render_template("admin/question_form.html", action="Edit", exams=exams, question=request.form, error="All question fields are required.")

        cursor.execute("""
            UPDATE question
            SET exam_id=%s, question_text=%s, option_a=%s, option_b=%s, option_c=%s, option_d=%s, correct_answer=%s
            WHERE question_id=%s
        """, (exam_id, question_text, option_a, option_b, option_c, option_d, correct_answer, question_id))
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for("admin_questions", exam_id=exam_id))

    cursor.execute("SELECT * FROM question WHERE question_id=%s", (question_id,))
    question = cursor.fetchone()
    cursor.close()

    if not question:
        return redirect(url_for("admin_questions"))

    return render_template("admin/question_form.html", action="Edit", exams=exams, question=question, admin_username=session["admin_username"])


@app.route("/admin/questions/delete/<int:question_id>", methods=["POST"])
@admin_required
def admin_delete_question(question_id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT exam_id FROM question WHERE question_id=%s", (question_id,))
    q = cursor.fetchone()
    exam_id = q["exam_id"] if q else None

    cursor.execute("DELETE FROM question WHERE question_id=%s", (question_id,))
    mysql.connection.commit()
    cursor.close()

    if exam_id:
        return redirect(url_for("admin_questions", exam_id=exam_id))
    return redirect(url_for("admin_questions"))


# --- ADMIN RESULTS ---
@app.route("/admin/results")
@admin_required
def admin_results():
    search = request.args.get("q", "").strip()
    cursor = mysql.connection.cursor()

    query = """
        SELECT r.result_id, s.full_name, s.email, e.exam_name, r.score,
               COALESCE(r.total_questions, (SELECT COUNT(*) FROM question WHERE question.exam_id = r.exam_id)) AS total_questions,
               COALESCE(r.percentage, ROUND((r.score / NULLIF((SELECT COUNT(*) FROM question WHERE question.exam_id = r.exam_id), 0)) * 100, 1)) AS percentage,
               DATE_FORMAT(r.test_date, '%%d-%%b-%%Y %%H:%%i') AS test_date
        FROM result r
        JOIN student s ON r.student_id = s.student_id
        JOIN exam e ON r.exam_id = e.exam_id
    """
    params = ()

    if search:
        query += " WHERE s.full_name LIKE %s OR s.email LIKE %s OR e.exam_name LIKE %s"
        params = (f"%{search}%", f"%{search}%", f"%{search}%")

    query += " ORDER BY r.test_date DESC"

    cursor.execute(query, params)
    all_results = cursor.fetchall()
    cursor.close()

    return render_template(
        "admin/results.html",
        results=all_results,
        search=search,
        admin_username=session["admin_username"]
    )


# ======================================================
# 10. ERROR HANDLERS
# ======================================================

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html", message="The requested page could not be found."), 404


@app.errorhandler(500)
def server_error(e):
    return render_template("500.html", message="An unexpected internal server error occurred."), 500


# ======================================================
# RUN APPLICATION
# ======================================================

if __name__ == "__main__":
    app.run(debug=True)
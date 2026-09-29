import unittest
from app import app
import pymysql
from config import Config

class SmartPrepSystemTests(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_01_home_page(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"SmartPrep", response.data)
        self.assertIn(b"Prepare", response.data)

    def test_02_registration_validation(self):
        # Mismatched passwords
        res = self.client.post("/register", data={
            "fullname": "Test User",
            "email": "testvalidation@example.com",
            "password": "password123",
            "confirm_password": "password456"
        })
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Passwords do not match", res.data)

    def test_03_login_invalid_credentials(self):
        res = self.client.post("/login", data={
            "email": "nonexistent_email_123@example.com",
            "password": "wrongpassword"
        })
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Invalid Email or Password", res.data)

    def test_04_all_exams_database_integrity(self):
        conn = pymysql.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB
        )
        cur = conn.cursor(pymysql.cursors.DictCursor)

        # Verify all 5 primary exams exist
        cur.execute("SELECT exam_id, exam_name FROM exam WHERE exam_id <= 5 ORDER BY exam_id")
        primary_exams = cur.fetchall()
        self.assertEqual(len(primary_exams), 5)
        exam_names = [e["exam_name"] for e in primary_exams]
        self.assertIn("TANCET", exam_names)
        self.assertIn("GATE", exam_names)
        self.assertIn("TNPSC Group 4", exam_names)
        self.assertIn("SSC CGL", exam_names)
        self.assertIn("CAT", exam_names)

        # Verify exactly 25 practice quizzes (5 per exam) with 20 questions each
        expected_quiz_ranges = {
            "TANCET": (6, 10),
            "GATE": (11, 15),
            "TNPSC Group 4": (16, 20),
            "SSC CGL": (21, 25),
            "CAT": (26, 30)
        }

        total_practice_questions = 0
        for exam_key, (start_id, end_id) in expected_quiz_ranges.items():
            for quiz_id in range(start_id, end_id + 1):
                cur.execute("SELECT exam_id, exam_name FROM exam WHERE exam_id=%s", (quiz_id,))
                quiz = cur.fetchone()
                self.assertIsNotNone(quiz, f"Exam ID {quiz_id} should exist")
                self.assertIn("Practice Quiz", quiz["exam_name"])

                # Check question count
                cur.execute("SELECT question_id, question_text, option_a, option_b, option_c, option_d, correct_answer FROM question WHERE exam_id=%s", (quiz_id,))
                questions = cur.fetchall()
                self.assertEqual(len(questions), 20, f"Quiz ID {quiz_id} ({quiz['exam_name']}) must have exactly 20 questions")
                total_practice_questions += len(questions)

                # Check options and correct_answer validity
                for q in questions:
                    self.assertTrue(q["question_text"], "Question text cannot be empty")
                    self.assertTrue(q["option_a"], "Option A cannot be empty")
                    self.assertTrue(q["option_b"], "Option B cannot be empty")
                    self.assertTrue(q["option_c"], "Option C cannot be empty")
                    self.assertTrue(q["option_d"], "Option D cannot be empty")
                    self.assertIn(q["correct_answer"], ["A", "B", "C", "D"], f"Correct answer must be A/B/C/D in QID {q['question_id']}")

        self.assertEqual(total_practice_questions, 500, "25 Practice Quizzes * 20 questions must equal 500 questions")

        # Total questions in database should be 525 (500 practice + 25 baseline)
        cur.execute("SELECT COUNT(*) AS total_q FROM question")
        total_q = cur.fetchone()["total_q"]
        self.assertEqual(total_q, 525)

        conn.close()

    def test_05_student_flow_all_exams(self):
        # Register new student
        email = "multiexamstudent@test.com"
        self.client.post("/register", data={
            "fullname": "Multi Exam Student",
            "email": email,
            "password": "securepassword123",
            "confirm_password": "securepassword123"
        }, follow_redirects=True)

        # Login
        res_login = self.client.post("/login", data={
            "email": email,
            "password": "securepassword123"
        }, follow_redirects=True)
        self.assertEqual(res_login.status_code, 200)

        # Dashboard: Check presence of all 5 primary exams and Practice Quiz Hub
        res_dash = self.client.get("/dashboard")
        self.assertEqual(res_dash.status_code, 200)
        self.assertIn(b"TANCET", res_dash.data)
        self.assertIn(b"GATE", res_dash.data)
        self.assertIn(b"TNPSC Group 4", res_dash.data)
        self.assertIn(b"SSC CGL", res_dash.data)
        self.assertIn(b"CAT", res_dash.data)
        self.assertIn(b"Practice Quiz Hub", res_dash.data)

        # Test Exam Details and Quiz Loading for each of the 5 Exams
        exam_test_configs = [
            (1, "TANCET", 6, "TANCET Practice Quiz 1"),
            (2, "GATE", 11, "GATE Practice Quiz 1"),
            (3, "TNPSC Group 4", 16, "TNPSC Group 4 Practice Quiz 1"),
            (4, "SSC CGL", 21, "SSC CGL Practice Quiz 1"),
            (5, "CAT", 26, "CAT Practice Quiz 1")
        ]

        conn = pymysql.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB
        )
        cur = conn.cursor(pymysql.cursors.DictCursor)

        for exam_id, exam_name, first_quiz_id, first_quiz_name in exam_test_configs:
            # 1. Exam Details page
            res_detail = self.client.get(f"/exam/{exam_id}")
            self.assertEqual(res_detail.status_code, 200)
            self.assertIn(exam_name.encode("utf-8"), res_detail.data)
            self.assertIn(b"Practice Series Structure", res_detail.data)
            self.assertIn(b"Practice Quiz 1", res_detail.data)
            self.assertIn(b"Practice Quiz 5", res_detail.data)
            self.assertIn(b"Easy", res_detail.data)
            self.assertIn(b"Difficult", res_detail.data)

            # 2. Test execution page for Quiz 1 of this exam
            res_quiz = self.client.get(f"/test/{first_quiz_id}")
            self.assertEqual(res_quiz.status_code, 200)
            self.assertIn(first_quiz_name.encode("utf-8"), res_quiz.data)
            self.assertIn(b"Question Palette", res_quiz.data)
            self.assertIn(b"20 Questions", res_quiz.data)

            # 3. Submit quiz with 19 correct answers, 1 unanswered
            cur.execute("SELECT question_id, correct_answer FROM question WHERE exam_id=%s ORDER BY question_id ASC", (first_quiz_id,))
            q_rows = cur.fetchall()
            self.assertEqual(len(q_rows), 20)

            submission_data = {}
            for i, qr in enumerate(q_rows):
                if i < 19:
                    submission_data[f"question_{qr['question_id']}"] = qr["correct_answer"]

            res_submit = self.client.post(f"/submit-test/{first_quiz_id}", data=submission_data)
            self.assertEqual(res_submit.status_code, 200)
            self.assertIn(b"Assessment Completed", res_submit.data)
            self.assertIn(first_quiz_name.encode("utf-8"), res_submit.data)
            self.assertIn(b"19", res_submit.data)  # Score
            self.assertIn(b"95.0%", res_submit.data)  # Percentage (19/20 = 95%)

        conn.close()

        # Check Result History contains all 5 test attempts
        res_history = self.client.get("/results")
        self.assertEqual(res_history.status_code, 200)
        self.assertIn(b"TANCET Practice Quiz 1", res_history.data)
        self.assertIn(b"GATE Practice Quiz 1", res_history.data)
        self.assertIn(b"TNPSC Group 4 Practice Quiz 1", res_history.data)
        self.assertIn(b"SSC CGL Practice Quiz 1", res_history.data)
        self.assertIn(b"CAT Practice Quiz 1", res_history.data)

        # AI Performance Analysis
        res_perf = self.client.get("/performance")
        self.assertEqual(res_perf.status_code, 200)
        self.assertIn(b"AI Academic Performance Analytics", res_perf.data)

        # Study Planner
        res_plan = self.client.get("/study-planner")
        self.assertEqual(res_plan.status_code, 200)
        self.assertIn(b"Personalized Weekly Study Plan", res_plan.data)

        # Score Prediction
        res_pred = self.client.get("/predict-score")
        self.assertEqual(res_pred.status_code, 200)
        self.assertIn(b"Score Prediction", res_pred.data)

        # Logout
        res_logout = self.client.get("/logout", follow_redirects=True)
        self.assertEqual(res_logout.status_code, 200)

    def test_06_admin_flow_all_exams(self):
        # Admin Login
        res_admin_login = self.client.post("/admin/login", data={
            "username": "admin",
            "password": "admin123"
        }, follow_redirects=True)
        self.assertEqual(res_admin_login.status_code, 200)

        # Admin Exams: Must show all 30 exams
        res_exams = self.client.get("/admin/exams")
        self.assertEqual(res_exams.status_code, 200)
        self.assertIn(b"GATE Practice Quiz 1", res_exams.data)
        self.assertIn(b"TNPSC Group 4 Practice Quiz 1", res_exams.data)
        self.assertIn(b"SSC CGL Practice Quiz 1", res_exams.data)
        self.assertIn(b"CAT Practice Quiz 1", res_exams.data)
        self.assertIn(b"TANCET Practice Quiz 1", res_exams.data)

        # Admin Questions: Filter by GATE Practice Quiz 1 (exam_id=11)
        res_q_gate = self.client.get("/admin/questions?exam_id=11")
        self.assertEqual(res_q_gate.status_code, 200)
        self.assertIn(b"GATE Practice Quiz 1", res_q_gate.data)

        # Admin Questions: Filter by CAT Practice Quiz 5 (exam_id=30)
        res_q_cat = self.client.get("/admin/questions?exam_id=30")
        self.assertEqual(res_q_cat.status_code, 200)
        self.assertIn(b"CAT Practice Quiz 5", res_q_cat.data)

        # Admin Results
        res_results = self.client.get("/admin/results")
        self.assertEqual(res_results.status_code, 200)
        self.assertIn(b"Master Results", res_results.data)

        # Admin Logout
        res_admin_logout = self.client.get("/admin/logout", follow_redirects=True)
        self.assertEqual(res_admin_logout.status_code, 200)

    def test_07_student_auth_isolated_from_mysql_password(self):
        # 1. Register a student with a distinct custom password
        email = "unique_student_auth@test.com"
        reg_password = "StudentUniquePassword@2026"
        self.client.post("/register", data={
            "fullname": "Unique Auth Student",
            "email": email,
            "password": reg_password,
            "confirm_password": reg_password
        }, follow_redirects=True)

        self.client.get("/logout")

        # 2. Login with registered password must SUCCEED
        res_valid = self.client.post("/login", data={
            "email": email,
            "password": reg_password
        }, follow_redirects=True)
        self.assertEqual(res_valid.status_code, 200)
        self.assertIn(b"Unique Auth Student", res_valid.data)
        self.assertIn(b"Competitive Exam Hub", res_valid.data)

        self.client.get("/logout")

        # 3. Login with MySQL Config password must FAIL and be REJECTED
        res_mysql_pw = self.client.post("/login", data={
            "email": email,
            "password": Config.MYSQL_PASSWORD
        })
        self.assertEqual(res_mysql_pw.status_code, 200)
        self.assertIn(b"Invalid Email or Password", res_mysql_pw.data)

        # 4. Login with random invalid password must FAIL
        res_wrong = self.client.post("/login", data={
            "email": email,
            "password": "wrongpassword123"
        })
        self.assertEqual(res_wrong.status_code, 200)
        self.assertIn(b"Invalid Email or Password", res_wrong.data)

    def test_08_result_review_full_option_text(self):
        # 1. Login
        email = "unique_student_auth@test.com"
        reg_password = "StudentUniquePassword@2026"
        self.client.post("/login", data={
            "email": email,
            "password": reg_password
        }, follow_redirects=True)

        # 2. Test TNPSC Quiz 1 (exam_id=16)
        # Question 1 (QID 226): Author of Tirukkural -> Option A: Thiruvalluvar
        # Question 2 (QID 227): Red planet -> Option B: Mars (we answer with wrong option A: Venus)
        # Question 3 (QID 228): HCF of 24 and 36 -> Option C: 12 (we leave unanswered)
        conn = pymysql.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB
        )
        cur = conn.cursor(pymysql.cursors.DictCursor)
        cur.execute("SELECT question_id, question_text, option_a, option_b, option_c, option_d, correct_answer FROM question WHERE exam_id=16 ORDER BY question_id ASC")
        questions = cur.fetchall()
        conn.close()

        q1 = questions[0]  # Correct: A (Thiruvalluvar)
        q2 = questions[1]  # Correct: B (Mars), option_a is Venus
        q3 = questions[2]  # Correct: C (12)

        submission_data = {
            f"question_{q1['question_id']}": "A",  # Correct
            f"question_{q2['question_id']}": "A"   # Wrong (Venus instead of Mars)
            # q3 left unanswered
        }

        res = self.client.post("/submit-test/16", data=submission_data)
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")

        # 3. Verify Q1 review: Correct Answer: A) Thiruvalluvar, Your Response: A) Thiruvalluvar
        self.assertIn("A) Thiruvalluvar", html)
        self.assertIn("Correct (+1 Mark)", html)

        # 4. Verify Q2 review: Your Response: A) Venus, Correct Answer: B) Mars
        self.assertIn("A) Venus", html)
        self.assertIn("B) Mars", html)
        self.assertIn("Wrong", html)

        # 5. Verify Q3 review: Your Response: Not Answered, Correct Answer: C) 12
        self.assertIn("Not Answered", html)
        self.assertIn("C) 12", html)
        self.assertIn("Unanswered", html)

    def test_09_welcome_email_and_forgot_password(self):
        # 1. Register student
        email = "recoverystudent@test.com"
        reg_password = "InitialPassword123"
        res_reg = self.client.post("/register", data={
            "fullname": "Recovery Student",
            "email": email,
            "password": reg_password,
            "confirm_password": reg_password
        }, follow_redirects=True)
        self.assertEqual(res_reg.status_code, 200)

        # 2. Forgot Password GET
        res_fp_get = self.client.get("/forgot-password")
        self.assertEqual(res_fp_get.status_code, 200)
        self.assertIn(b"Password Recovery", res_fp_get.data)

        # 3. Forgot Password POST with non-existent email -> Generic Success message
        res_fp_nonexist = self.client.post("/forgot-password", data={
            "email": "does_not_exist_user_999@test.com"
        })
        self.assertEqual(res_fp_nonexist.status_code, 200)
        self.assertIn(b"If an account exists for this email, a password reset link has been sent.", res_fp_nonexist.data)

        # 4. Forgot Password POST with existing email -> Same Generic Success message & DB token created
        res_fp_exist = self.client.post("/forgot-password", data={
            "email": email
        })
        self.assertEqual(res_fp_exist.status_code, 200)
        self.assertIn(b"If an account exists for this email, a password reset link has been sent.", res_fp_exist.data)

        # Verify token in database
        conn = pymysql.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB
        )
        cur = conn.cursor(pymysql.cursors.DictCursor)
        cur.execute("""
            SELECT p.id, p.token_hash, p.expires_at, p.used
            FROM password_reset_token p
            JOIN student s ON p.student_id = s.student_id
            WHERE s.email = %s
            ORDER BY p.id DESC LIMIT 1
        """, (email,))
        token_entry = cur.fetchone()
        conn.close()

        self.assertIsNotNone(token_entry)
        self.assertEqual(token_entry["used"], 0)
        self.assertTrue(len(token_entry["token_hash"]) == 64)

    def test_10_password_reset_token_validation_and_update(self):
        email = "tokenstudent@test.com"
        old_password = "OldPassword123"
        new_password = "NewPassword456"

        self.client.post("/register", data={
            "fullname": "Token Student",
            "email": email,
            "password": old_password,
            "confirm_password": old_password
        }, follow_redirects=True)
        self.client.get("/logout")

        # Request reset
        self.client.post("/forgot-password", data={"email": email})

        # Fetch student and create known test token
        import secrets
        import hashlib
        from datetime import datetime, timedelta

        raw_test_token = secrets.token_urlsafe(32)
        test_hash = hashlib.sha256(raw_test_token.encode()).hexdigest()
        expires_at = datetime.now() + timedelta(minutes=30)

        conn = pymysql.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB
        )
        cur = conn.cursor(pymysql.cursors.DictCursor)
        cur.execute("SELECT student_id FROM student WHERE email=%s", (email,))
        student = cur.fetchone()
        cur.execute("""
            INSERT INTO password_reset_token (student_id, token_hash, expires_at, used)
            VALUES (%s, %s, %s, 0)
        """, (student["student_id"], test_hash, expires_at))
        conn.commit()

        # Test GET with invalid token
        res_invalid = self.client.get("/reset-password/completely_fake_token")
        self.assertEqual(res_invalid.status_code, 200)
        self.assertIn(b"invalid or has expired", res_invalid.data)

        # Test GET with valid token
        res_valid_get = self.client.get(f"/reset-password/{raw_test_token}")
        self.assertEqual(res_valid_get.status_code, 200)
        self.assertIn(b"Set New Password", res_valid_get.data)

        # Test POST password mismatch
        res_mismatch = self.client.post(f"/reset-password/{raw_test_token}", data={
            "password": new_password,
            "confirm_password": "mismatched_password"
        })
        self.assertIn(b"Passwords do not match", res_mismatch.data)

        # Test POST successful reset
        res_success = self.client.post(f"/reset-password/{raw_test_token}", data={
            "password": new_password,
            "confirm_password": new_password
        })
        self.assertIn(b"successfully reset", res_success.data)

        # Verify token is now marked used
        cur.execute("SELECT used FROM password_reset_token WHERE token_hash=%s", (test_hash,))
        updated_token = cur.fetchone()
        self.assertEqual(updated_token["used"], 1)
        conn.close()

        # Test re-using the same token -> must be rejected
        res_reuse = self.client.get(f"/reset-password/{raw_test_token}")
        self.assertIn(b"invalid or has expired", res_reuse.data)

        # Verify login with old password fails
        res_old_login = self.client.post("/login", data={
            "email": email,
            "password": old_password
        })
        self.assertIn(b"Invalid Email or Password", res_old_login.data)

        # Verify login with new password succeeds
        res_new_login = self.client.post("/login", data={
            "email": email,
            "password": new_password
        }, follow_redirects=True)
        self.assertEqual(res_new_login.status_code, 200)
        self.assertIn(b"Token Student", res_new_login.data)

    def test_11_test_result_email_and_submission(self):
        # 1. Login
        email = "tokenstudent@test.com"
        new_password = "NewPassword456"
        self.client.post("/login", data={
            "email": email,
            "password": new_password
        }, follow_redirects=True)

        # 2. Submit test for GATE Practice Quiz 2 (exam_id=12)
        res_sub = self.client.post("/submit-test/12", data={
            "question_146": "A"
        })
        self.assertEqual(res_sub.status_code, 200)
        self.assertIn(b"Assessment Completed", res_sub.data)
        self.assertIn(b"GATE Practice Quiz 2", res_sub.data)

    def test_12_expired_token_handling(self):
        import secrets
        import hashlib
        from datetime import datetime, timedelta

        email = "expiredstudent@test.com"
        pw = "TestPassword123"
        self.client.post("/register", data={
            "fullname": "Expired Student",
            "email": email,
            "password": pw,
            "confirm_password": pw
        }, follow_redirects=True)
        self.client.get("/logout")

        raw_expired_token = secrets.token_urlsafe(32)
        expired_hash = hashlib.sha256(raw_expired_token.encode()).hexdigest()
        # Expired 10 minutes ago
        past_time = datetime.now() - timedelta(minutes=10)

        conn = pymysql.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB
        )
        cur = conn.cursor(pymysql.cursors.DictCursor)
        cur.execute("SELECT student_id FROM student WHERE email=%s", (email,))
        student = cur.fetchone()
        cur.execute("""
            INSERT INTO password_reset_token (student_id, token_hash, expires_at, used)
            VALUES (%s, %s, %s, 0)
        """, (student["student_id"], expired_hash, past_time))
        conn.commit()
        conn.close()

        # Accessing with expired token must show invalid/expired
        res = self.client.get(f"/reset-password/{raw_expired_token}")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"invalid or has expired", res.data)

if __name__ == "__main__":
    unittest.main()

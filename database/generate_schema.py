import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from database.migrate import all_exams, all_practice_questions

def generate_schema_sql():
    schema_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "schema.sql"))
    with open(schema_path, "w", encoding="utf-8") as f:
        f.write("""-- SmartPrep Database Schema
-- Competitive Exam Preparation and Progress Tracking System

CREATE DATABASE IF NOT EXISTS smartprep;
USE smartprep;

-- 1. Student Table
CREATE TABLE IF NOT EXISTS student (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Admin Table
CREATE TABLE IF NOT EXISTS admin (
    admin_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);

-- 3. Exam Table
CREATE TABLE IF NOT EXISTS exam (
    exam_id INT AUTO_INCREMENT PRIMARY KEY,
    exam_name VARCHAR(100) NOT NULL,
    description TEXT,
    duration_minutes INT DEFAULT 30
);

-- 4. Question Table
CREATE TABLE IF NOT EXISTS question (
    question_id INT AUTO_INCREMENT PRIMARY KEY,
    exam_id INT NOT NULL,
    question_text TEXT NOT NULL,
    option_a VARCHAR(255) NOT NULL,
    option_b VARCHAR(255) NOT NULL,
    option_c VARCHAR(255) NOT NULL,
    option_d VARCHAR(255) NOT NULL,
    correct_answer CHAR(1) NOT NULL,
    FOREIGN KEY (exam_id) REFERENCES exam(exam_id) ON DELETE CASCADE
);

-- 5. Result Table
CREATE TABLE IF NOT EXISTS result (
    result_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    exam_id INT NOT NULL,
    score INT NOT NULL,
    total_questions INT DEFAULT 0,
    percentage FLOAT DEFAULT 0.0,
    test_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES student(student_id) ON DELETE CASCADE,
    FOREIGN KEY (exam_id) REFERENCES exam(exam_id) ON DELETE CASCADE
);

-- 6. Password Reset Token Table
CREATE TABLE IF NOT EXISTS password_reset_token (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    token_hash VARCHAR(255) NOT NULL,
    expires_at DATETIME NOT NULL,
    used TINYINT(1) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES student(student_id) ON DELETE CASCADE
);

-- Active Exams and Practice Quizzes
INSERT IGNORE INTO exam (exam_id, exam_name, description, duration_minutes) VALUES
""")
        exam_entries = []
        for ex in all_exams:
            name = str(ex[1]).replace("'", "''")
            desc = str(ex[2]).replace("'", "''")
            exam_entries.append(f"({ex[0]}, '{name}', '{desc}', {ex[3]})")
        f.write(",\n".join(exam_entries) + ";\n\n")

        f.write("-- Questions for All Exams and Practice Quizzes\nINSERT IGNORE INTO question (question_id, exam_id, question_text, option_a, option_b, option_c, option_d, correct_answer) VALUES\n")
        q_entries = []
        for q in all_practice_questions:
            qt = str(q[2]).replace("'", "''")
            oa = str(q[3]).replace("'", "''")
            ob = str(q[4]).replace("'", "''")
            oc = str(q[5]).replace("'", "''")
            od = str(q[6]).replace("'", "''")
            q_entries.append(f"({q[0]}, {q[1]}, '{qt}', '{oa}', '{ob}', '{oc}', '{od}', '{q[7]}')")
        f.write(",\n".join(q_entries) + ";\n")
    print(f"Generated {schema_path} with {len(all_exams)} exams and {len(all_practice_questions)} questions.")

if __name__ == "__main__":
    generate_schema_sql()

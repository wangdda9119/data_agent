-- 1. course 테이블 생성
CREATE TABLE course (
    id SERIAL PRIMARY KEY,
    course_name VARCHAR(255) NOT NULL,
    description TEXT
);

-- 2. course 예시 데이터 삽입
INSERT INTO course (course_name, description) VALUES
('Python Backend Development', 'Python과 FastAPI를 활용한 백엔드 개발'),
('Data Science with Python', '데이터 분석 및 머신러닝 기초'),
('Web Frontend Development', 'React와 TypeScript 기반 프론트엔드 개발');

-- 3. student 테이블에 course_id 컬럼 추가
ALTER TABLE student 
ADD COLUMN course_id INTEGER,
ADD CONSTRAINT fk_student_course 
    FOREIGN KEY (course_id) 
    REFERENCES course(id) 
    ON DELETE SET NULL;

-- 4. 마이페이지 조회 SQL
SELECT 
    s.email,
    s.name,
    c.course_name
FROM student s
LEFT JOIN course c ON s.course_id = c.id
WHERE s.id = $1;

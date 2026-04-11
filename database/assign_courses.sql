-- 학생에게 코스 할당

-- 예시 1: 특정 학생 1명에게 코스 할당
UPDATE student SET course_id = 1 WHERE id = 1;

-- 예시 2: 여러 학생에게 각각 다른 코스 할당
UPDATE student SET course_id = 1 WHERE id IN (1, 2, 3);
UPDATE student SET course_id = 2 WHERE id IN (4, 5);
UPDATE student SET course_id = 3 WHERE id = 6;

-- 예시 3: 이메일로 특정 학생에게 코스 할당
UPDATE student SET course_id = 1 WHERE email = 'student@example.com';

-- 예시 4: course_id가 NULL인 모든 학생에게 기본 코스 할당
UPDATE student SET course_id = 1 WHERE course_id IS NULL;

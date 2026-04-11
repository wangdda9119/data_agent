# 마이페이지 API 사용 가이드

## 1. SQL 실행

### 환경변수 설정
```bash
set DB_HOST=localhost
set DB_NAME=your_database
set DB_USER=postgres
set DB_PASSWORD=your_password
```

### 스키마 실행
```bash
python database/run_schema.py
```

## 2. API 서버 실행

```bash
uvicorn main:app --reload
```

서버 주소: `http://localhost:8000`

## 3. 마이페이지 접근

### 엔드포인트
```
GET http://localhost:8000/api/mypage
```

### 요청 예시 (curl)
```bash
curl -X GET "http://localhost:8000/api/mypage" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### 요청 예시 (Python requests)
```python
import requests

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
headers = {"Authorization": f"Bearer {token}"}

response = requests.get("http://localhost:8000/api/mypage", headers=headers)
print(response.json())
```

### 요청 예시 (JavaScript fetch)
```javascript
const token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...";

fetch("http://localhost:8000/api/mypage", {
  headers: {
    "Authorization": `Bearer ${token}`
  }
})
.then(res => res.json())
.then(data => console.log(data));
```

## 4. JWT 토큰 생성 (테스트용)

```python
import jwt
from datetime import datetime, timedelta

JWT_SECRET = "your-secret-key"

payload = {
    "user_id": 1,  # student.id
    "exp": datetime.utcnow() + timedelta(hours=24)
}

token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
print(token)
```

## 5. Swagger UI로 테스트

브라우저에서 접속:
```
http://localhost:8000/docs
```

1. `/api/mypage` 엔드포인트 클릭
2. "Try it out" 클릭
3. 🔒 Authorize 버튼 클릭
4. JWT 토큰 입력 후 "Authorize"
5. "Execute" 클릭

## 응답 예시

```json
{
  "email": "student@example.com",
  "name": "홍길동",
  "course_name": "Python Backend Development"
}
```

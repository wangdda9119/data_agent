# 마이페이지 API 응답 예시

## 요청
```http
GET /mypage
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## 성공 응답 (200 OK)
```json
{
  "email": "student@example.com",
  "name": "홍길동",
  "course_name": "Python Backend Development"
}
```

## 코스가 없는 경우 (200 OK)
```json
{
  "email": "student@example.com",
  "name": "홍길동",
  "course_name": null
}
```

## 인증 실패 (401 Unauthorized)
```json
{
  "detail": "유효하지 않은 토큰입니다"
}
```

## 사용자 없음 (404 Not Found)
```json
{
  "detail": "사용자를 찾을 수 없습니다"
}
```

# Frontend Harness Rules

> Vue 3, TypeScript, Tailwind CSS 관련 코드 수정 시 이 문서를 반드시 준수합니다.
> 프론트엔드 루트: `frontend/sch-landing-vue/src/`

---

## 1. 기술 스택 고정

| 항목 | 구현체 | 비고 |
|------|--------|------|
| 프레임워크 | Vue 3 (Composition API 권장) | `main.ts`에서 `createApp` |
| 언어 | TypeScript (`.ts`, `.vue`) | `env.d.ts`에 타입 선언 |
| 스타일링 | Tailwind CSS | `styles/` 디렉토리 |
| 라우팅 | Vue Router (`createWebHistory`) | `router.ts` |
| HTTP 통신 | fetch API (Axios 미사용, 현재 구현 기준) | `api/client.ts` |

---

## 2. 파일별 책임 분리

### 2.1 `api/client.ts` — API 통신 클라이언트 (핵심)

```typescript
// ApiClient 클래스 구조 (싱글턴 export):
class ApiClient {
    private accessToken: string | null    // localStorage에서 복원
    private refreshToken: string | null   // localStorage에서 복원

    setTokens(accessToken, refreshToken)  // localStorage 저장 + 내부 상태 갱신
    clearTokens()                         // localStorage 삭제 + 내부 상태 초기화

    signup(data: SignupRequest)           // POST /auth/signup
    login(data: LoginRequest)             // POST /auth/login → setTokens() 자동 호출
    logout()                              // POST /auth/logout (Bearer AT + body RT) → clearTokens()
    getMe(): UserInfo                     // GET /auth/me (Bearer AT)
    chat(query: string): string           // POST /api/chat → result.answer 반환

    isAuthenticated(): boolean            // !!this.accessToken
}

export const apiClient = new ApiClient()  // 싱글턴
```

**인터페이스 (타입 강제):**
```typescript
interface LoginRequest   { email: string; password: string }
interface SignupRequest   { email: string; password: string; nickname?: string }
interface AuthResponse    { access_token: string; refresh_token: string; token_type: string }
interface UserInfo        { id: number; email: string; nickname: string | null; is_active: boolean; created_at: string }
```

**수정 시 준수 사항:**
- API_BASE_URL은 `'http://localhost:8000'` 고정 (환경변수 방식 전환 시 사용자 허가 필요)
- `login()` 성공 시 **반드시** `setTokens()` 호출
- `logout()` 완료 시 **반드시** `clearTokens()` 호출
- 모든 인증 요청의 Header: `Authorization: Bearer ${this.accessToken}`
- 로그아웃 body: `{ refresh_token: this.refreshToken }`

### 2.2 `api/authModal.js` — 인증 모달 헬퍼 (JavaScript)
- 레거시 JS 파일 — 신규 수정 시 TypeScript 전환 권장하되, 기존 코드 동작에 영향 주지 않도록 주의

### 2.3 `router.ts` — Vue Router 설정
```typescript
const routes = [
    { path: '/',        name: 'Home',    component: Home },
    { path: '/chatbot', name: 'Chatbot', component: ChatbotPage },
    { path: '/mypage',  name: 'Mypage',  component: Mypage }
]
// createWebHistory() 사용 (Hash 모드 아님)
```

**수정 시 준수 사항:**
- 새 라우트 추가 시 컴포넌트 lazy loading(`() => import(...)`) 사용 권장
- path 네이밍: 소문자 kebab-case (`/my-page` 등)
- `/mypage` 등 인증 필요 라우트에는 Navigation Guard 추가 권장

---

## 3. 컴포넌트 구조 맵

```
app/components/
├── Header.vue       ← 전역 네비게이션 바 (모든 페이지에서 사용)
├── Home.vue         ← 랜딩 페이지 (Hero, About, Campus, Departments 등 조합)
├── Hero.vue         ← 히어로 섹션
├── About.vue        ← 학교 소개 섹션
├── Campus.vue       ← 캠퍼스 소개 섹션
├── Departments.vue  ← 학과 소개 섹션
├── Admission.vue    ← 입학 정보 섹션
├── Footer.vue       ← 전역 푸터
├── Chatbot.vue      ← 플로팅 챗봇 위젯 (빠른 질문 버튼 포함)
├── ChatbotPage.vue  ← /chatbot 전용 페이지
├── Login.vue        ← 로그인 모달
├── Signup.vue       ← 회원가입 모달
└── Mypage.vue       ← /mypage 학생 정보 + 수강과정 조회
```

**컴포넌트 설계 원칙:**
- 각 `.vue` 파일은 **하나의 명확한 역할**만 수행
- `Home.vue`는 여러 섹션 컴포넌트를 조합하는 **컨테이너** 역할
- `Chatbot.vue`는 **플로팅 위젯** (어느 페이지에서든 표시 가능)
- `ChatbotPage.vue`는 **전체 페이지** (/chatbot 라우트 전용)
- `Login.vue`/`Signup.vue`는 **모달** — 별도 라우트 없이 Header에서 트리거

---

## 4. 토큰 흐름 (Frontend ↔ Backend)

```
[회원가입]
  Signup.vue → apiClient.signup({ email, password, nickname })
    → POST /auth/signup → 성공 시 안내 메시지

[로그인]
  Login.vue → apiClient.login({ email, password })
    → POST /auth/login → AuthResponse 반환
    → apiClient.setTokens(access_token, refresh_token)
    → localStorage에 저장

[인증 API 호출]
  Mypage.vue → apiClient.getMe()
    → GET /auth/me, Header: Authorization: Bearer {access_token}
    → UserInfo 반환

[채팅]
  Chatbot.vue → apiClient.chat(query)
    → POST /api/chat, Body: { query }
    → { answer: "..." } 반환

[로그아웃]
  Header.vue → apiClient.logout()
    → POST /auth/logout
       Header: Bearer {access_token}
       Body: { refresh_token }
    → apiClient.clearTokens()
    → localStorage 클리어
```

---

## 5. TypeScript 규칙

### 5.1 타입 선언 필수
- **`any` 타입 사용 절대 금지** — 모든 데이터에 명시적 `interface`/`type` 정의
- API 응답은 반드시 `client.ts`의 기존 인터페이스 활용 또는 새로 정의
- 컴포넌트의 `ref()`, `reactive()` 사용 시 제네릭 타입 명시

### 5.2 예시
```typescript
// ✅ Good
const userInfo = ref<UserInfo | null>(null)
const messages = ref<Array<{ role: string; content: string }>>([])

// ❌ Bad
const userInfo = ref<any>(null)
const messages = ref([])  // 타입 추론 불명확
```

---

## 6. 스타일링 규칙

- **Tailwind CSS 유틸리티 클래스** 사용
- 인라인 `style` 속성 최소화 — Tailwind 클래스로 대체
- 반복되는 스타일 조합은 컴포넌트로 추출하거나 `@apply` 디렉티브 사용
- 다크 모드 고려: `dark:` prefix 활용 권장
- 반응형 필수: `sm:`, `md:`, `lg:` breakpoint 사용

---

## 7. 코드 수정 시 체크리스트

새 컴포넌트 추가 시:
- [ ] `app/components/` 하위에 `.vue` 파일로 생성했는가?
- [ ] 라우트가 필요하면 `router.ts`에 등록했는가?
- [ ] API 호출이 필요하면 `apiClient`의 기존 메서드를 활용하거나 새 메서드를 추가했는가?
- [ ] 타입을 `client.ts`에 인터페이스로 정의했는가?

기존 컴포넌트 수정 시:
- [ ] props/emits 시그니처가 변경되면 사용처도 함께 수정했는가?
- [ ] `apiClient`의 메서드 시그니처 변경 시 모든 호출처를 업데이트했는가?

인증 관련 수정 시:
- [ ] `apiClient.setTokens()` / `clearTokens()` 호출 타이밍이 올바른가?
- [ ] localStorage의 키 이름(`access_token`, `refresh_token`)을 변경하지 않았는가?

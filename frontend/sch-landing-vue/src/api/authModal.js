import { apiClient } from './client'

export function showLoginModal() {
  const modal = document.createElement('div')
  modal.className = 'fixed inset-0 z-[9999] flex items-center justify-center bg-black/50 p-4'
  modal.innerHTML = `
    <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md p-8">
      <h2 class="text-3xl font-bold text-gray-900 mb-8 text-center">로그인</h2>
      
      <form id="loginForm" class="space-y-6">
        <div>
          <label class="block text-sm font-semibold text-gray-700 mb-2">이메일</label>
          <input
            id="loginEmail"
            type="email"
            required
            class="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:outline-none transition-colors"
            placeholder="example@email.com"
          />
        </div>
        
        <div>
          <label class="block text-sm font-semibold text-gray-700 mb-2">비밀번호</label>
          <input
            id="loginPassword"
            type="password"
            required
            class="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:outline-none transition-colors"
            placeholder="비밀번호를 입력하세요"
          />
        </div>
        
        <div id="loginError" class="hidden bg-red-50 text-red-600 px-4 py-3 rounded-xl text-sm"></div>
        
        <button 
          type="submit" 
          class="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 rounded-xl transition-colors"
        >
          로그인
        </button>
        
        <div class="text-center space-y-2">
          <button
            type="button"
            id="switchToSignup"
            class="text-sm text-blue-600 hover:text-blue-700 font-medium"
          >
            계정이 없으신가요? 회원가입
          </button>
          
          <div>
            <button
              type="button"
              id="closeLogin"
              class="text-sm text-gray-500 hover:text-gray-700"
            >
              닫기
            </button>
          </div>
        </div>
      </form>
    </div>
  `
  
  document.body.appendChild(modal)
  
  const form = document.getElementById('loginForm')
  const errorDiv = document.getElementById('loginError')
  
  form.addEventListener('submit', async (e) => {
    e.preventDefault()
    errorDiv.classList.add('hidden')
    
    const email = document.getElementById('loginEmail').value
    const password = document.getElementById('loginPassword').value
    
    try {
      await apiClient.login({ email, password })
      modal.remove()
      window.location.reload()
    } catch (error) {
      errorDiv.textContent = '로그인에 실패했습니다. 이메일과 비밀번호를 확인해주세요.'
      errorDiv.classList.remove('hidden')
    }
  })
  
  document.getElementById('switchToSignup').addEventListener('click', () => {
    modal.remove()
    showSignupModal()
  })
  
  document.getElementById('closeLogin').addEventListener('click', () => {
    modal.remove()
  })
  
  modal.addEventListener('click', (e) => {
    if (e.target === modal) modal.remove()
  })
}

export function showSignupModal() {
  const modal = document.createElement('div')
  modal.className = 'fixed inset-0 z-[9999] flex items-center justify-center bg-black/50 p-4'
  modal.innerHTML = `
    <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md p-8">
      <h2 class="text-3xl font-bold text-gray-900 mb-8 text-center">회원가입</h2>
      
      <form id="signupForm" class="space-y-6">
        <div>
          <label class="block text-sm font-semibold text-gray-700 mb-2">이메일</label>
          <input
            id="signupEmail"
            type="email"
            required
            class="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:outline-none transition-colors"
            placeholder="example@email.com"
          />
        </div>
        
        <div>
          <label class="block text-sm font-semibold text-gray-700 mb-2">비밀번호</label>
          <input
            id="signupPassword"
            type="password"
            required
            minlength="6"
            class="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:outline-none transition-colors"
            placeholder="6자 이상"
          />
        </div>
        
        <div>
          <label class="block text-sm font-semibold text-gray-700 mb-2">닉네임 (선택)</label>
          <input
            id="signupNickname"
            type="text"
            class="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:outline-none transition-colors"
            placeholder="닉네임"
          />
        </div>
        
        <div id="signupError" class="hidden bg-red-50 text-red-600 px-4 py-3 rounded-xl text-sm"></div>
        <div id="signupSuccess" class="hidden bg-green-50 text-green-600 px-4 py-3 rounded-xl text-sm"></div>
        
        <button 
          type="submit" 
          class="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 rounded-xl transition-colors"
        >
          회원가입
        </button>
        
        <div class="text-center space-y-2">
          <button
            type="button"
            id="switchToLogin"
            class="text-sm text-blue-600 hover:text-blue-700 font-medium"
          >
            이미 계정이 있으신가요? 로그인
          </button>
          
          <div>
            <button
              type="button"
              id="closeSignup"
              class="text-sm text-gray-500 hover:text-gray-700"
            >
              닫기
            </button>
          </div>
        </div>
      </form>
    </div>
  `
  
  document.body.appendChild(modal)
  
  const form = document.getElementById('signupForm')
  const errorDiv = document.getElementById('signupError')
  const successDiv = document.getElementById('signupSuccess')
  
  form.addEventListener('submit', async (e) => {
    e.preventDefault()
    errorDiv.classList.add('hidden')
    successDiv.classList.add('hidden')
    
    const email = document.getElementById('signupEmail').value
    const password = document.getElementById('signupPassword').value
    const nickname = document.getElementById('signupNickname').value
    
    try {
      await apiClient.signup({ email, password, nickname: nickname || undefined })
      successDiv.textContent = '회원가입 성공! 로그인해주세요.'
      successDiv.classList.remove('hidden')
      setTimeout(() => {
        modal.remove()
        showLoginModal()
      }, 1500)
    } catch (error) {
      errorDiv.textContent = '회원가입에 실패했습니다. 이미 사용 중인 이메일일 수 있습니다.'
      errorDiv.classList.remove('hidden')
    }
  })
  
  document.getElementById('switchToLogin').addEventListener('click', () => {
    modal.remove()
    showLoginModal()
  })
  
  document.getElementById('closeSignup').addEventListener('click', () => {
    modal.remove()
  })
  
  modal.addEventListener('click', (e) => {
    if (e.target === modal) modal.remove()
  })
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

export interface LoginRequest {
  email: string
  password: string
}

export interface SignupRequest {
  email: string
  password: string
  nickname?: string
}

export interface AuthResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface UserInfo {
  id: number
  email: string
  nickname: string | null
  is_active: boolean
  created_at: string
}

class ApiClient {
  private accessToken: string | null = null
  private refreshToken: string | null = null

  constructor() {
    this.accessToken = localStorage.getItem('access_token')
    this.refreshToken = localStorage.getItem('refresh_token')
  }

  setTokens(accessToken: string, refreshToken: string) {
    this.accessToken = accessToken
    this.refreshToken = refreshToken
    localStorage.setItem('access_token', accessToken)
    localStorage.setItem('refresh_token', refreshToken)
  }

  clearTokens() {
    this.accessToken = null
    this.refreshToken = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  async signup(data: SignupRequest) {
    const response = await fetch(`${API_BASE_URL}/auth/signup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    })
    if (!response.ok) throw new Error('Signup failed')
    return response.json()
  }

  async login(data: LoginRequest): Promise<AuthResponse> {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    })
    if (!response.ok) throw new Error('Login failed')
    const result = await response.json()
    this.setTokens(result.access_token, result.refresh_token)
    return result
  }

  async logout() {
    if (!this.accessToken) return

    await fetch(`${API_BASE_URL}/auth/logout`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${this.accessToken}`,
      },
      body: JSON.stringify({ refresh_token: this.refreshToken }),
    })
    this.clearTokens()
  }

  async getMe(): Promise<UserInfo> {
    const response = await fetch(`${API_BASE_URL}/auth/me`, {
      headers: { Authorization: `Bearer ${this.accessToken}` },
    })
    if (!response.ok) throw new Error('Failed to get user info')
    return response.json()
  }

  async chat(query: string): Promise<string> {
    const response = await fetch(`${API_BASE_URL}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query }),
    })
    if (!response.ok) throw new Error('Chat request failed')
    const result = await response.json()
    return result.answer
  }

  isAuthenticated(): boolean {
    return !!this.accessToken
  }
}

export const apiClient = new ApiClient()

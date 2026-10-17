export interface User {
  id: string
  fullName: string
  email: string
  dateOfBirth?: string
  phone?: string
  avatarUrl?: string
  createdAt?: string
}

export interface AuthResponse {
  user: User
  token: string
}

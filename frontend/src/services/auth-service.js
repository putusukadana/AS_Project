import api from './api'

const register = async (userData) => {
  try {
    const response = await api.post('/users', userData)
    return response.data
  } catch (error) {
    throw error.response?.data?.detail?.message || 'An error occurred during registration.'
  }
}

const login = async (credentials) => {
  try {
    const response = await api.post('/users/login', credentials)
    return response.data
  } catch (error) {
    throw error.response?.data?.detail?.message || 'An error occurred during login.'
  }
}

export default {
  register,
  login
}

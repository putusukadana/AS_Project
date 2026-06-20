import api from './api'

const register = async (userData) => {
  try {
    const response = await api.post('/users', userData)
    return response.data
  } catch (error) {
    const message = error.response?.data?.detail?.message || 'An error occurred during registration.'
    throw new Error(message)
  }
}

const login = async (credentials) => {
  try {
    const response = await api.post('/users/login', credentials)
    return response.data
  } catch (error) {
    const message = error.response?.data?.detail?.message || 'An error occurred during login.'
    throw new Error(message)
  }
}

export default {
  register,
  login
}

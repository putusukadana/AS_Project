import axios from 'axios'

const API_URL = 'http://localhost:8000/api/v1'

const register = async (userData) => {
  try {
    const response = await axios.post(`${API_URL}/users`, userData)
    return response.data
  } catch (error) {
    throw error.response?.data?.detail?.message || 'An error occurred during registration.'
  }
}

const login = async (credentials) => {
  try {
    const response = await axios.post(`${API_URL}/users/login`, credentials)
    return response.data
  } catch (error) {
    throw error.response?.data?.detail?.message || 'An error occurred during login.'
  }
}

export default {
  register,
  login
}

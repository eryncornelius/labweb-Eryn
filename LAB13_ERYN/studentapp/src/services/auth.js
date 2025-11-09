// src/services/auth.js
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

// === LOGIN ===
export const login = async (email, password) => {
  try {
    const username = email.split('@')[0];

    const response = await axios.post(`${API_BASE_URL}/token/`, {
      username: username,
      password: password,
    });

    const { token, email, full_name, major, role } = response.data;
    const { access, refresh } = token;

    if (access) {
      const userData = {
        email,
        full_name,
        major,
        role
      };

      localStorage.setItem('access_token', access);
      localStorage.setItem('refresh_token', refresh);
      localStorage.setItem('user', JSON.stringify(userData));

      return { success: true, data: userData };
    } else {
      return { success: false, error: 'Invalid token response' };
    }
  } catch (error) {
    console.error('Login error:', error);
    return {
      success: false,
      error:
        error.response?.data?.detail ||
        error.response?.data?.message ||
        error.message ||
        'Login failed',
    };
  }
};

// === REGISTER ===
export const register = async (email, fullName, password, confirmPassword) => {
  if (password !== confirmPassword) {
    return { success: false, error: 'Passwords do not match' };
  }

  try {
    const username = email.split('@')[0];

    const response = await axios.post(`${API_BASE_URL}/register/`, {
      email: email,
      username: username,
      full_name: fullName,
      password: password,
      password_confirmation: confirmPassword,
      role: email.includes('@student.') ? 'student' : 'instructor'
    });

    return { success: true, data: response.data };
  } catch (error) {
    console.error('Registration error:', error);
    return {
      success: false,
      error:
        error.response?.data?.detail ||
        error.response?.data?.message ||
        error.message ||
        'Registration failed',
    };
  }
};
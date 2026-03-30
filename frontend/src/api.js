import axios from 'axios'

export const api = axios.create({
  baseURL: 'http://127.0.0.1:8001',
})

export function setToken(token) {
  if (token) {
    api.defaults.headers.common.Authorization = `Bearer ${token}`
    return
  }
  delete api.defaults.headers.common.Authorization
}


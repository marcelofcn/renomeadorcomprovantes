import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

const healthCheck = () => api.get('/health')

const uploadComprovante = (formData: FormData) =>
  api.post('/upload/pdf', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })

const listarComprovantes = () => api.get('/comprovantes')

export default {
  healthCheck,
  uploadComprovante,
  listarComprovantes,
}

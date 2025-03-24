// src/boot/axios.js
import { boot } from 'quasar/wrappers'
import axios from 'axios'

// Cria uma instância do axios
const api = axios.create({
  // Configurações padrão
  timeout: 10000, // 10 segundos
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  },
})

export default boot(({ app }) => {
  // Para uso dentro de arquivos Vue (Options API)
  app.config.globalProperties.$axios = axios
  // Para uso dentro de arquivos Vue (Options API)
  app.config.globalProperties.$api = api
})

export { api }

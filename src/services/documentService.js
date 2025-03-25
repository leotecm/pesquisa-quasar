import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000'

export const getRecentDocuments = async () => {
  try {
    console.log('Iniciando busca de documentos recentes')
    const response = await axios.get(`${API_URL}/api/documents/recent`)
    console.log('Resposta da busca de documentos recentes:', response.data)
    return response.data
  } catch (error) {
    console.error('Erro ao buscar documentos recentes:', error)
    throw error
  }
}

export const clearRecentDocuments = async () => {
  try {
    const response = await axios.post(`${API_URL}/api/documents/recent/clear`)
    return response.data
  } catch (error) {
    console.error('Erro ao limpar documentos recentes:', error)
    throw error
  }
}

export const registerDocumentAccess = async (filename) => {
  try {
    console.log('Iniciando registro de acesso para:', filename)
    const response = await axios.post(`${API_URL}/api/documents/access`, { filename })
    console.log('Resposta do registro de acesso:', response.data)
    return response.data
  } catch (error) {
    console.error('Erro ao registrar acesso ao documento:', error)
    throw error
  }
}

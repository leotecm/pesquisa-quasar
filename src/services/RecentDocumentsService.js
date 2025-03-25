import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000'

/**
 * Serviço para gerenciar documentos recentes
 */
class RecentDocumentsService {
  /**
   * Busca os documentos recentes
   * @returns {Promise<Array>} Lista de documentos recentes
   */
  async getRecentDocuments() {
    try {
      const response = await axios.get(`${API_URL}/api/documents/recent`)
      return response.data
    } catch (error) {
      console.error('Erro ao buscar documentos recentes:', error)
      throw error
    }
  }

  /**
   * Registra o acesso a um documento
   * @param {string} filename - Nome do arquivo acessado
   * @returns {Promise} Promessa da requisição
   */
  async registerAccess(filename) {
    try {
      await axios.post(`${API_URL}/api/documents/access`, {
        filename,
        timestamp: new Date().toISOString(),
      })
    } catch (error) {
      console.error('Erro ao registrar acesso ao documento:', error)
      throw error
    }
  }
}

export default new RecentDocumentsService()

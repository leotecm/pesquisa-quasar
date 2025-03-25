// src/services/fileService.js
import { api } from 'boot/axios'

// URL base da API (ajuste conforme seu ambiente)
const API_URL = 'http://localhost:5000'

// Função para obter todos os documentos
export async function getDocuments(filter = null, type = null) {
  try {
    // Buscar lista de arquivos do backend
    const response = await api.get(`${API_URL}/files`)

    // Transformar a lista de nomes de arquivos em objetos de documento
    let documents = response.data.map((filename) => {
      const extension = filename.split('.').pop().toLowerCase()
      const id = encodeURIComponent(filename) // Usar o nome do arquivo como ID

      return {
        id,
        name: filename,
        type: extension,
        lastModified: new Date().toISOString(), // O backend não fornece esta info
        path: `${API_URL}/file-content/${encodeURIComponent(filename)}`,
      }
    })

    // Aplicar filtros se necessário
    if (filter === 'recent') {
      // Como não temos data real, vamos simplesmente pegar os 2 primeiros
      documents = documents.slice(0, 2)
    } else if (filter === 'favorite') {
      // Em uma aplicação real, teria uma propriedade de favorito
      // Aqui vamos apenas filtrar aleatoriamente como exemplo
      documents = documents.filter((_, index) => index % 2 === 0)
    }

    if (type) {
      // Filtrar por tipo de documento
      if (type === 'doc') {
        documents = documents.filter((doc) => doc.type === 'doc' || doc.type === 'docx')
      } else {
        documents = documents.filter((doc) => doc.type === type)
      }
    }

    return documents
  } catch (error) {
    console.error('Erro ao buscar documentos:', error)
    throw error
  }
}

// Função para obter o conteúdo de um documento específico
export async function getDocumentContent(documentId) {
  try {
    // Como o ID é o nome do arquivo codificado, precisamos decodificá-lo
    const filename = decodeURIComponent(documentId)

    // Buscar conteúdo do documento
    const response = await api.get(`${API_URL}/file-content/${encodeURIComponent(filename)}`)

    // Formatar o conteúdo como HTML
    let content = ''
    if (response.data && response.data.content) {
      // Transformar quebras de linha em tags <p>
      content = response.data.content
        .split('\n')
        .filter((line) => line.trim() !== '')
        .map((line) => `<p>${line}</p>`)
        .join('')
    }

    return content
  } catch (error) {
    console.error('Erro ao buscar conteúdo do documento:', error)
    throw error
  }
}

// Para compatibilidade com o código existente
export async function getDocumentById(id) {
  try {
    const documents = await getDocuments()
    const document = documents.find((doc) => doc.id === id)

    if (document) {
      // Buscar o conteúdo do documento
      document.content = await getDocumentContent(id)
    }

    return document || null
  } catch (error) {
    console.error('Erro ao buscar documento por ID:', error)
    throw error
  }
}

// Função para salvar um novo documento (não implementada no backend)
export async function saveDocument() {
  // Esta função precisaria de um endpoint de upload no backend
  // Como não temos isso no código Python fornecido, vamos apenas simular um erro
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      reject(new Error('Upload de arquivos não está implementado no backend'))
    }, 500)
  })
}

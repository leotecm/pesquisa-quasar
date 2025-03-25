/**
 * Calcula a distância de Levenshtein entre duas strings
 * @param {string} a - Primeira string
 * @param {string} b - Segunda string
 * @returns {number} - Distância entre as strings
 */
function levenshteinDistance(a, b) {
  if (a.length === 0) return b.length
  if (b.length === 0) return a.length

  const matrix = []

  // Incrementa ao longo da primeira coluna de cada linha
  for (let i = 0; i <= b.length; i++) {
    matrix[i] = [i]
  }

  // Incrementa cada coluna na primeira linha
  for (let j = 0; j <= a.length; j++) {
    matrix[0][j] = j
  }

  // Preenche o resto da matriz
  for (let i = 1; i <= b.length; i++) {
    for (let j = 1; j <= a.length; j++) {
      if (b.charAt(i - 1) === a.charAt(j - 1)) {
        matrix[i][j] = matrix[i - 1][j - 1]
      } else {
        matrix[i][j] = Math.min(
          matrix[i - 1][j - 1] + 1, // substituição
          Math.min(
            matrix[i][j - 1] + 1, // inserção
            matrix[i - 1][j] + 1, // remoção
          ),
        )
      }
    }
  }

  return matrix[b.length][a.length]
}

/**
 * Verifica se uma palavra corresponde ao termo de busca com tolerância a erros
 * @param {string} word - Palavra a ser verificada
 * @param {string} searchTerm - Termo de busca
 * @returns {object} - Objeto com informações sobre a correspondência
 */
function matchWord(word, searchTerm) {
  // Normaliza as strings para comparação (remove acentos, converte para minúsculas)
  const normalizedWord = word
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
  const normalizedTerm = searchTerm
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')

  console.log('Comparando palavras:', {
    original: word,
    normalized: normalizedWord,
    term: searchTerm,
    normalizedTerm,
  })

  // Correspondência exata
  if (normalizedWord === normalizedTerm) {
    return { matches: true, distance: 0, exact: true }
  }

  // Verifica se a palavra contém o termo de busca
  if (normalizedWord.includes(normalizedTerm)) {
    return { matches: true, distance: 0, exact: false, contains: true }
  }

  // Calcula a distância de Levenshtein
  const distance = levenshteinDistance(normalizedWord, normalizedTerm)

  // Aumenta a tolerância para 30% do tamanho do termo de busca
  const tolerance = Math.max(2, Math.floor(searchTerm.length * 0.3))

  // Retorna true se a distância for menor ou igual à tolerância
  return {
    matches: distance <= tolerance,
    distance,
    exact: false,
    contains: false,
  }
}

/**
 * Pontua um documento baseado na relevância para o termo de busca
 * @param {object} document - Documento a ser pontuado
 * @param {string} searchTerm - Termo de busca
 * @returns {number} - Pontuação de relevância
 */
function scoreDocument(document, searchTerm) {
  let score = 0

  // Primeiro, verifica o nome do arquivo
  const filename = document.filename || ''
  const filenameMatch = matchWord(filename, searchTerm)
  if (filenameMatch.matches) {
    if (filenameMatch.exact) {
      score += 10
    } else if (filenameMatch.contains) {
      score += 5
    } else {
      score += Math.max(0, 3 - filenameMatch.distance)
    }
  }

  // Depois, verifica os highlights se existirem
  if (document.highlights && document.highlights.length > 0) {
    console.log('Processando highlights do documento:', {
      filename: document.filename,
      highlights: document.highlights.length,
    })

    for (const highlight of document.highlights) {
      const highlightWords = highlight.split(/\s+/)
      for (const word of highlightWords) {
        const match = matchWord(word, searchTerm)
        if (match.matches) {
          if (match.exact) {
            score += 10
          } else if (match.contains) {
            score += 5
          } else {
            score += Math.max(0, 3 - match.distance)
          }
        }
      }
    }
  }

  // Por fim, verifica o conteúdo se existir
  if (document.content) {
    const contentWords = document.content.split(/\s+/)
    console.log('Processando conteúdo do documento:', {
      filename: document.filename,
      contentWords: contentWords.length,
    })

    for (const word of contentWords) {
      const match = matchWord(word, searchTerm)
      if (match.matches) {
        if (match.exact) {
          score += 10
        } else if (match.contains) {
          score += 5
        } else {
          score += Math.max(0, 3 - match.distance)
        }
      }
    }
  }

  console.log('Pontuação final do documento:', {
    filename: document.filename,
    score,
    hasHighlights: document.highlights?.length > 0,
    hasContent: !!document.content,
  })

  return score
}

/**
 * Formata os destaques do texto com a tag mark
 * @param {string} text - Texto a ser formatado
 * @param {string} searchTerm - Termo de busca
 * @returns {string} - Texto formatado com tags mark
 */
function formatHighlight(text, searchTerm) {
  if (!text || !searchTerm) return text

  const regex = new RegExp(`(${searchTerm})`, 'gi')
  return text.replace(regex, '<mark>$1</mark>')
}

/**
 * Filtra e ordena os resultados da busca
 * @param {Array} documents - Lista de documentos
 * @param {string} searchTerm - Termo de busca
 * @returns {Array} - Documentos filtrados e ordenados por relevância
 */
export function searchDocuments(documents, searchTerm) {
  if (!searchTerm || searchTerm.trim().length === 0) {
    return documents
  }

  console.log('Iniciando busca com termo:', searchTerm)
  console.log('Documentos recebidos:', documents)

  // Filtra e pontua os documentos
  const scoredDocuments = documents
    .map((doc) => {
      const score = scoreDocument(doc, searchTerm)

      // Formata os highlights com a tag mark
      if (doc.highlights) {
        doc.highlights = doc.highlights.map((highlight) => formatHighlight(highlight, searchTerm))
      }

      console.log(`Documento ${doc.filename} pontuado com ${score}`)
      return {
        ...doc,
        score,
      }
    })
    .filter((doc) => doc.score > 0)
    .sort((a, b) => b.score - a.score)

  console.log('Documentos filtrados e ordenados:', scoredDocuments)
  return scoredDocuments
}

export default {
  searchDocuments,
}

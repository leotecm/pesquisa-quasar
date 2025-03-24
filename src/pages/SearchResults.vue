<!-- src/pages/SearchResults.vue -->
<!-- src/pages/SearchResults.vue -->
<!-- src/pages/SearchResults.vue -->
<template>
  <q-page padding class="search-results-page">
    <!-- Título da página e instruções iniciais -->
    <div v-if="!searchPerformed && !currentQuery" class="text-center q-mt-xl">
      <h4 class="text-h4 q-mb-md">Sistema de Busca de Documentos</h4>
      <p class="text-subtitle1 q-mb-xl">
        Digite um termo na barra de pesquisa abaixo para encontrar documentos em todo o sistema.
      </p>
    </div>

    <search-bar
      :loading="loading"
      :total-results="totalResults"
      :search-performed="searchPerformed"
      @search="performSearch"
      @clear="clearSearch"
    />

    <!-- Header para quando está visualizando uma tag específica -->
    <div v-if="tagId && currentTagInfo" class="current-tag-header q-mb-lg">
      <q-card class="current-tag-card">
        <q-card-section class="row items-center no-wrap">
          <div class="folder-icon q-mr-md">
            <q-icon name="folder" size="42px" color="amber-7" />
          </div>
          <div class="folder-content">
            <div class="text-h5">{{ currentTagInfo.name }}</div>
            <div v-if="currentTagInfo.description" class="text-caption text-grey-8">
              {{ currentTagInfo.description }}
            </div>
            <div class="text-subtitle2 q-mt-xs">
              {{ totalResults }} documento{{ totalResults !== 1 ? 's' : '' }} com esta tag
            </div>
          </div>
        </q-card-section>
      </q-card>
    </div>

    <!-- Filtros renovados: APENAS UM MÉTODO DE FILTROS -->
    <div class="filters-row q-mt-md" v-if="searchPerformed || currentQuery">
      <q-btn-toggle
        v-model="activeFilter"
        spread
        no-caps
        rounded
        unelevated
        toggle-color="accent"
        color="primary"
        text-color="white"
        class="filter-buttons"
        :options="[
          { label: 'Últimos 7 dias', value: 'recent' },
          { label: 'Documentos Word', value: 'docx' },
          { label: 'Alta prioridade', value: 'priority' },
        ]"
      />
    </div>

    <!-- Resultados da busca -->
    <div class="results-container q-mt-md">
      <!-- Loading state -->
      <div v-if="loading" class="text-center q-pa-lg">
        <q-spinner color="primary" size="3em" />
        <div class="q-mt-sm">Buscando documentos...</div>
      </div>

      <!-- Sem resultados -->
      <div
        v-else-if="searchPerformed && results.length === 0 && !tagResults.length"
        class="text-center q-pa-lg"
      >
        <q-icon name="search_off" size="3em" color="grey-7" />
        <div class="q-mt-sm text-grey-8">Nenhum documento encontrado para a sua pesquisa.</div>
        <div class="text-grey-6">Tente termos diferentes ou mais gerais.</div>
      </div>

      <!-- Para debug: mostrar termo de busca atual -->
      <div v-if="currentQuery" class="q-pa-sm bg-blue-1 text-center q-mb-md">
        Termo de busca atual: "{{ currentQuery }}" ({{ totalResults }} documentos encontrados)
      </div>

      <div v-if="searchPerformed && (tagResults.length > 0 || results.length > 0)">
        <!-- Resultados de tags (agora exibidos primeiro) -->
        <div v-if="tagResults.length > 0" class="tag-folders q-mb-md">
          <div class="row q-col-gutter-md">
            <div
              v-for="tagResult in tagResults"
              :key="tagResult.tag.id"
              class="col-12 col-sm-6 col-md-4 col-lg-3"
            >
              <q-card
                class="tag-folder-card cursor-pointer"
                @click="openTagModal(tagResult)"
                v-ripple
              >
                <q-card-section class="tag-folder-section">
                  <div class="folder-icon q-mr-sm">
                    <q-icon name="folder" size="32px" color="amber-7" />
                  </div>
                  <div class="folder-content">
                    <div class="text-subtitle1 text-weight-bold">{{ tagResult.tag.name }}</div>
                    <div class="text-caption text-grey-8">
                      {{ tagResult.document_count }} documentos
                    </div>
                    <div
                      v-if="tagResult.tag.description"
                      class="text-caption text-grey-7 description-ellipsis"
                    >
                      {{ tagResult.tag.description }}
                    </div>
                  </div>
                </q-card-section>
              </q-card>
            </div>
          </div>
        </div>

        <!-- Grid de resultados de documentos -->
        <div v-if="results.length > 0">
          <div class="row q-col-gutter-md">
            <div
              v-for="result in results"
              :key="result.id"
              class="col-12 col-sm-6 col-md-4 col-lg-3"
            >
              <q-card class="document-card cursor-pointer" @click="openDocument(result)" v-ripple>
                <q-card-section class="text-center">
                  <q-icon
                    :name="getDocumentIcon(result.extension)"
                    size="50px"
                    :color="getDocumentColor(result.extension)"
                  />
                </q-card-section>

                <q-card-section>
                  <div class="text-h6 ellipsis">{{ result.filename }}</div>

                  <!-- Tags do documento -->
                  <div v-if="result.tags && result.tags.length > 0" class="document-tags q-mb-xs">
                    <tag-badge
                      v-for="tag in result.tags"
                      :key="tag.id"
                      :tag="tag"
                      class="q-mr-xs q-mb-xs"
                      @click.stop="searchByTag(tag.id)"
                    />
                  </div>

                  <!-- Trechos destacados -->
                  <div
                    v-if="result.highlights && result.highlights.length > 0"
                    class="search-highlight text-caption q-mt-xs text-grey-8 ellipsis-3-lines"
                  >
                    <span v-html="formatHighlights(result.highlights)"></span>
                  </div>

                  <div class="text-caption text-grey">
                    Modificado: {{ formatDate(result.last_modified) }}
                  </div>
                </q-card-section>

                <q-card-actions align="right">
                  <q-btn
                    icon="download"
                    flat
                    round
                    dense
                    color="primary"
                    @click.stop="downloadDocument(result)"
                  >
                    <q-tooltip>Baixar documento</q-tooltip>
                  </q-btn>
                </q-card-actions>
              </q-card>
            </div>
          </div>

          <!-- Paginação -->
          <div class="text-center q-pa-md">
            <q-pagination
              v-if="totalPages > 1"
              v-model="currentPage"
              :max="totalPages"
              direction-links
              boundary-links
              @update:model-value="changePage"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- Modal para visualizar o documento -->
    <document-modal
      v-model="modalOpen"
      :document="selectedDocument"
      :loading="documentLoading"
      :search-term="currentQuery"
      @tag-added="handleTagAdded"
      @tag-removed="handleTagRemoved"
    />

    <!-- Modal de documentos da tag -->
    <q-dialog v-model="tagModalOpen" maxWidth="900px">
      <q-card class="tag-documents-modal">
        <q-card-section class="row items-center">
          <q-avatar color="amber-7" text-color="white" icon="folder" />
          <div class="text-h6 q-ml-sm">{{ selectedTag ? selectedTag.tag.name : '' }}</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>

        <q-separator />

        <q-card-section>
          <div v-if="selectedTag && selectedTag.tag.description" class="text-subtitle2 q-mb-md">
            {{ selectedTag.tag.description }}
          </div>

          <div class="text-subtitle1 q-mb-sm">
            <q-icon name="description" class="q-mr-xs" /> Documentos nesta tag:
          </div>

          <div
            v-if="selectedTag && selectedTag.document_count === 0"
            class="text-grey-8 q-pa-md text-center"
          >
            Nenhum documento encontrado com esta tag.
          </div>

          <div v-else class="row q-col-gutter-md">
            <div v-for="doc in tagDocuments" :key="doc.id" class="col-12">
              <q-item
                clickable
                @click="openDocument(doc)"
                v-ripple
                class="bg-grey-2 rounded-borders"
              >
                <q-item-section avatar>
                  <q-icon
                    :name="getDocumentIcon(doc.filename)"
                    :color="getDocumentColor(doc.filename)"
                  />
                </q-item-section>

                <q-item-section>
                  <q-item-label>{{ doc.filename }}</q-item-label>
                  <q-item-label caption>
                    Modificado: {{ formatDate(doc.last_modified) }}
                  </q-item-label>
                </q-item-section>

                <q-item-section side>
                  <q-btn flat round icon="open_in_new" size="sm" color="primary">
                    <q-tooltip>Abrir documento</q-tooltip>
                  </q-btn>
                </q-item-section>
              </q-item>
            </div>
          </div>
        </q-card-section>
      </q-card>
    </q-dialog>
  </q-page>
</template>

Aqui está a parte do script (script) do componente SearchResults.vue: ```vue
<script>
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { date, useQuasar } from 'quasar'
import SearchBar from 'components/SearchBar.vue'
import DocumentModal from 'components/DocumentModal.vue'
import TagBadge from 'components/TagBadge.vue'
import axios from 'axios'

// API URL
const API_URL = 'http://localhost:5000'

export default {
  name: 'SearchResults',
  components: {
    SearchBar,
    DocumentModal,
    TagBadge,
  },
  props: {
    filter: {
      type: String,
      default: null,
    },
    type: {
      type: String,
      default: null,
    },
    timeframe: {
      type: String,
      default: null,
    },
    tagId: {
      type: String,
      default: null,
    },
  },
  setup(props) {
    const $q = useQuasar()
    const route = useRoute()
    const router = useRouter()

    // Variáveis reativas
    const searchPerformed = ref(false)
    const loading = ref(false)
    const results = ref([])
    const totalResults = ref(0)
    const currentPage = ref(1)
    const pageSize = ref(12) // Aumentado para mostrar mais cards por página
    const totalPages = ref(0)
    const currentQuery = ref('')
    const tagResults = ref([])
    const activeFilter = ref(null) // Para os filtros em forma de botões

    // Para armazenar informações da tag atual quando visualizando por tag
    const currentTagInfo = ref(null)

    // Variáveis para o modal de documento
    const modalOpen = ref(false)
    const selectedDocument = ref(null)
    const documentLoading = ref(false)

    // Variáveis para o modal de tag
    const tagModalOpen = ref(false)
    const selectedTag = ref(null)
    const tagDocuments = ref([])

    // Debugging: observar quando o modal é aberto
    watch(
      () => modalOpen.value,
      (isOpen) => {
        if (isOpen) {
          console.log('Modal aberto com termo de busca:', currentQuery.value)
        }
      },
    )

    // Observar mudanças no filtro ativo
    watch(
      () => activeFilter.value,
      (filter) => {
        if (filter && currentQuery.value) {
          applyFilter(filter)
        }
      },
    )

    // Funções para formatação
    function formatDate(dateString) {
      if (!dateString) return 'Data desconhecida'
      return date.formatDate(dateString, 'DD/MM/YYYY HH:mm')
    }

    function formatFileSize(size) {
      if (!size) return ''

      const units = ['B', 'KB', 'MB', 'GB']
      let fileSize = size
      let unitIndex = 0

      while (fileSize >= 1024 && unitIndex < units.length - 1) {
        fileSize /= 1024
        unitIndex++
      }

      return `${fileSize.toFixed(1)} ${units[unitIndex]}`
    }

    function getDocumentIcon(extension) {
      if (!extension) return 'insert_drive_file'

      const ext =
        typeof extension === 'string'
          ? extension.toLowerCase()
          : typeof extension === 'object' && extension.filename
            ? extension.filename.split('.').pop().toLowerCase()
            : 'unknown'

      const icons = {
        doc: 'mdi-file-word',
        docx: 'mdi-file-word',
        pdf: 'mdi-file-pdf',
        txt: 'mdi-file-document',
        default: 'insert_drive_file',
      }
      return icons[ext] || icons.default
    }

    function getDocumentColor(extension) {
      if (!extension) return 'grey-7'

      const ext =
        typeof extension === 'string'
          ? extension.toLowerCase()
          : typeof extension === 'object' && extension.filename
            ? extension.filename.split('.').pop().toLowerCase()
            : 'unknown'

      const colors = {
        doc: 'blue',
        docx: 'blue',
        pdf: 'red',
        txt: 'grey',
        default: 'grey-7',
      }
      return colors[ext] || colors.default
    }

    function formatHighlights(highlights) {
      if (!highlights || highlights.length === 0) return ''

      // Limitar para 2 trechos para não sobrecarregar os cards
      return highlights.slice(0, 2).join('... ')
    }

    // Função para buscar informações da tag
    async function fetchTagInfo(tagId) {
      try {
        const response = await axios.get(`${API_URL}/api/tags/${tagId}`)
        currentTagInfo.value = response.data
      } catch (error) {
        console.error('Erro ao buscar informações da tag:', error)
        currentTagInfo.value = null
      }
    }

    // Pesquisar por tag específica
    function searchByTag(tagId) {
      router.push({
        path: `/tags/${tagId}`,
      })
    }

    // Abrir modal da tag
    async function openTagModal(tagResult) {
      selectedTag.value = tagResult
      tagModalOpen.value = true

      // Carregar documentos da tag
      await loadTagDocuments(tagResult.tag.id)
    }

    // Carregar documentos da tag
    async function loadTagDocuments(tagId) {
      try {
        const response = await axios.get(`${API_URL}/api/tags/${tagId}/documents`)
        tagDocuments.value = response.data
      } catch (error) {
        console.error('Erro ao carregar documentos da tag:', error)
        tagDocuments.value = []
      }
    }

    // Função para salvar busca no histórico
    function saveToHistory(query, resultCount) {
      // Carregar histórico existente
      let history = localStorage.getItem('searchHistory')
      history = history ? JSON.parse(history) : []

      // Adicionar busca atual ao histórico
      const searchItem = {
        query,
        timestamp: date.formatDate(new Date(), 'DD/MM/YYYY HH:mm'),
        results: resultCount,
      }

      // Verificar se essa busca já existe (evitar duplicatas)
      const existingIndex = history.findIndex((item) => item.query === query)
      if (existingIndex !== -1) {
        // Atualizar busca existente
        history.splice(existingIndex, 1)
      }

      // Adicionar ao início da lista
      history.unshift(searchItem)

      // Limitar a 20 itens no histórico
      if (history.length > 20) {
        history = history.slice(0, 20)
      }

      // Salvar no localStorage
      localStorage.setItem('searchHistory', JSON.stringify(history))
    }

    // Aplicar filtro selecionado
    function applyFilter(filter) {
      console.log('Aplicando filtro:', filter)
      let filterParams = {}

      switch (filter) {
        case 'recent':
          filterParams = { timeframe: '7days' }
          break
        case 'docx':
          filterParams = { type: 'docx' }
          break
        case 'priority':
          filterParams = { priority: 'high' }
          break
      }

      // Refazer a busca com os parâmetros do filtro
      performSearch(currentQuery.value, filterParams)
    }

    // Funções para busca
    async function performSearch(query, additionalParams = {}) {
      if (!query.trim()) return

      console.log('Função performSearch chamada com query:', query)
      loading.value = true
      currentQuery.value = query
      currentPage.value = 1

      try {
        console.log('Iniciando busca por:', query)

        // Ajustar URL da busca conforme filtros
        let apiUrl = `${API_URL}/api/search?q=${encodeURIComponent(query)}&page=${currentPage.value}&size=${pageSize.value}`

        // Adicionar filtros específicos à URL
        if (additionalParams.timeframe || props.timeframe) {
          apiUrl += `&timeframe=${additionalParams.timeframe || props.timeframe}`
        }

        if (additionalParams.type || props.type) {
          apiUrl += `&type=${additionalParams.type || props.type}`
        }

        if (additionalParams.priority || props.filter === 'favorites') {
          apiUrl += `&priority=${additionalParams.priority || 'favorites'}`
        }

        if (props.tagId) {
          apiUrl += `&tag_id=${props.tagId}`
        }

        console.log('Chamando API com URL:', apiUrl)
        const response = await fetch(apiUrl)
        const data = await response.json()

        results.value = data.results || []
        totalResults.value = data.total || 0
        totalPages.value = data.pages || 0
        tagResults.value = data.tag_results || []
        searchPerformed.value = true

        console.log(`Busca concluída: ${results.value.length} resultados de ${totalResults.value}`)
        console.log(`Tags encontradas: ${tagResults.value.length}`)

        // Salvar busca no histórico
        saveToHistory(query, totalResults.value)

        // Atualizar URL com parâmetro de busca
        router.replace({
          query: {
            q: query,
            page: currentPage.value,
            ...additionalParams,
          },
        })
      } catch (error) {
        console.error('Erro ao buscar:', error)
        $q.notify({
          color: 'negative',
          message: 'Erro ao realizar a busca. Tente novamente.',
          icon: 'error',
        })
        results.value = []
        totalResults.value = 0
        tagResults.value = []
      } finally {
        loading.value = false
      }
    }

    // Função para buscar documentos por tag
    async function searchDocumentsByTag() {
      if (!props.tagId) return

      loading.value = true
      try {
        // Buscar informações da tag
        await fetchTagInfo(props.tagId)

        const response = await fetch(`${API_URL}/api/tags/${props.tagId}/documents`)
        const data = await response.json()

        results.value = data.map((doc) => ({
          ...doc,
          extension: doc.filename.split('.').pop().toLowerCase(),
        }))
        totalResults.value = results.value.length
        searchPerformed.value = true

        // Se não temos informações da tag, buscar pelo ID
        if (currentTagInfo.value && currentTagInfo.value.name) {
          currentQuery.value = `Tag: ${currentTagInfo.value.name}`
        }
      } catch (error) {
        console.error('Erro ao buscar documentos por tag:', error)
        $q.notify({
          color: 'negative',
          message: 'Erro ao carregar documentos da tag',
          icon: 'error',
        })
        results.value = []
        totalResults.value = 0
      } finally {
        loading.value = false
      }
    }

    function changePage(page) {
      if (currentQuery.value) {
        currentPage.value = page
        performSearch(currentQuery.value)
      }
    }

    function clearSearch() {
      results.value = []
      totalResults.value = 0
      searchPerformed.value = false
      currentQuery.value = ''
      currentPage.value = 1
      tagResults.value = []
      activeFilter.value = null
      router.replace({ query: {} })
    }

    // Funções para lidar com eventos de tags
    function handleTagAdded({ documentId, tag }) {
      console.log(`Tag ${tag.name} adicionada ao documento ${documentId}`)

      // Encontrar o documento nos resultados e adicionar a tag
      const docIndex = results.value.findIndex(
        (doc) => doc.id === documentId || doc.filename === documentId,
      )
      if (docIndex !== -1) {
        // Se o documento não tem tags, inicializar com array vazio
        if (!results.value[docIndex].tags) {
          results.value[docIndex].tags = []
        }

        // Verificar se a tag já existe para evitar duplicatas
        const tagExists = results.value[docIndex].tags.some((t) => t.id === tag.id)
        if (!tagExists) {
          results.value[docIndex].tags.push(tag)
        }
      }
    }

    function handleTagRemoved({ documentId, tagId }) {
      console.log(`Tag ${tagId} removida do documento ${documentId}`)

      // Encontrar o documento nos resultados e remover a tag
      const docIndex = results.value.findIndex(
        (doc) => doc.id === documentId || doc.filename === documentId,
      )
      if (docIndex !== -1 && results.value[docIndex].tags) {
        results.value[docIndex].tags = results.value[docIndex].tags.filter(
          (tag) => tag.id !== tagId,
        )
      }
    }

    // Funções para lidar com documentos
    async function openDocument(document) {
      console.log('Abrindo documento com termo atual:', currentQuery.value)

      selectedDocument.value = {
        id: document.id || document.filename,
        name: document.filename,
        type: document.extension,
        path: `${API_URL}/download/${encodeURIComponent(document.filename)}`,
      }
      modalOpen.value = true
      documentLoading.value = true

      try {
        const response = await fetch(
          `${API_URL}/api/file-content/${encodeURIComponent(document.filename)}`,
        )
        const data = await response.json()

        if (data.content) {
          console.log('Conteúdo carregado, tamanho:', data.content.length)
          selectedDocument.value.content = data.content

          // Se houver tags no documento, vamos incluí-las
          if (data.tags) {
            selectedDocument.value.tags = data.tags
          }
        }
      } catch (error) {
        console.error('Erro ao carregar conteúdo:', error)
        $q.notify({
          color: 'negative',
          message: 'Erro ao carregar o conteúdo do documento',
          icon: 'error',
        })
      } finally {
        documentLoading.value = false
      }
    }

    function downloadDocument(document) {
      const downloadUrl = `${API_URL}/download/${encodeURIComponent(document.filename)}`

      // Abrir o URL em uma nova aba ou iniciar o download
      const link = document.createElement('a')
      link.href = downloadUrl
      link.target = '_blank' // Para abrir em nova aba (opcional)
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)

      $q.notify({
        color: 'positive',
        message: 'Download iniciado!',
        icon: 'download',
      })
    }

    // Verificar se há parâmetros de busca na URL ao carregar
    onMounted(() => {
      const queryParam = route.query.q
      const pageParam = route.query.page ? parseInt(route.query.page) : 1

      if (props.tagId) {
        // Se estiver visualizando por tag, buscar documentos dessa tag
        searchDocumentsByTag()
      } else if (queryParam) {
        console.log('Termo de busca encontrado na URL:', queryParam)
        currentQuery.value = queryParam
        currentPage.value = pageParam

        // Verificar se há algum filtro ativo na URL
        if (route.query.timeframe) {
          activeFilter.value = 'recent'
        } else if (route.query.type === 'docx') {
          activeFilter.value = 'docx'
        } else if (route.query.priority === 'high') {
          activeFilter.value = 'priority'
        }

        performSearch(queryParam)
      }
    })

    // Observar mudanças na tagId
    watch(
      () => props.tagId,
      (newTagId) => {
        if (newTagId) {
          fetchTagInfo(newTagId)
          searchDocumentsByTag()
        } else {
          currentTagInfo.value = null
        }
      },
    )

    return {
      searchPerformed,
      loading,
      results,
      totalResults,
      currentPage,
      totalPages,
      modalOpen,
      selectedDocument,
      documentLoading,
      currentQuery,
      tagResults,
      currentTagInfo,
      tagModalOpen,
      selectedTag,
      tagDocuments,
      activeFilter,
      performSearch,
      applyFilter,
      clearSearch,
      changePage,
      openDocument,
      downloadDocument,
      searchByTag,
      fetchTagInfo,
      openTagModal,
      loadTagDocuments,
      handleTagAdded,
      handleTagRemoved,
      formatDate,
      formatFileSize,
      formatHighlights,
      getDocumentIcon,
      getDocumentColor,
    }
  },
}
</script>

<style lang="scss" scoped>
// Definir variáveis localmente
$primary: #0a192f;
$secondary: #2c3e50;
$accent: #00a0b0;
$background: #0d1117;
$border-color: #30363d;
$info: #00838f;

.results-container {
  max-width: 1200px;
  margin: 0 auto;
}

.document-card,
.tag-folder-card {
  transition: transform 0.3s ease;
  height: 100%;

  &:hover {
    transform: scale(1.03);
  }
}

.tag-folder-card {
  background-color: lighten($background, 2%);
  border-left: 4px solid $info;
  background-color: rgba(0, 131, 143, 0.1);
}

.tag-folder-section {
  display: flex;
  align-items: flex-start;
  padding: 12px;
}

.folder-icon {
  display: flex;
  align-items: center;
  justify-content: center;
}

.folder-content {
  flex: 1;
}

.description-ellipsis {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
}

.document-tags {
  display: flex;
  flex-wrap: wrap;
}

.search-highlight {
  :deep(mark) {
    background-color: rgba(0, 160, 176, 0.25);
    padding: 0 2px;
    border-radius: 2px;
  }
}

.ellipsis-3-lines {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

.current-tag-header {
  margin-top: 1rem;
}

.current-tag-card {
  background-color: lighten($background, 2%);
  border-left: 4px solid #ffb300;
}

.tag-documents-modal {
  width: 800px;
  max-width: 90vw;
  max-height: 80vh;
}

.filters-row {
  display: flex;
  justify-content: center;
  max-width: 1200px;
  margin: 0 auto 16px auto;

  .filter-buttons {
    border-radius: 24px;
    overflow: hidden;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);

    :deep(.q-btn) {
      border-radius: 0;
      padding: 10px 16px;
    }

    :deep(.q-btn:first-child) {
      border-top-left-radius: 24px;
      border-bottom-left-radius: 24px;
    }

    :deep(.q-btn:last-child) {
      border-top-right-radius: 24px;
      border-bottom-right-radius: 24px;
    }
  }
}
</style>

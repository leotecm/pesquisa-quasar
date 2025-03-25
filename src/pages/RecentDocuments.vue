<template>
  <q-page padding class="recent-documents-page">
    <!-- Cabeçalho da página -->
    <div class="row items-center justify-between q-mb-md">
      <h4 class="text-h4 q-mb-none">
        <q-icon name="history" size="32px" color="accent" class="q-mr-sm" />
        Documentos Recentes
      </h4>
      <q-btn color="negative" icon="delete" label="Limpar Histórico" @click="confirmClear" />
    </div>

    <!-- Loading state -->
    <div v-if="loading" class="text-center q-pa-lg">
      <q-spinner color="primary" size="3em" />
      <div class="q-mt-sm">Carregando documentos recentes...</div>
    </div>

    <!-- Sem documentos -->
    <div v-else-if="!loading && documents.length === 0" class="text-center q-pa-lg">
      <q-icon name="folder_open" size="3em" color="grey-7" />
      <div class="q-mt-sm text-grey-8">Nenhum documento visualizado recentemente.</div>
    </div>

    <!-- Grid de documentos -->
    <div v-else class="row q-col-gutter-md">
      <div
        v-for="document in documents"
        :key="document.id"
        class="col-12 col-sm-6 col-md-4 col-lg-3"
      >
        <q-card class="document-card cursor-pointer" @click="openDocument(document)" v-ripple>
          <q-card-section class="text-center">
            <q-icon
              :name="getDocumentIcon(document.extension || document.filename)"
              size="50px"
              :color="getDocumentColor(document.extension || document.filename)"
            />
          </q-card-section>

          <q-card-section>
            <div class="text-h6 ellipsis">{{ document.filename }}</div>

            <!-- Vínculos do documento -->
            <div v-if="document.tags && document.tags.length > 0" class="document-vinculos q-mb-xs">
              <tag-badge
                v-for="tag in document.tags"
                :key="tag.id"
                :tag="tag"
                class="q-mr-xs q-mb-xs"
              />
            </div>

            <div class="text-caption text-grey">
              Último acesso: {{ formatDate(document.last_accessed) }}
            </div>
          </q-card-section>

          <q-card-actions align="right">
            <q-btn
              icon="download"
              flat
              round
              dense
              color="primary"
              @click.stop="downloadDocument(document)"
            >
              <q-tooltip>Baixar documento</q-tooltip>
            </q-btn>
            <q-btn
              v-if="document"
              icon="link"
              flat
              round
              dense
              class="q-mr-xs"
              @click.stop="showTagManager = true"
              color="accent"
            >
              <q-tooltip>Gerenciar vínculos</q-tooltip>
            </q-btn>
          </q-card-actions>
        </q-card>
      </div>
    </div>

    <!-- Modal para visualizar o documento -->
    <document-modal
      v-model="modalOpen"
      :document="selectedDocument"
      :loading="documentLoading"
      @tag-added="handleTagAdded"
      @tag-removed="handleTagRemoved"
    />

    <q-dialog v-model="showConfirmDialog" persistent>
      <q-card>
        <q-card-section class="row items-center">
          <q-avatar icon="warning" color="negative" text-color="white" />
          <span class="q-ml-sm"
            >Tem certeza que deseja limpar o histórico de documentos recentes?</span
          >
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancelar" color="primary" v-close-popup />
          <q-btn flat label="Confirmar" color="negative" @click="clearHistory" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import axios from 'axios'
import TagBadge from '../components/TagBadge.vue'
import DocumentModal from '../components/DocumentModal.vue'
import { getRecentDocuments, clearRecentDocuments } from 'src/services/documentService'

export default {
  name: 'RecentDocuments',
  components: {
    TagBadge,
    DocumentModal,
  },
  setup() {
    const $q = useQuasar()
    console.log('Objeto $q:', $q)
    console.log('Objeto $q.date:', $q.date)

    const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000'

    // Variáveis reativas
    const loading = ref(true)
    const documents = ref([])
    const modalOpen = ref(false)
    const selectedDocument = ref(null)
    const documentLoading = ref(false)
    const showTagManager = ref(false)
    const showConfirmDialog = ref(false)

    // Funções para formatação
    function formatDate(dateString) {
      if (!dateString) return 'Data desconhecida'
      try {
        const date = new Date(dateString)
        return date.toLocaleString('pt-BR', {
          day: '2-digit',
          month: '2-digit',
          year: 'numeric',
          hour: '2-digit',
          minute: '2-digit',
        })
      } catch (error) {
        console.error('Erro ao formatar data:', error)
        return 'Data desconhecida'
      }
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

    // Carregar documentos recentes
    async function loadRecentDocuments() {
      loading.value = true
      try {
        console.log('Carregando documentos recentes...')
        const response = await getRecentDocuments()
        console.log('Resposta da API:', response)
        // Filtrar apenas documentos que têm last_accessed
        documents.value = response.filter((doc) => doc.last_accessed)
      } catch (error) {
        console.error('Erro ao carregar documentos recentes:', error)
        documents.value = []
        $q.notify({
          type: 'negative',
          message: 'Erro ao carregar documentos recentes',
          timeout: 5000,
        })
      } finally {
        loading.value = false
      }
    }

    // Funções para lidar com documentos
    async function openDocument(document) {
      selectedDocument.value = {
        id: document.id || document.filename,
        name: document.filename,
        type: document.extension,
        path: `${API_URL}/download/${encodeURIComponent(document.filename)}`,
      }
      modalOpen.value = true
      documentLoading.value = true

      try {
        // Registrar o acesso ao documento
        await axios.post(`${API_URL}/api/documents/access`, {
          filename: document.filename,
          timestamp: new Date().toISOString(),
        })

        const response = await axios.get(
          `${API_URL}/api/file-content/${encodeURIComponent(document.filename)}`,
          {
            headers: { Accept: 'application/json' },
          },
        )

        if (response.data.content) {
          selectedDocument.value.content = response.data.content
          if (response.data.tags) {
            selectedDocument.value.tags = response.data.tags
          }
          // Recarregar a lista após abrir o documento
          await loadRecentDocuments()
        }
      } catch (error) {
        console.error('Erro ao carregar conteúdo:', error)
        $q.notify({
          type: 'negative',
          message: 'Erro ao carregar o conteúdo do documento',
          timeout: 5000,
        })
      } finally {
        documentLoading.value = false
      }
    }

    async function downloadDocument(document) {
      try {
        window.open(`${API_URL}/download/${encodeURIComponent(document.filename)}`, '_blank')
        $q.notify({
          type: 'positive',
          message: 'Download iniciado',
          timeout: 2000,
        })
      } catch (error) {
        console.error('Erro ao baixar documento:', error)
        $q.notify({
          type: 'negative',
          message: 'Erro ao baixar o documento',
          timeout: 5000,
        })
      }
    }

    // Handlers para tags
    function handleTagAdded({ documentId, tag }) {
      const doc = documents.value.find((d) => d.id === documentId || d.filename === documentId)
      if (doc) {
        if (!doc.tags) doc.tags = []
        if (!doc.tags.some((t) => t.id === tag.id)) {
          doc.tags.push(tag)
        }
      }
    }

    function handleTagRemoved({ documentId, tagId }) {
      const doc = documents.value.find((d) => d.id === documentId || d.filename === documentId)
      if (doc && doc.tags) {
        doc.tags = doc.tags.filter((t) => t.id !== tagId)
      }
    }

    const confirmClear = () => {
      showConfirmDialog.value = true
    }

    const clearHistory = async () => {
      try {
        loading.value = true
        await clearRecentDocuments()
        $q.notify({
          color: 'positive',
          message: 'Histórico limpo com sucesso',
        })
        showConfirmDialog.value = false
        // Limpar a lista de documentos imediatamente
        documents.value = []
        // Recarregar os documentos
        await loadRecentDocuments()
      } catch (error) {
        $q.notify({
          color: 'negative',
          message: `Erro ao limpar histórico: ${error.message || 'Erro desconhecido'}`,
        })
      } finally {
        loading.value = false
      }
    }

    // Carregar documentos ao montar o componente
    onMounted(() => {
      loadRecentDocuments()
    })

    return {
      loading,
      documents,
      modalOpen,
      selectedDocument,
      documentLoading,
      showTagManager,
      formatDate,
      getDocumentIcon,
      getDocumentColor,
      openDocument,
      downloadDocument,
      handleTagAdded,
      handleTagRemoved,
      showConfirmDialog,
      confirmClear,
      clearHistory,
    }
  },
}
</script>

<style lang="scss" scoped>
.document-card {
  transition: transform 0.3s ease;
  height: 100%;

  &:hover {
    transform: scale(1.03);
  }
}

.document-vinculos {
  display: flex;
  flex-wrap: wrap;
}

.ellipsis {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>

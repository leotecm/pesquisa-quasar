<!-- src/components/TagResults.vue -->
<template>
  <div v-if="tagResults && tagResults.length > 0" class="tag-results q-mb-xl">
    <div class="text-h6 q-mb-md">
      <q-icon name="local_offer" class="q-mr-xs" /> Tags relacionadas à busca
    </div>

    <!-- Tags em estilo de pasta -->
    <div class="row q-col-gutter-md">
      <div
        v-for="tagResult in tagResults"
        :key="tagResult.tag.id"
        class="col-12 col-sm-6 col-md-4 col-lg-3"
      >
        <q-card class="tag-folder-card cursor-pointer" @click="openTagModal(tagResult)" v-ripple>
          <q-card-section class="tag-folder-section">
            <div class="folder-icon q-mr-sm">
              <q-icon name="folder" size="32px" color="amber-7" />
            </div>
            <div class="folder-content">
              <div class="text-subtitle1 text-weight-bold">{{ tagResult.tag.name }}</div>
              <div class="text-caption text-grey-8">{{ tagResult.document_count }} documentos</div>
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
                @click="$emit('open-document', doc)"
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
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { date } from 'quasar'

// API URL
const API_URL = 'http://localhost:5000'

export default {
  name: 'TagResults',
  props: {
    tagResults: {
      type: Array,
      default: () => [],
    },
  },
  emits: ['open-document'],
  setup(_, { emit }) {
    const router = useRouter()
    const tagModalOpen = ref(false)
    const selectedTag = ref(null)
    const tagDocuments = ref([])
    const loadingDocuments = ref(false)

    // Função para calcular cor de contraste
    const getContrastColor = (hexColor) => {
      // Remove o # se existir
      const hex = hexColor.replace('#', '')

      // Converte para RGB
      const r = parseInt(hex.substring(0, 2), 16)
      const g = parseInt(hex.substring(2, 4), 16)
      const b = parseInt(hex.substring(4, 6), 16)

      // Calcula a luminosidade
      const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255

      // Retorna branco ou preto dependendo da luminosidade
      return luminance > 0.5 ? '#000000' : '#FFFFFF'
    }

    // Pesquisar por tag
    const searchByTag = (tagId) => {
      router.push({
        path: '/tags/' + tagId,
      })
    }

    // Abrir modal da tag
    const openTagModal = async (tagResult) => {
      selectedTag.value = tagResult
      tagModalOpen.value = true

      // Carregar documentos da tag
      await loadTagDocuments(tagResult.tag.id)
    }

    // Carregar documentos da tag
    const loadTagDocuments = async (tagId) => {
      loadingDocuments.value = true
      try {
        const response = await axios.get(`${API_URL}/api/tags/${tagId}/documents`)
        tagDocuments.value = response.data
      } catch (error) {
        console.error('Erro ao carregar documentos da tag:', error)
        tagDocuments.value = []
      } finally {
        loadingDocuments.value = false
      }
    }

    // Função para formatar data
    const formatDate = (dateString) => {
      if (!dateString) return 'Data desconhecida'
      return date.formatDate(dateString, 'DD/MM/YYYY HH:mm')
    }

    // Obter ícone para documento baseado na extensão
    const getDocumentIcon = (filename) => {
      if (!filename) return 'insert_drive_file'

      const extension = filename.split('.').pop().toLowerCase()
      const icons = {
        doc: 'mdi-file-word',
        docx: 'mdi-file-word',
        pdf: 'mdi-file-pdf',
        txt: 'mdi-file-document',
      }

      return icons[extension] || 'insert_drive_file'
    }

    // Obter cor para documento baseado na extensão
    const getDocumentColor = (filename) => {
      if (!filename) return 'grey'

      const extension = filename.split('.').pop().toLowerCase()
      const colors = {
        doc: 'blue',
        docx: 'blue',
        pdf: 'red',
        txt: 'grey',
      }

      return colors[extension] || 'grey-7'
    }

    return {
      tagModalOpen,
      selectedTag,
      tagDocuments,
      loadingDocuments,
      getContrastColor,
      searchByTag,
      openTagModal,
      loadTagDocuments,
      formatDate,
      getDocumentIcon,
      getDocumentColor,
      emit,
    }
  },
}
</script>

<style lang="scss" scoped>
.tag-results {
  margin-top: 2rem;
  border-top: 1px solid #e0e0e0;
  padding-top: 1rem;
}

.tag-folder-card {
  transition: all 0.2s ease;
  background-color: #fff8e1; /* Cor bege claro */
  border-left: 4px solid #ffb300; /* Borda lateral amarela */

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  }
}

.tag-folder-section {
  display: flex;
  align-items: flex-start;
  padding: 12px;
}

.folder-icon {
  margin-top: 4px;
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

.tag-documents-modal {
  width: 800px;
  max-width: 90vw;
  max-height: 80vh;
}

.ellipsis {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>

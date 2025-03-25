<template>
  <q-dialog v-model="isOpen" maximized persistent>
    <q-card class="vinculo-documents-modal">
      <q-card-section class="row items-center q-pb-none">
        <div class="text-h6">
          <q-icon name="link" color="accent" class="q-mr-sm" />
          Documentos vinculados a: {{ tag?.name }}
        </div>
        <q-space />
        <q-btn icon="close" flat round dense v-close-popup />
      </q-card-section>

      <q-card-section class="q-pt-md">
        <!-- Loading state -->
        <div v-if="loading" class="text-center q-pa-lg">
          <q-spinner color="primary" size="3em" />
          <div class="q-mt-sm">Carregando documentos vinculados...</div>
        </div>

        <!-- Sem documentos -->
        <div v-else-if="!loading && documents.length === 0" class="text-center q-pa-lg">
          <q-icon name="folder_open" size="3em" color="grey-7" />
          <div class="q-mt-sm text-grey-8">Nenhum documento vinculado encontrado.</div>
        </div>

        <!-- Grid de documentos -->
        <div v-else class="row q-col-gutter-md">
          <div
            v-for="document in documents"
            :key="document.id"
            class="col-12 col-sm-6 col-md-4 col-lg-3"
          >
            <q-card
              class="document-card cursor-pointer"
              @click="$emit('document-clicked', document)"
              v-ripple
            >
              <q-card-section class="text-center">
                <q-icon
                  :name="getDocumentIcon(document.extension || document.filename)"
                  size="50px"
                  :color="getDocumentColor(document.extension || document.filename)"
                />
              </q-card-section>

              <q-card-section>
                <div class="text-h6 ellipsis">{{ document.filename }}</div>
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
              </q-card-actions>
            </q-card>
          </div>
        </div>
      </q-card-section>
    </q-card>
  </q-dialog>
</template>

<script>
import { ref, watch } from 'vue'
import axios from 'axios'

export default {
  name: 'VinculoDocumentsModal',
  props: {
    modelValue: {
      type: Boolean,
      required: true,
    },
    tag: {
      type: Object,
      required: true,
    },
  },
  emits: ['update:modelValue', 'document-clicked'],
  setup(props, { emit }) {
    const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000'
    const loading = ref(false)
    const documents = ref([])
    const isOpen = ref(props.modelValue)

    // Observar mudanças no modelValue
    watch(
      () => props.modelValue,
      (newValue) => {
        isOpen.value = newValue
        if (newValue && props.tag) {
          loadDocuments()
        }
      },
    )

    // Observar mudanças no isOpen
    watch(isOpen, (newValue) => {
      emit('update:modelValue', newValue)
    })

    // Carregar documentos da tag
    async function loadDocuments() {
      if (!props.tag) return

      loading.value = true
      try {
        const response = await axios.get(`${API_URL}/api/tags/${props.tag.id}/documents`)
        documents.value = response.data
      } catch (error) {
        console.error('Erro ao carregar documentos:', error)
        documents.value = []
      } finally {
        loading.value = false
      }
    }

    // Funções auxiliares
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

    async function downloadDocument(document) {
      const downloadUrl = `${API_URL}/download/${encodeURIComponent(document.filename)}`
      window.open(downloadUrl, '_blank')
    }

    return {
      isOpen,
      loading,
      documents,
      formatDate,
      getDocumentIcon,
      getDocumentColor,
      downloadDocument,
    }
  },
}
</script>

<style lang="scss" scoped>
.vinculo-documents-modal {
  .document-card {
    transition: transform 0.3s ease;

    &:hover {
      transform: scale(1.03);
    }
  }
}
</style>

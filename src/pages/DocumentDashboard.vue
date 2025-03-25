<!-- src/pages/DocumentDashboard.vue -->
<template>
  <q-page padding>
    <div class="text-h4 q-mb-md">Meus Documentos</div>

    <!-- Mensagem de erro se houver -->
    <q-banner v-if="error" class="bg-negative text-white q-mb-md">
      {{ error }}
      <template v-slot:action>
        <q-btn flat color="white" label="Tentar novamente" @click="loadDocuments" />
      </template>
    </q-banner>

    <!-- Loading state -->
    <div v-if="loading" class="flex flex-center q-pa-xl">
      <q-spinner color="primary" size="3em" />
      <span class="q-ml-sm">Carregando documentos...</span>
    </div>

    <!-- Mensagem quando não há documentos -->
    <q-banner v-else-if="documents.length === 0 && !error" class="bg-grey-3 q-mb-md">
      Nenhum documento encontrado.
    </q-banner>

    <!-- Grid de documentos -->
    <div v-else class="row q-col-gutter-md">
      <div
        v-for="document in documents"
        :key="document.id"
        class="col-12 col-sm-6 col-md-4 col-lg-3"
      >
        <document-card :document="document" @click="openDocument(document)" />
      </div>
    </div>

    <!-- Modal de documento -->
    <document-modal v-model="modalOpen" :document="selectedDocument" :loading="documentLoading" />
  </q-page>
</template>

<script>
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import DocumentCard from 'components/DocumentCard.vue'
import DocumentModal from 'components/DocumentModal.vue'
import { getDocuments, getDocumentById } from 'src/services/fileService'

export default {
  name: 'DocumentDashboard',
  components: {
    DocumentCard,
    DocumentModal,
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
  },
  setup(props) {
    const documents = ref([])
    const modalOpen = ref(false)
    const selectedDocument = ref(null)
    const loading = ref(false)
    const documentLoading = ref(false)
    const error = ref(null)
    const route = useRoute()

    // Função para carregar documentos
    async function loadDocuments() {
      loading.value = true
      error.value = null

      try {
        // Buscar documentos através do serviço
        documents.value = await getDocuments(props.filter, props.type)
      } catch (err) {
        console.error('Erro ao carregar documentos:', err)
        error.value =
          'Não foi possível carregar os documentos. Verifique se o servidor está em execução.'
      } finally {
        loading.value = false
      }
    }

    // Carregar documentos na montagem do componente
    onMounted(loadDocuments)

    // Observar mudanças nas props para recarregar documentos quando a rota mudar
    watch(() => [props.filter, props.type, route.path], loadDocuments)

    // Função para abrir o documento
    async function openDocument(document) {
      selectedDocument.value = document
      modalOpen.value = true
      documentLoading.value = true

      try {
        // Buscar o conteúdo completo do documento
        const fullDocument = await getDocumentById(document.id)
        if (fullDocument) {
          selectedDocument.value = fullDocument
        }
      } catch (err) {
        console.error('Erro ao carregar conteúdo do documento:', err)
      } finally {
        documentLoading.value = false
      }
    }

    return {
      documents,
      modalOpen,
      selectedDocument,
      loading,
      documentLoading,
      error,
      loadDocuments,
      openDocument,
    }
  },
}
</script>

<!-- src/components/DocumentModal.vue -->
<template>
  <q-dialog
    v-model="isOpen"
    transition-show="fade"
    transition-hide="fade"
    maximized
    persistent
    class="intelligence-document-modal"
  >
    <q-card class="document-modal-card">
      <q-card-section class="row items-center document-modal-header q-pb-none">
        <div class="document-header-left">
          <q-icon
            :name="getDocumentIcon(document ? document.type : 'default')"
            :color="getDocumentColor(document ? document.type : 'default')"
            size="28px"
            class="q-mr-sm"
          />
          <div class="text-h6 ellipsis">{{ document ? document.name : '' }}</div>
        </div>

        <q-space />

        <!-- Indicador de segurança -->
        <div class="security-indicator q-mr-md">
          <q-chip outline color="info" icon="security" size="sm">
            Nível de Segurança: Confidencial
          </q-chip>
        </div>

        <!-- Tags do documento -->
        <div v-if="documentTags.length > 0" class="document-tags q-mr-md">
          <tag-badge
            v-for="tag in documentTags"
            :key="tag.id"
            :tag="tag"
            removable
            @remove="confirmRemoveTag(tag)"
            @click="showTagManager = true"
          />
        </div>

        <!-- Botões de ação -->
        <div class="document-actions">
          <!-- Botão para gerenciar tags -->
          <q-btn
            v-if="document"
            icon="local_offer"
            flat
            round
            dense
            class="q-mr-xs"
            @click="showTagManager = true"
            color="accent"
          >
            <q-tooltip>Gerenciar tags</q-tooltip>
          </q-btn>

          <q-btn
            v-if="document"
            icon="download"
            flat
            round
            dense
            class="q-mr-xs"
            @click="downloadDocument"
            :loading="downloading"
            :disable="loading || downloading"
            color="info"
          >
            <q-tooltip>Download do documento original</q-tooltip>
          </q-btn>

          <q-btn v-if="document" icon="print" flat round dense class="q-mr-xs" color="grey-7">
            <q-tooltip>Imprimir documento</q-tooltip>
          </q-btn>

          <q-btn v-if="document" icon="share" flat round dense class="q-mr-xs" color="grey-7">
            <q-tooltip>Compartilhar documento</q-tooltip>
          </q-btn>

          <!-- Debug: Mostrar termo de busca -->
          <q-badge v-if="searchTerm" color="accent" class="q-mr-md">
            Termo: {{ searchTerm }}
          </q-badge>

          <q-btn icon="close" flat round dense v-close-popup color="grey-7" />
        </div>
      </q-card-section>

      <q-separator class="q-my-sm" dark />

      <!-- Barra de ferramentas do documento -->
      <q-card-section class="document-toolbar q-py-xs">
        <div class="row justify-between items-center">
          <div class="toolbar-left">
            <q-btn flat dense size="sm" icon="zoom_in" color="grey-7">
              <q-tooltip>Aumentar zoom</q-tooltip>
            </q-btn>
            <q-btn flat dense size="sm" icon="zoom_out" color="grey-7">
              <q-tooltip>Diminuir zoom</q-tooltip>
            </q-btn>
            <q-btn flat dense size="sm" icon="fit_screen" color="grey-7">
              <q-tooltip>Ajustar à tela</q-tooltip>
            </q-btn>
          </div>

          <div class="toolbar-center">
            <q-chip outline color="grey-7" size="sm" icon="info">
              {{ document ? formatFileInfo() : '' }}
            </q-chip>
          </div>

          <div class="toolbar-right">
            <q-btn flat dense size="sm" icon="text_format" color="grey-7">
              <q-tooltip>Formatar texto</q-tooltip>
            </q-btn>
            <q-btn flat dense size="sm" icon="translate" color="grey-7">
              <q-tooltip>Traduzir documento</q-tooltip>
            </q-btn>
            <q-btn flat dense size="sm" icon="find_in_page" color="accent">
              <q-tooltip>Buscar no documento</q-tooltip>
            </q-btn>
          </div>
        </div>
      </q-card-section>

      <q-card-section class="document-container" ref="contentRef">
        <!-- Loading state -->
        <div v-if="loading" class="text-center q-py-xl">
          <q-spinner size="50px" color="accent" />
          <div class="q-mt-sm">Carregando documento...</div>
          <div class="q-mt-xs text-caption text-grey">
            Verificando permissões e descriptografando conteúdo...
          </div>
        </div>

        <!-- Conteúdo do documento -->
        <div v-else-if="document && document.content" class="document-content">
          <!-- Conteúdo processado -->
          <div v-html="processedContent"></div>
        </div>

        <!-- Mensagem de erro -->
        <div v-else class="text-center q-py-xl text-negative">
          <q-icon name="error" size="50px" />
          <div class="q-mt-sm">Não foi possível carregar o conteúdo do documento.</div>
          <div class="q-mt-xs text-caption">
            Verifique suas permissões ou tente novamente mais tarde.
          </div>
        </div>
      </q-card-section>
    </q-card>

    <!-- Dialog para gerenciar tags -->
    <q-dialog v-model="showTagManager" persistent>
      <q-card style="width: 700px; max-width: 90vw" class="tag-manager-modal">
        <q-card-section class="row items-center">
          <div class="text-h6">Gerenciar Tags</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>

        <q-separator dark />

        <q-card-section>
          <p class="text-grey-6">
            Organize o documento com tags para uma melhor classificação e recuperação.
          </p>

          <!-- Lista de tags atuais -->
          <div v-if="documentTags.length > 0" class="q-my-md">
            <div class="text-subtitle1 q-mb-sm">Tags atuais:</div>
            <div class="current-tags">
              <tag-badge
                v-for="tag in documentTags"
                :key="tag.id"
                :tag="tag"
                removable
                @remove="confirmRemoveTag(tag)"
              />
            </div>
          </div>
          <div v-else class="q-my-md text-grey-7">Este documento não possui tags.</div>

          <!-- Adicionar tags existentes -->
          <div class="q-my-md">
            <div class="text-subtitle1 q-mb-sm">Adicionar tags existentes:</div>
            <div class="available-tags" v-if="availableTags.length > 0">
              <tag-badge
                v-for="tag in availableTags"
                :key="tag.id"
                :tag="tag"
                :clickable="true"
                @click="handleAddTag(tag)"
              />
            </div>
            <div v-else class="text-grey-7">Não há mais tags disponíveis.</div>
          </div>

          <!-- Criar nova tag -->
          <div class="q-mt-lg">
            <div class="text-subtitle1 q-mb-sm">Criar nova tag:</div>
            <tag-manager :document-id="document?.id" @tag-added="onTagAdded" />
          </div>
        </q-card-section>
      </q-card>
    </q-dialog>

    <!-- Dialog de confirmação para remover tag -->
    <q-dialog v-model="confirmRemoveDialog">
      <q-card class="confirm-dialog">
        <q-card-section class="row items-center">
          <q-avatar icon="warning" color="warning" text-color="white" />
          <span class="q-ml-sm">Remover tag</span>
        </q-card-section>

        <q-card-section>
          <p>Deseja remover a tag "{{ tagToRemove?.name }}" deste documento?</p>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancelar" color="grey-7" v-close-popup />
          <q-btn
            flat
            label="Remover"
            color="negative"
            @click="removeTag(tagToRemove)"
            v-close-popup
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-dialog>
</template>

<script>
import { computed, ref, onMounted, watch } from 'vue'
import TagBadge from './TagBadge.vue'
import TagManager from './TagManager.vue'
import axios from 'axios'

// URL base da API
const API_URL = 'http://localhost:5000'

export default {
  name: 'DocumentModal',
  components: {
    TagBadge,
    TagManager,
  },
  props: {
    modelValue: {
      type: Boolean,
      default: false,
    },
    document: {
      type: Object,
      default: null,
    },
    loading: {
      type: Boolean,
      default: false,
    },
    searchTerm: {
      type: String,
      default: '',
    },
  },
  emits: ['update:modelValue', 'tag-added', 'tag-removed'],
  setup(props, { emit }) {
    const isOpen = computed({
      get: () => props.modelValue,
      set: (value) => emit('update:modelValue', value),
    })
    const downloading = ref(false)
    const contentRef = ref(null)
    const documentTags = ref([])
    const allTags = ref([])
    const showTagManager = ref(false)

    // Para diálogo de confirmação de remoção de tag
    const confirmRemoveDialog = ref(false)
    const tagToRemove = ref(null)

    // Tags disponíveis (não associadas ao documento)
    const availableTags = computed(() => {
      if (!documentTags.value.length) return allTags.value
      const docTagIds = documentTags.value.map((tag) => tag.id)
      return allTags.value.filter((tag) => !docTagIds.includes(tag.id))
    })

    // Função para carregar tags do documento
    const loadDocumentTags = async () => {
      if (!props.document || !props.document.id) return

      try {
        const response = await axios.get(`${API_URL}/api/documents/${props.document.id}/tags`)
        documentTags.value = response.data
      } catch (error) {
        console.error('Erro ao carregar tags do documento:', error)
      }
    }

    // Função para carregar todas as tags
    const loadAllTags = async () => {
      try {
        const response = await axios.get(`${API_URL}/api/tags`)
        allTags.value = response.data
      } catch (error) {
        console.error('Erro ao carregar tags:', error)
      }
    }

    // Adicionar tag ao documento
    const handleAddTag = async (tag) => {
      if (!props.document || !props.document.id) {
        return
      }

      try {
        await axios.post(`${API_URL}/api/documents/${props.document.id}/tags/${tag.id}`)
        documentTags.value.push(tag)

        // Emitir evento para atualizar a visualização principal
        emit('tag-added', {
          documentId: props.document.id,
          tag: tag,
        })
      } catch (error) {
        console.error('Erro ao adicionar tag:', error)
      }
    }

    // Confirmar remoção de tag
    const confirmRemoveTag = (tag) => {
      tagToRemove.value = tag
      confirmRemoveDialog.value = true
    }

    // Remover tag do documento
    const removeTag = async (tag) => {
      if (!props.document || !props.document.id || !tag) return

      try {
        await axios.delete(`${API_URL}/api/documents/${props.document.id}/tags/${tag.id}`)
        documentTags.value = documentTags.value.filter((t) => t.id !== tag.id)

        // Emitir evento para atualizar a visualização principal
        emit('tag-removed', {
          documentId: props.document.id,
          tagId: tag.id,
        })
      } catch (error) {
        console.error('Erro ao remover tag:', error)
      }
    }

    // Quando uma nova tag é adicionada
    const onTagAdded = (tag) => {
      documentTags.value.push(tag)
      loadAllTags() // Recarregar todas as tags

      // Emitir evento para atualizar a visualização principal
      if (props.document && props.document.id) {
        emit('tag-added', {
          documentId: props.document.id,
          tag: tag,
        })
      }
    }

    // Função para destacar texto
    const processedContent = computed(() => {
      if (!props.document?.content) return ''
      if (!props.searchTerm || props.searchTerm.trim() === '') return props.document.content

      // Destacar o termo no conteúdo
      try {
        // Criar uma expressão regular para buscar o termo (insensitive)
        const regex = new RegExp(props.searchTerm.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'gi')

        // Destacar com uma tag de destaque inline
        const highlighted = props.document.content.replace(
          regex,
          '<span class="intelligence-highlight">$&</span>',
        )

        return highlighted
      } catch (e) {
        console.error('Erro ao processar highlights:', e)
        return props.document.content
      }
    })

    // Obter ícone para documento baseado na extensão
    function getDocumentIcon(type) {
      const icons = {
        doc: 'mdi-file-word',
        docx: 'mdi-file-word',
        pdf: 'mdi-file-pdf',
        txt: 'mdi-file-document',
        default: 'mdi-file',
      }
      return icons[type] || icons.default
    }

    // Obter cor para documento baseado na extensão
    function getDocumentColor(type) {
      const colors = {
        doc: 'blue-6',
        docx: 'blue-6',
        pdf: 'red-6',
        txt: 'grey-6',
        default: 'grey-7',
      }
      return colors[type] || colors.default
    }

    // Formatação de informações do arquivo
    function formatFileInfo() {
      if (!props.document) return ''

      const fileType = props.document.type ? props.document.type.toUpperCase() : 'DOC'
      const fileName = props.document.name || 'documento'

      // Simulando tamanho do arquivo
      const fileSize = Math.floor(Math.random() * 1000 + 100) + ' KB'

      // Adicionar fileName no retorno para usar a variável
      return `${fileType} · ${fileSize} · ${fileName.substring(0, 15)}${fileName.length > 15 ? '...' : ''}`
    }

    watch(
      () => props.document,
      (doc) => {
        if (doc) {
          loadDocumentTags()
        }
      },
    )

    watch(isOpen, (open) => {
      if (open) {
        loadAllTags()
        if (props.document) {
          loadDocumentTags()
        }
      }
    })

    function downloadDocument() {
      if (!props.document) return

      downloading.value = true

      try {
        // Usar o endpoint para download do arquivo original
        const downloadUrl = props.document.path

        // Abrir o URL em uma nova aba ou iniciar o download
        const link = document.createElement('a')
        link.href = downloadUrl
        link.target = '_blank' // Para abrir em nova aba (opcional)
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
      } catch (error) {
        console.error('Erro ao iniciar download:', error)
      } finally {
        downloading.value = false
      }
    }

    onMounted(() => {
      console.log('Modal montado')
    })

    return {
      isOpen,
      downloading,
      downloadDocument,
      processedContent,
      contentRef,
      documentTags,
      allTags,
      availableTags,
      showTagManager,
      confirmRemoveDialog,
      tagToRemove,
      loadDocumentTags,
      loadAllTags,
      handleAddTag,
      confirmRemoveTag,
      removeTag,
      onTagAdded,
      getDocumentIcon,
      getDocumentColor,
      formatFileInfo,
    }
  },
}
</script>

<style lang="scss">
@import 'src/css/quasar.variables.scss';

// Estilo global para os destaques
.intelligence-highlight {
  background-color: rgba(0, 160, 176, 0.25);
  color: lighten($accent, 30%);
  padding: 0 2px;
  border-radius: 2px;
  font-weight: 500;
  text-shadow: 0 1px 1px rgba(0, 0, 0, 0.5);
}
</style>

<style lang="scss" scoped>
@import 'src/css/quasar.variables.scss';

.intelligence-document-modal {
  .document-modal-card {
    background-color: lighten($background, 3%);
    border-radius: 6px;
    overflow: hidden;
  }

  .document-modal-header {
    background-color: lighten($primary, 2%);
    padding: 12px 16px;

    .document-header-left {
      display: flex;
      align-items: center;
    }

    .document-actions {
      display: flex;
      align-items: center;
    }
  }

  .document-toolbar {
    background-color: lighten($background, 5%);
    padding: 4px 16px;

    .toolbar-left,
    .toolbar-center,
    .toolbar-right {
      display: flex;
      align-items: center;
      gap: 4px;
    }
  }

  .document-container {
    height: calc(100vh - 160px);
    overflow-y: auto;
    background-color: $background;
    padding: 0;
  }

  .document-content {
    padding: 2cm;
    background: lighten($background, 6%);
    height: 100%;
    overflow-y: auto;
    line-height: 1.6;
    font-size: 12pt;

    :deep(p) {
      margin-bottom: 1em;
    }
  }

  .current-tags,
  .available-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 8px;
  }

  .tag-manager-modal {
    background-color: lighten($background, 3%);
  }

  .confirm-dialog {
    background-color: lighten($background, 3%);
  }
}
</style>

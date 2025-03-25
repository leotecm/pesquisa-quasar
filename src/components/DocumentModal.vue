<!-- src/components/DocumentModal.vue -->
<template>
  <q-dialog
    v-model="isOpen"
    transition-show="fade"
    transition-hide="fade"
    persistent
    class="intelligence-document-modal"
    maximized
  >
    <q-card class="document-modal-card">
      <!-- Botão de fechar no topo direito -->
      <div class="close-button-container">
        <q-btn icon="close" flat class="close-button" v-close-popup />
      </div>

      <!-- Título centralizado -->
      <div class="document-title-container">
        <div class="text-h6 text-center document-title">{{ document ? document.name : '' }}</div>
      </div>

      <!-- Barra de ações centralizada -->
      <div class="document-actions-container">
        <!-- Indicador de segurança -->
        <div class="security-indicator">
          <div class="confidential-stamp">CONFIDENCIAL</div>
        </div>

        <q-space />

        <!-- Tags do documento -->
        <div v-if="documentTags.length > 0" class="document-tags">
          <tag-badge
            v-for="tag in documentTags"
            :key="tag.id"
            :tag="tag"
            removable
            @remove="confirmRemoveTag(tag)"
            @click="showTagManager = true"
          />
        </div>

        <q-space />

        <!-- Botões de ação -->
        <div class="action-buttons">
          <!-- Botão para gerenciar tags -->
          <q-btn
            v-if="document"
            icon="link"
            flat
            round
            dense
            class="q-mr-xs"
            @click="showTagManager = true"
            color="accent"
          >
            <q-tooltip>Gerenciar vínculos</q-tooltip>
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
        </div>
      </div>

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
          <div class="watermark-container">
            <div class="watermark">CORREGEDORIA</div>
          </div>
          <div class="content-wrapper" v-if="document.content">
            <div v-html="processedContent"></div>
          </div>
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

      <q-card-actions align="right">
        <q-btn flat label="Fechar" color="primary" v-close-popup />
      </q-card-actions>
    </q-card>

    <!-- Dialog para gerenciar tags -->
    <q-dialog v-model="showTagManager" persistent>
      <q-card style="width: 700px; max-width: 90vw" class="tag-manager-modal">
        <q-card-section class="row items-center">
          <div class="text-h6">Gerenciar Vínculos</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>

        <q-separator dark />

        <q-card-section>
          <p class="text-grey-6">
            Organize o documento com vínculos para uma melhor classificação e recuperação.
          </p>

          <!-- Lista de tags atuais -->
          <div v-if="documentTags.length > 0" class="q-my-md">
            <div class="text-subtitle1 q-mb-sm">Vínculos atuais:</div>
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
          <div v-else class="q-my-md text-grey-7">Este documento não possui vínculos.</div>

          <!-- Adicionar tags existentes -->
          <div class="q-my-md">
            <div class="text-subtitle1 q-mb-sm">Adicionar vínculos existentes:</div>
            <div class="available-tags" v-if="availableTags.length > 0">
              <tag-badge
                v-for="tag in availableTags"
                :key="tag.id"
                :tag="tag"
                :clickable="true"
                @click="handleAddTag(tag)"
              />
            </div>
            <div v-else class="text-grey-7">Não há mais vínculos disponíveis.</div>
          </div>

          <!-- Criar nova tag -->
          <div class="q-mt-lg">
            <div class="text-subtitle1 q-mb-sm">Criar novo vínculo:</div>
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
          <span class="q-ml-sm">Remover vínculo</span>
        </q-card-section>

        <q-card-section>
          <p>Deseja remover o vínculo "{{ tagToRemove?.name }}" deste documento?</p>
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
import { registerDocumentAccess } from 'src/services/documentService'

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
      required: true,
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

    // Função para destacar texto e formatar parágrafos
    const processedContent = computed(() => {
      if (!props.document?.content) return ''

      // Primeiro, vamos formatar o texto em parágrafos
      let content = props.document.content

      // Dividir em parágrafos nos pontos finais seguidos de espaço e letra maiúscula
      content = content.replace(/\.\s+([A-Z])/g, '.</p><p>$1')

      // Garantir que o conteúdo começa e termina com tags de parágrafo
      if (!content.startsWith('<p>')) {
        content = '<p>' + content
      }
      if (!content.endsWith('</p>')) {
        content = content + '</p>'
      }

      // Se houver um termo de busca, destacá-lo
      if (props.searchTerm && props.searchTerm.trim() !== '') {
        try {
          // Criar uma expressão regular para buscar o termo (insensitive)
          const regex = new RegExp(props.searchTerm.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'gi')

          // Destacar com uma tag de destaque inline
          content = content.replace(regex, '<span class="intelligence-highlight">$&</span>')
        } catch (e) {
          console.error('Erro ao processar highlights:', e)
        }
      }

      return content
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

    // Registrar acesso ao documento quando o modal é aberto
    watch(isOpen, async (newValue) => {
      if (newValue && props.document) {
        try {
          const filename = props.document.name || props.document.filename
          console.log('Modal aberto, registrando acesso ao documento:', filename)
          await registerDocumentAccess(filename)
          console.log('Acesso registrado com sucesso')
        } catch (error) {
          console.error('Erro ao registrar acesso:', error)
        }
      }
    })

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
  background-color: rgb(18, 177, 21); /* Verde sólido */
  color: #000;
  padding: 0 2px;
  border-radius: 2px;
  font-weight: 500;
  text-shadow: none;
}
</style>

<style lang="scss" scoped>
@import 'src/css/quasar.variables.scss';

.intelligence-document-modal {
  .document-modal-card {
    background-color: lighten($background, 3%);
    border-radius: 6px;
    overflow: hidden;
    width: 900px;
    height: 800px;
    max-width: 90vw;
    max-height: 90vh;
    margin: 0 auto;
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
    height: calc(100% - 160px);
    overflow-y: auto;
    background-color: $background;
    padding: 0;
  }

  .document-content {
    padding: 2cm;
    background: lighten($background, 6%);
    height: 100%;
    overflow-y: auto;
    line-height: 1.8;
    font-size: 13pt;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.3);
    border-radius: 4px;
    margin: 0 auto;
    position: relative;
    max-width: 720px; /* Limita a largura do texto para melhor legibilidade */

    &:before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 1px;
      background: rgba(255, 255, 255, 0.1);
    }

    :deep(p) {
      margin-bottom: 1.5em;
      text-align: justify;
      text-indent: 1.5em; /* Recuo de parágrafo */
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

.watermark-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 1;
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  align-items: center;
  opacity: 0.15;
}

.watermark {
  font-size: 78px;
  font-weight: bold;
  color: #000;
  transform: rotate(-45deg);
  white-space: nowrap;
  margin: 20px;
}

.content-wrapper {
  position: relative;
  z-index: 2;
  background-color: transparent;
}

:deep(.highlight) {
  background-color: yellow;
  padding: 2px;
  border-radius: 2px;
}

.search-highlight {
  :deep(mark) {
    background-color: rgb(18, 177, 21); /* Verde sólido */
    padding: 0 2px;
    border-radius: 2px;
  }
}

.document-modal-card {
  position: relative; // Adiciona posicionamento relativo para o container do botão
}

.close-button-container {
  position: absolute;
  top: 8px;
  right: 8px;
  z-index: 1000;
}

.close-button {
  background-color: #ff0000;
  color: white;
  border-radius: 4px;
  width: 36px;
  height: 36px;
  padding: 0;

  &:hover {
    background-color: darken(#ff0000, 10%);
  }
}

.document-title-container {
  padding: 16px;
  background-color: lighten($primary, 2%);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.document-title {
  font-size: 1.2rem;
  font-weight: 500;
  color: white;
  margin: 0;
  padding: 0;
}

.document-actions-container {
  padding: 12px 16px;
  background-color: lighten($primary, 2%);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);

  .security-indicator,
  .document-tags,
  .action-buttons {
    display: flex;
    align-items: center;
    gap: 8px;
  }
}

.security-indicator {
  .confidential-stamp {
    background-color: #ff0000;
    color: white;
    padding: 4px 12px;
    border: 2px solid #ff0000;
    border-radius: 4px;
    font-weight: bold;
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 1px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  }
}
</style>

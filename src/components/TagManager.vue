<!-- src/components/TagManager.vue -->
<template>
  <div class="intelligence-tag-manager">
    <!-- Lista de tags existentes -->
    <div v-if="tags.length > 0" class="tag-list q-mb-md">
      <tag-badge
        v-for="tag in tags"
        :key="tag.id"
        :tag="tag"
        @click="selectTag(tag)"
        class="q-mr-xs q-mb-xs"
      />
    </div>
    <div v-else class="no-tags q-mb-md text-grey-7">
      Nenhuma tag disponível. Crie uma nova tag abaixo.
    </div>

    <!-- Form para adicionar/editar tag -->
    <q-card class="tag-form" flat bordered>
      <q-card-section>
        <div class="text-subtitle1">{{ isEditing ? 'Editar Tag' : 'Criar Nova Tag' }}</div>

        <q-form @submit="saveTag" class="q-mt-md">
          <div class="row q-col-gutter-md">
            <div class="col-12 col-sm-6">
              <q-input
                v-model="formData.name"
                label="Nome da Tag"
                :rules="[(val) => !!val || 'Nome é obrigatório']"
                outlined
                dense
                dark
              />
            </div>
            <div class="col-12 col-sm-6">
              <q-input v-model="formData.color" outlined dense label="Cor" dark>
                <template v-slot:append>
                  <q-icon name="colorize" class="cursor-pointer">
                    <q-popup-proxy>
                      <q-color v-model="formData.color" dark />
                    </q-popup-proxy>
                  </q-icon>
                </template>
                <template v-slot:after>
                  <div class="color-preview" :style="`background-color: ${formData.color}`"></div>
                </template>
              </q-input>
            </div>
          </div>

          <q-input
            v-model="formData.description"
            label="Descrição (opcional)"
            outlined
            dense
            dark
            class="q-mt-sm"
          />

          <div class="row justify-between q-mt-md">
            <q-btn v-if="isEditing" label="Cancelar" color="grey-7" flat @click="cancelEdit" />
            <q-btn v-if="isEditing" label="Excluir" color="negative" flat @click="confirmDelete" />
            <q-space />
            <q-btn
              :label="isEditing ? 'Atualizar' : 'Criar'"
              color="accent"
              type="submit"
              :loading="saving"
            />
          </div>
        </q-form>
      </q-card-section>
    </q-card>

    <!-- Dialog de confirmação para excluir tag -->
    <q-dialog v-model="confirmDeleteDialog">
      <q-card class="confirm-dialog">
        <q-card-section class="row items-center">
          <q-avatar icon="warning" color="negative" text-color="white" />
          <span class="q-ml-sm">
            Tem certeza que deseja excluir a tag "{{ selectedTag?.name }}"?
          </span>
        </q-card-section>
        <q-card-section>
          <p class="text-grey-8">Esta ação irá remover a tag de todos os documentos associados.</p>
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Cancelar" color="grey-7" v-close-popup />
          <q-btn flat label="Excluir" color="negative" @click="deleteTag" v-close-popup />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import TagBadge from './TagBadge.vue'
import axios from 'axios'

// URL base da API
const API_URL = 'http://localhost:5000'

export default {
  name: 'TagManager',
  components: {
    TagBadge,
  },
  props: {
    documentId: {
      type: String,
      default: null,
    },
  },
  emits: ['tag-added', 'tag-updated', 'tag-deleted'],
  setup(props, { emit }) {
    const tags = ref([])
    const saving = ref(false)
    const isEditing = ref(false)
    const selectedTag = ref(null)
    const confirmDeleteDialog = ref(false)

    // Form data
    const formData = reactive({
      name: '',
      color: '#00A0B0', // Cor padrão de acordo com o tema
      description: '',
    })

    // Buscar todas as tags disponíveis
    const fetchTags = async () => {
      try {
        const response = await axios.get(`${API_URL}/api/tags`)
        tags.value = response.data
      } catch (error) {
        console.error('Erro ao buscar tags:', error)
      }
    }

    // Inicializar o componente
    onMounted(fetchTags)

    // Selecionar tag para edição
    const selectTag = (tag) => {
      selectedTag.value = tag
      formData.name = tag.name
      formData.color = tag.color
      formData.description = tag.description
      isEditing.value = true
    }

    // Cancelar edição
    const cancelEdit = () => {
      selectedTag.value = null
      formData.name = ''
      formData.color = '#00A0B0'
      formData.description = ''
      isEditing.value = false
    }

    // Confirmar exclusão
    const confirmDelete = () => {
      confirmDeleteDialog.value = true
    }

    // Salvar tag (criar ou atualizar)
    const saveTag = async () => {
      if (!formData.name) return

      saving.value = true
      try {
        if (isEditing.value && selectedTag.value) {
          // Atualizar tag existente
          const response = await axios.put(`${API_URL}/api/tags/${selectedTag.value.id}`, {
            name: formData.name,
            color: formData.color,
            description: formData.description,
          })

          // Atualizar lista de tags
          const index = tags.value.findIndex((t) => t.id === selectedTag.value.id)
          if (index !== -1) {
            tags.value[index] = response.data
          }

          emit('tag-updated', response.data)
        } else {
          // Criar nova tag
          const response = await axios.post(`${API_URL}/api/tags`, {
            name: formData.name,
            color: formData.color,
            description: formData.description,
          })

          // Adicionar à lista de tags
          tags.value.push(response.data)

          emit('tag-added', response.data)

          // Se tiver um documentId, associar a tag ao documento
          if (props.documentId) {
            await axios.post(
              `${API_URL}/api/documents/${props.documentId}/tags/${response.data.id}`,
            )
          }
        }

        // Limpar form
        cancelEdit()
      } catch (error) {
        console.error('Erro ao salvar tag:', error)
      } finally {
        saving.value = false
      }
    }

    // Excluir tag
    const deleteTag = async () => {
      if (!selectedTag.value) return

      saving.value = true
      try {
        await axios.delete(`${API_URL}/api/tags/${selectedTag.value.id}`)

        // Remover da lista de tags
        tags.value = tags.value.filter((t) => t.id !== selectedTag.value.id)

        emit('tag-deleted', selectedTag.value)

        // Limpar form
        cancelEdit()
      } catch (error) {
        console.error('Erro ao excluir tag:', error)
      } finally {
        saving.value = false
      }
    }

    return {
      tags,
      formData,
      saving,
      isEditing,
      selectedTag,
      confirmDeleteDialog,
      fetchTags,
      selectTag,
      cancelEdit,
      confirmDelete,
      saveTag,
      deleteTag,
    }
  },
}
</script>

<style lang="scss" scoped>
// Definir variáveis localmente em vez de importar
$primary: #0a192f;
$accent: #00a0b0;
$background: #0d1117;
$border-color: #30363d;

.intelligence-tag-manager {
  padding: 0.5rem;

  .tag-list {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 8px;
  }

  .tag-form {
    border-radius: 6px;
    background-color: lighten($background, 3%);
    border: 1px solid $border-color;
  }

  .confirm-dialog {
    background-color: lighten($background, 3%);
  }

  .color-preview {
    width: 24px;
    height: 24px;
    border-radius: 4px;
    margin-left: 8px;
    border: 1px solid rgba(255, 255, 255, 0.2);
  }
}
</style>

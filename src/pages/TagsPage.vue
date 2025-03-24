<!-- src/pages/TagsPage.vue -->
<template>
  <q-page padding class="intelligence-tags-page">
    <div class="intelligence-page-header q-mb-md">
      <div class="row items-center">
        <q-icon name="local_offer" size="32px" color="accent" class="q-mr-md" />
        <div>
          <div class="text-h4">Sistema de Classificação</div>
          <div class="text-subtitle1 text-grey-7">Gerenciamento de Tags</div>
        </div>
        <q-space />
        <q-chip color="info" outline icon="info"> {{ tags.length }} Tags no Sistema </q-chip>
      </div>
      <div class="header-line q-mt-sm"></div>
    </div>

    <!-- Mensagem de loading -->
    <div v-if="loading" class="text-center q-pa-lg">
      <q-spinner color="accent" size="3em" />
      <div class="q-mt-sm">Carregando tags...</div>
    </div>

    <div class="row q-col-gutter-lg">
      <!-- Coluna esquerda: Lista de tags -->
      <div class="col-12 col-md-8">
        <q-card flat bordered class="tags-table-card">
          <q-card-section>
            <div class="intelligence-section-header q-mb-md">
              <div class="text-h6">Tags do Sistema</div>
              <q-chip outline size="sm" color="accent"> {{ tags.length }} tags encontradas </q-chip>
            </div>

            <q-table
              v-if="tags.length > 0"
              :rows="tags"
              :columns="columns"
              row-key="id"
              :pagination="initialPagination"
              :rows-per-page-options="[10, 20, 50, 0]"
              dark
              class="tags-table"
              :loading="loading"
            >
              <!-- Coluna de cor -->
              <template v-slot:body-cell-color="props">
                <q-td :props="props">
                  <q-chip
                    :style="`background-color: ${props.value}; border: 1px solid rgba(255,255,255,0.2);`"
                    dense
                    square
                    class="tag-color-chip"
                  />
                </q-td>
              </template>

              <!-- Coluna de nome -->
              <template v-slot:body-cell-name="props">
                <q-td :props="props">
                  <div class="cursor-pointer tag-name-cell" @click="selectTag(props.row)">
                    {{ props.value }}
                  </div>
                </q-td>
              </template>

              <!-- Coluna de documentos -->
              <template v-slot:body-cell-documentCount="props">
                <q-td :props="props">
                  <q-btn
                    v-if="props.value > 0"
                    flat
                    dense
                    color="accent"
                    :label="props.value"
                    @click="viewDocuments(props.row)"
                  />
                  <span v-else>{{ props.value }}</span>
                </q-td>
              </template>

              <!-- Coluna de ações -->
              <template v-slot:body-cell-actions="props">
                <q-td :props="props" class="q-gutter-xs">
                  <q-btn flat round dense color="info" icon="edit" @click="selectTag(props.row)">
                    <q-tooltip>Editar</q-tooltip>
                  </q-btn>
                  <q-btn
                    flat
                    round
                    dense
                    color="negative"
                    icon="delete"
                    @click="confirmDelete(props.row)"
                  >
                    <q-tooltip>Excluir</q-tooltip>
                  </q-btn>
                </q-td>
              </template>

              <template v-slot:no-data>
                <div class="full-width text-center q-py-lg">
                  <q-icon name="sentiment_dissatisfied" size="2em" color="grey-7" />
                  <div class="q-mt-sm text-grey-7">
                    Nenhuma tag encontrada. Crie uma nova tag ao lado.
                  </div>
                </div>
              </template>
            </q-table>

            <div v-else class="text-center q-pa-lg">
              <q-icon name="local_offer" size="3em" color="grey-7" />
              <div class="q-mt-sm text-grey-7">
                Nenhuma tag encontrada. Crie uma nova tag ao lado.
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>

      <!-- Coluna direita: Formulário -->
      <div class="col-12 col-md-4">
        <q-card flat bordered class="tag-form-card">
          <q-card-section>
            <div class="intelligence-section-header q-mb-md">
              <div class="text-h6">{{ isEditing ? 'Editar Tag' : 'Nova Tag' }}</div>
              <q-chip size="sm" outline :color="isEditing ? 'info' : 'accent'">
                {{ isEditing ? 'Modo Edição' : 'Criação' }}
              </q-chip>
            </div>

            <q-form @submit="saveTag" class="q-mt-md">
              <q-input
                v-model="formData.name"
                label="Nome da Tag"
                dense
                outlined
                dark
                :rules="[(val) => !!val || 'Nome é obrigatório']"
                class="q-mb-md"
              />

              <q-input v-model="formData.color" label="Cor" dense outlined dark class="q-mb-md">
                <template v-slot:append>
                  <q-icon name="colorize" class="cursor-pointer">
                    <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                      <q-color v-model="formData.color" dark />
                    </q-popup-proxy>
                  </q-icon>
                </template>
                <template v-slot:after>
                  <div
                    class="tag-color-preview"
                    :style="`background-color: ${formData.color}`"
                  ></div>
                </template>
              </q-input>

              <q-input
                v-model="formData.description"
                label="Descrição (opcional)"
                dense
                outlined
                dark
                type="textarea"
                rows="3"
                class="q-mb-md"
              />

              <q-card
                v-if="isEditing"
                flat
                bordered
                class="tag-preview q-pa-sm q-mb-md flex items-center justify-center"
              >
                <tag-badge
                  :tag="{
                    name: formData.name,
                    color: formData.color,
                    description: formData.description,
                  }"
                  class="q-mx-auto"
                />
              </q-card>

              <div class="row q-col-gutter-sm">
                <div class="col">
                  <q-btn
                    outline
                    no-caps
                    class="full-width"
                    label="Cancelar"
                    color="grey-7"
                    @click="cancelEdit"
                  />
                </div>
                <div class="col">
                  <q-btn
                    unelevated
                    no-caps
                    class="full-width"
                    type="submit"
                    :label="isEditing ? 'Atualizar' : 'Criar'"
                    :color="isEditing ? 'info' : 'accent'"
                    :loading="saving"
                  />
                </div>
              </div>
            </q-form>
          </q-card-section>
        </q-card>

        <!-- Card de informações úteis -->
        <q-card flat bordered class="tips-card q-mt-md">
          <q-card-section>
            <div class="text-subtitle1">Sobre o Sistema de Tags</div>
            <q-separator dark spaced />
            <p class="text-grey-7 q-my-sm">
              Tags são usadas para organizar e classificar documentos, facilitando a busca e
              recuperação.
            </p>
            <ul class="text-grey-7">
              <li>Crie tags com nomes descritivos</li>
              <li>Use cores diferentes para categorias distintas</li>
              <li>Associe várias tags a um mesmo documento</li>
            </ul>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Dialog de confirmação para exclusão -->
    <q-dialog v-model="confirmDeleteDialog" persistent>
      <q-card class="confirm-dialog">
        <q-card-section class="row items-center">
          <q-avatar icon="warning" color="negative" text-color="white" />
          <span class="q-ml-sm"
            >Tem certeza que deseja excluir a tag "{{ selectedTag?.name }}"?</span
          >
        </q-card-section>

        <q-card-section class="q-pt-none">
          Esta ação removerá a tag de todos os documentos associados.
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancelar" color="grey-7" v-close-popup />
          <q-btn
            flat
            label="Excluir"
            color="negative"
            @click="deleteTag"
            :loading="saving"
            v-close-popup
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import TagBadge from 'components/TagBadge.vue'

// URL base da API
const API_URL = 'http://localhost:5000'

export default {
  name: 'TagsPage',
  components: {
    TagBadge,
  },
  setup() {
    const router = useRouter()
    const tags = ref([])
    const loading = ref(false)
    const saving = ref(false)
    const isEditing = ref(false)
    const selectedTag = ref(null)
    const confirmDeleteDialog = ref(false)

    // Form data
    const formData = reactive({
      name: '',
      color: '#00A0B0',
      description: '',
    })

    // Definição de colunas para a tabela
    const columns = [
      {
        name: 'color',
        label: 'Cor',
        field: 'color',
        align: 'center',
        sortable: false,
        style: 'width: 50px',
      },
      {
        name: 'name',
        label: 'Nome',
        field: 'name',
        align: 'left',
        sortable: true,
      },
      {
        name: 'description',
        label: 'Descrição',
        field: 'description',
        align: 'left',
        sortable: false,
      },
      {
        name: 'documentCount',
        label: 'Documentos',
        field: 'documentCount',
        align: 'center',
        sortable: true,
      },
      {
        name: 'actions',
        label: 'Ações',
        field: 'actions',
        align: 'center',
        sortable: false,
      },
    ]

    // Configuração inicial de paginação
    const initialPagination = {
      rowsPerPage: 10,
    }

    // Carregar todas as tags
    const fetchTags = async () => {
      loading.value = true
      try {
        const response = await axios.get(`${API_URL}/api/tags`)

        // Para cada tag, buscar a contagem de documentos
        const tagsWithCounts = await Promise.all(
          response.data.map(async (tag) => {
            try {
              const docsResponse = await axios.get(`${API_URL}/api/tags/${tag.id}/documents`)
              return {
                ...tag,
                documentCount: docsResponse.data.length || 0,
              }
            } catch (error) {
              console.error(`Erro ao buscar documentos para tag ${tag.id}:`, error)
              return {
                ...tag,
                documentCount: 0,
              }
            }
          }),
        )

        tags.value = tagsWithCounts
      } catch (error) {
        console.error('Erro ao carregar tags:', error)
      } finally {
        loading.value = false
      }
    }

    // Selecionar tag para edição
    const selectTag = (tag) => {
      selectedTag.value = tag
      formData.name = tag.name
      formData.color = tag.color
      formData.description = tag.description || ''
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
    const confirmDelete = (tag) => {
      selectedTag.value = tag
      confirmDeleteDialog.value = true
    }

    // Salvar tag
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

          // Atualizar na lista
          const index = tags.value.findIndex((t) => t.id === selectedTag.value.id)
          if (index !== -1) {
            tags.value[index] = {
              ...response.data,
              documentCount: tags.value[index].documentCount,
            }
          }

          console.log('Tag atualizada com sucesso')
        } else {
          // Criar nova tag
          const response = await axios.post(`${API_URL}/api/tags`, {
            name: formData.name,
            color: formData.color,
            description: formData.description,
          })

          // Adicionar à lista
          tags.value.push({
            ...response.data,
            documentCount: 0,
          })

          console.log('Tag criada com sucesso')
        }

        // Resetar formulário
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

        // Remover da lista
        tags.value = tags.value.filter((t) => t.id !== selectedTag.value.id)

        console.log('Tag excluída com sucesso')

        // Limpar seleção
        cancelEdit()
      } catch (error) {
        console.error('Erro ao excluir tag:', error)
      } finally {
        saving.value = false
      }
    }

    // Ver documentos associados à tag
    const viewDocuments = (tag) => {
      router.push(`/tags/${tag.id}`)
    }

    // Carregar tags ao montar componente
    onMounted(fetchTags)

    return {
      tags,
      columns,
      initialPagination,
      loading,
      saving,
      formData,
      isEditing,
      selectedTag,
      confirmDeleteDialog,
      selectTag,
      cancelEdit,
      saveTag,
      confirmDelete,
      deleteTag,
      viewDocuments,
    }
  },
}
</script>

<style lang="scss" scoped>
@import 'src/css/quasar.variables.scss';

.intelligence-tags-page {
  .intelligence-page-header {
    .header-line {
      height: 1px;
      background: linear-gradient(
        90deg,
        rgba(0, 160, 176, 0.8),
        rgba(0, 160, 176, 0.2),
        rgba(0, 160, 176, 0)
      );
    }
  }

  .intelligence-section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .tags-table-card,
  .tag-form-card,
  .tips-card {
    background-color: lighten($background, 2%);
    border: 1px solid $border-color;
    border-radius: 6px;
  }

  .tags-table {
    border-radius: 6px;

    .tag-name-cell {
      color: white;
      font-weight: 500;
      transition: color 0.2s;

      &:hover {
        color: $accent;
      }
    }
  }

  .tag-color-chip {
    width: 30px;
    height: 20px;
    border-radius: 4px;
  }

  .tag-color-preview {
    width: 36px;
    height: 36px;
    border-radius: 4px;
    border: 1px solid rgba(255, 255, 255, 0.1);
  }

  .tag-preview {
    min-height: 50px;
    background-color: lighten($background, 4%);
    border: 1px solid $border-color;
  }

  .confirm-dialog {
    background-color: lighten($background, 3%);
  }
}
</style>

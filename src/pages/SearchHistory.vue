<!-- src/pages/SearchHistory.vue -->
<template>
  <q-page padding class="intelligence-history-page">
    <div class="intelligence-page-header q-mb-md">
      <div class="row items-center">
        <q-icon name="history" size="32px" color="accent" class="q-mr-md" />
        <div>
          <div class="text-h4">Histórico de Buscas</div>
          <div class="text-subtitle1 text-grey-7">Registro de consultas anteriores</div>
        </div>
        <q-space />
        <q-chip color="info" outline icon="info">
          {{ searchHistory.length }} Consultas Registradas
        </q-chip>
      </div>
      <div class="header-line q-mt-sm"></div>
    </div>

    <div v-if="!searchHistory.length" class="text-center q-mt-xl history-empty">
      <q-icon name="history" size="4em" color="grey-7" />
      <p class="text-subtitle1 q-mt-md">Nenhuma busca realizada ainda.</p>
      <p class="text-caption text-grey-7">
        O histórico de buscas será armazenado automaticamente à medida que você utilizar o sistema.
      </p>
    </div>

    <q-card v-else flat bordered class="history-list-card">
      <q-card-section>
        <div class="intelligence-section-header q-mb-md">
          <div class="text-h6">Consultas Recentes</div>
          <q-btn
            flat
            color="negative"
            icon="delete"
            label="Limpar Histórico"
            @click="confirmClear"
          />
        </div>

        <q-list bordered separator dark class="rounded-borders">
          <q-item
            v-for="(item, index) in searchHistory"
            :key="index"
            clickable
            @click="repeatSearch(item.query)"
            class="history-item"
          >
            <q-item-section avatar>
              <q-avatar color="primary" text-color="white">
                {{ item.query.charAt(0).toUpperCase() }}
              </q-avatar>
            </q-item-section>

            <q-item-section>
              <q-item-label class="search-query">{{ item.query }}</q-item-label>
              <q-item-label caption>
                <div class="row items-center">
                  <q-icon name="schedule" size="xs" class="q-mr-xs" />
                  {{ item.timestamp }}
                  <q-separator vertical inset color="grey-7" class="q-mx-sm" />
                  <q-icon name="article" size="xs" class="q-mr-xs" />
                  {{ item.results }} resultados
                </div>
              </q-item-label>
            </q-item-section>

            <q-item-section side>
              <div class="row items-center">
                <q-btn
                  flat
                  round
                  dense
                  icon="replay"
                  color="accent"
                  @click.stop="repeatSearch(item.query)"
                >
                  <q-tooltip>Repetir esta busca</q-tooltip>
                </q-btn>

                <q-btn
                  flat
                  round
                  dense
                  icon="delete_outline"
                  color="grey-7"
                  @click.stop="removeHistoryItem(index)"
                >
                  <q-tooltip>Remover do histórico</q-tooltip>
                </q-btn>
              </div>
            </q-item-section>
          </q-item>
        </q-list>

        <div class="text-right q-mt-sm">
          <q-badge outline color="grey-7">
            Local Storage: {{ Math.round(getStorageSize() / 1024) }} KB
          </q-badge>
        </div>
      </q-card-section>
    </q-card>

    <!-- Card de análise de buscas -->
    <q-card v-if="searchHistory.length > 3" flat bordered class="analytics-card q-mt-md">
      <q-card-section>
        <div class="intelligence-section-header q-mb-md">
          <div class="text-h6">Análise de Padrões de Busca</div>
          <q-chip outline size="sm" color="info"> Inteligência de Dados </q-chip>
        </div>

        <div class="row q-col-gutter-md">
          <div class="col-12 col-md-4">
            <q-card dark bordered flat class="insight-card">
              <q-card-section>
                <div class="text-subtitle2">Termos Frequentes</div>
                <div class="text-h5 q-mt-sm">{{ getMostFrequentTerm() }}</div>
                <div class="text-caption text-grey-7">Termo mais buscado nas últimas consultas</div>
              </q-card-section>
            </q-card>
          </div>

          <div class="col-12 col-md-4">
            <q-card dark bordered flat class="insight-card">
              <q-card-section>
                <div class="text-subtitle2">Resultados</div>
                <div class="text-h5 q-mt-sm">{{ getAverageResults() }}</div>
                <div class="text-caption text-grey-7">Média de resultados por busca</div>
              </q-card-section>
            </q-card>
          </div>

          <div class="col-12 col-md-4">
            <q-card dark bordered flat class="insight-card">
              <q-card-section>
                <div class="text-subtitle2">Período Ativo</div>
                <div class="text-h5 q-mt-sm">{{ getMostActiveTime() }}</div>
                <div class="text-caption text-grey-7">Horário com maior atividade de busca</div>
              </q-card-section>
            </q-card>
          </div>
        </div>
      </q-card-section>
    </q-card>

    <q-dialog v-model="confirmDialog">
      <q-card class="confirm-dialog">
        <q-card-section class="row items-center">
          <q-avatar icon="delete" color="negative" text-color="white" />
          <span class="q-ml-sm">Limpar histórico de buscas?</span>
        </q-card-section>
        <q-card-section class="q-pt-none">
          <p>Esta ação não pode ser desfeita e removerá todos os registros de buscas anteriores.</p>
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Cancelar" color="grey-7" v-close-popup />
          <q-btn flat label="Limpar" color="negative" @click="clearHistory" v-close-popup />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

export default {
  name: 'SearchHistory',
  setup() {
    const router = useRouter()
    const searchHistory = ref([])
    const confirmDialog = ref(false)

    // Carregar histórico do localStorage
    onMounted(() => {
      loadHistory()
    })

    // Função para carregar o histórico
    const loadHistory = () => {
      const savedHistory = localStorage.getItem('searchHistory')
      if (savedHistory) {
        searchHistory.value = JSON.parse(savedHistory)
      }
    }

    // Repetir uma busca anterior
    function repeatSearch(query) {
      router.push({
        path: '/',
        query: { q: query },
      })
    }

    // Mostrar diálogo de confirmação
    function confirmClear() {
      confirmDialog.value = true
    }

    // Limpar histórico
    function clearHistory() {
      searchHistory.value = []
      localStorage.removeItem('searchHistory')
    }

    // Remover um item específico do histórico
    function removeHistoryItem(index) {
      searchHistory.value.splice(index, 1)
      localStorage.setItem('searchHistory', JSON.stringify(searchHistory.value))
    }

    // Calcular tamanho do armazenamento local
    function getStorageSize() {
      const history = JSON.stringify(searchHistory.value)
      return new Blob([history]).size
    }

    // Funções para análise de busca

    // Obter o termo mais frequente
    function getMostFrequentTerm() {
      if (!searchHistory.value.length) return 'N/A'

      const terms = {}
      searchHistory.value.forEach((item) => {
        const words = item.query.toLowerCase().split(' ')
        words.forEach((word) => {
          if (word.length > 2) {
            // Ignorar preposições e palavras curtas
            terms[word] = (terms[word] || 0) + 1
          }
        })
      })

      let mostFrequent = ''
      let maxCount = 0

      Object.keys(terms).forEach((term) => {
        if (terms[term] > maxCount) {
          mostFrequent = term
          maxCount = terms[term]
        }
      })

      return mostFrequent.charAt(0).toUpperCase() + mostFrequent.slice(1)
    }

    // Calcular média de resultados
    function getAverageResults() {
      if (!searchHistory.value.length) return 'N/A'

      const total = searchHistory.value.reduce((sum, item) => sum + item.results, 0)
      return Math.round(total / searchHistory.value.length)
    }

    // Obter horário com mais buscas
    function getMostActiveTime() {
      if (!searchHistory.value.length) return 'N/A'

      const hours = {}

      searchHistory.value.forEach((item) => {
        const time = item.timestamp.split(' ')[1] // Pega HH:mm do formato DD/MM/YYYY HH:mm
        if (time) {
          const hour = time.split(':')[0]
          hours[hour] = (hours[hour] || 0) + 1
        }
      })

      let mostActiveHour = ''
      let maxCount = 0

      Object.keys(hours).forEach((hour) => {
        if (hours[hour] > maxCount) {
          mostActiveHour = hour
          maxCount = hours[hour]
        }
      })

      return `${mostActiveHour}h`
    }

    return {
      searchHistory,
      confirmDialog,
      repeatSearch,
      confirmClear,
      clearHistory,
      removeHistoryItem,
      getStorageSize,
      getMostFrequentTerm,
      getAverageResults,
      getMostActiveTime,
    }
  },
}
</script>

<style lang="scss" scoped>
@import 'src/css/quasar.variables.scss';

.intelligence-history-page {
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

  .history-list-card,
  .analytics-card {
    background-color: lighten($background, 2%);
    border: 1px solid $border-color;
    border-radius: 6px;
  }

  .history-item {
    transition: background-color 0.2s;

    &:hover {
      background-color: lighten($background, 5%);
    }

    .search-query {
      font-weight: 500;
      letter-spacing: 0.3px;
    }
  }

  .insight-card {
    background-color: lighten($background, 4%);
    border: 1px solid $border-color;
    height: 100%;
    transition: transform 0.2s;

    &:hover {
      transform: translateY(-3px);
    }
  }

  .history-empty {
    color: $text-color;
    opacity: 0.7;
  }

  .confirm-dialog {
    background-color: lighten($background, 3%);
  }
}
</style>

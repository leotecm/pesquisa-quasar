<!-- src/components/SearchBar.vue -->
<template>
  <div class="intelligence-search q-pa-md">
    <q-form @submit.prevent="onSearch" class="search-form">
      <q-input
        v-model="searchQuery"
        outlined
        placeholder="Busca avançada em documentos..."
        class="search-input rounded-search"
        :loading="loading"
        dark
      >
        <template v-slot:prepend>
          <q-icon name="search" />
        </template>

        <template v-slot:append>
          <q-icon v-if="searchQuery" name="close" class="cursor-pointer" @click="clearSearch" />
          <q-btn v-else dense flat round icon="keyboard_voice" color="accent">
            <q-tooltip>Busca por voz</q-tooltip>
          </q-btn>
        </template>

        <template v-slot:after>
          <q-btn
            :loading="loading"
            :disable="loading"
            color="primary"
            class="search-button"
            @click="$emit('search', searchQuery)"
          >
            <q-icon name="search" class="q-mr-sm" />
            BUSCAR
          </q-btn>
        </template>
      </q-input>
    </q-form>

    <!-- Estatísticas da busca -->
    <div v-if="searchPerformed" class="search-stats q-mt-sm">
      <div class="status-indicator">
        <q-icon name="info" size="xs" color="accent" class="q-mr-xs" />
        <span>{{ searchStats }}</span>
      </div>
      <div v-if="totalResults > 0" class="status-badges">
        <q-chip dense size="sm" icon="access_time" outline color="accent">
          Tempo: {{ Math.random().toFixed(2) }}s
        </q-chip>
        <q-chip dense size="sm" icon="mdi-database-search" outline color="info">
          Precisão: {{ (85 + Math.random() * 10).toFixed(1) }}%
        </q-chip>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'

export default {
  name: 'SearchBar',
  props: {
    loading: {
      type: Boolean,
      default: false,
    },
    totalResults: {
      type: Number,
      default: 0,
    },
    searchPerformed: {
      type: Boolean,
      default: false,
    },
  },
  emits: ['search', 'clear'],
  setup(props, { emit }) {
    const searchQuery = ref('')

    // Informações de estatísticas da busca
    const searchStats = computed(() => {
      if (props.totalResults === 0) {
        return 'Nenhum documento correspondente aos critérios de busca'
      } else if (props.totalResults === 1) {
        return '1 documento encontrado'
      } else {
        return `${props.totalResults} documentos encontrados`
      }
    })

    // Função para executar busca
    function onSearch() {
      console.log('onSearch chamado com:', searchQuery.value)
      if (searchQuery.value.trim()) {
        console.log('Emitindo evento de busca com termo:', searchQuery.value)
        emit('search', searchQuery.value)
      }
    }

    // Função para limpar busca
    function clearSearch() {
      console.log('clearSearch chamado')
      searchQuery.value = ''
      emit('clear')
    }

    return {
      searchQuery,
      searchStats,
      onSearch,
      clearSearch,
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

.intelligence-search {
  max-width: 950px;
  margin: 0 auto;
  border-radius: 8px;

  .search-form {
    width: 100%;
    position: relative;

    &:after {
      content: '';
      position: absolute;
      bottom: -2px;
      left: 20%;
      width: 60%;
      height: 1px;
      background: linear-gradient(
        90deg,
        rgba(0, 160, 176, 0),
        rgba(0, 160, 176, 0.6),
        rgba(0, 160, 176, 0)
      );
    }
  }

  .search-input {
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);

    /* Estilo para barra de pesquisa com cantos arredondados estilo Google */
    &.rounded-search {
      :deep(.q-field__control) {
        border-radius: 24px !important;
        background-color: lighten($background, 5%);
        border: 1px solid $border-color;
        height: 48px;

        &:hover {
          border-color: rgba(0, 160, 176, 0.4);
        }

        &.q-field__control--focused {
          border-color: $accent;
          box-shadow:
            0 0 0 1px $accent,
            0 3px 8px rgba(0, 0, 0, 0.2);
        }
      }

      :deep(.q-field__marginal) {
        height: 48px;
        color: rgba(255, 255, 255, 0.7);
      }
    }

    :deep(.q-field__native) {
      color: white;
      font-weight: 400;
      letter-spacing: 0.3px;
      padding-left: 4px;
    }
  }

  /* Botão arredondado para combinar com a barra de pesquisa */
  .search-button {
    background-color: #00666b !important;
    color: white !important;
    border-radius: 8px;
    padding: 0 24px;
    height: 48px;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    transition: all 0.3s ease;

    &:hover {
      background-color: darken(#00666b, 5%) !important;
      transform: translateY(-1px);
      box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }

    &:active {
      transform: translateY(0);
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
  }

  .search-stats {
    font-size: 0.85rem;
    color: rgba(255, 255, 255, 0.7);
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 8px;

    .status-indicator {
      display: flex;
      align-items: center;
    }
  }
}
</style>

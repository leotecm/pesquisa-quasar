<!-- src/components/SideNavigation.vue -->
<template>
  <q-list padding class="intelligence-nav">
    <q-item-label header class="text-uppercase">Operações</q-item-label>

    <q-item to="/" exact clickable v-ripple class="nav-item" @click="clearSearch">
      <q-item-section avatar>
        <q-icon name="search" />
      </q-item-section>
      <q-item-section>Busca Avançada</q-item-section>
    </q-item>

    <q-item to="/recent" clickable v-ripple class="nav-item">
      <q-item-section avatar>
        <q-icon name="update" />
      </q-item-section>
      <q-item-section>Documentos Recentes</q-item-section>
    </q-item>

    <q-item to="/historico" clickable v-ripple class="nav-item">
      <q-item-section avatar>
        <q-icon name="history" />
      </q-item-section>
      <q-item-section>Histórico de Buscas</q-item-section>
    </q-item>

    <q-expansion-item
      icon="folder"
      label="Classificação de Documentos"
      caption="Filtros por tipo"
      expand-separator
      class="nav-expansion"
      header-class="nav-expansion-header"
    >
      <q-item to="/documentos/doc" clickable v-ripple dense class="nav-item">
        <q-item-section avatar>
          <q-icon name="mdi-file-word" color="blue-6" />
        </q-item-section>
        <q-item-section>Word (.doc, .docx)</q-item-section>
      </q-item>

      <q-item to="/documentos/pdf" clickable v-ripple dense class="nav-item">
        <q-item-section avatar>
          <q-icon name="mdi-file-pdf" color="negative" />
        </q-item-section>
        <q-item-section>PDF</q-item-section>
      </q-item>

      <q-item to="/documentos/txt" clickable v-ripple dense class="nav-item">
        <q-item-section avatar>
          <q-icon name="mdi-file-document" color="grey" />
        </q-item-section>
        <q-item-section>Texto (.txt)</q-item-section>
      </q-item>
    </q-expansion-item>

    <q-expansion-item
      icon="date_range"
      label="Análise Temporal"
      caption="Filtros por período"
      expand-separator
      class="nav-expansion"
      header-class="nav-expansion-header"
    >
      <q-item to="/periodo/hoje" clickable v-ripple dense class="nav-item">
        <q-item-section avatar>
          <q-icon name="today" />
        </q-item-section>
        <q-item-section>Hoje</q-item-section>
      </q-item>

      <q-item to="/periodo/semana" clickable v-ripple dense class="nav-item">
        <q-item-section avatar>
          <q-icon name="view_week" />
        </q-item-section>
        <q-item-section>Esta Semana</q-item-section>
      </q-item>

      <q-item to="/periodo/mes" clickable v-ripple dense class="nav-item">
        <q-item-section avatar>
          <q-icon name="calendar_month" />
        </q-item-section>
        <q-item-section>Este Mês</q-item-section>
      </q-item>
    </q-expansion-item>

    <q-item-label header class="text-uppercase">Sistema de Vínculos</q-item-label>

    <q-item to="/tags" clickable v-ripple class="nav-item">
      <q-item-section avatar>
        <q-icon name="link" color="accent" />
      </q-item-section>
      <q-item-section>Vínculos</q-item-section>
    </q-item>

    <q-item-label header class="text-uppercase">Recursos</q-item-label>

    <q-item to="/favoritos" clickable v-ripple class="nav-item">
      <q-item-section avatar>
        <q-icon name="star" color="amber-6" />
      </q-item-section>
      <q-item-section>Favoritos</q-item-section>
    </q-item>

    <!-- Status do sistema -->
    <div class="system-status q-mt-xl q-mb-md q-mx-sm q-pa-sm">
      <div class="text-caption q-mb-xs">STATUS DO SISTEMA</div>
      <div class="row items-center q-gutter-xs">
        <q-chip dense size="sm" color="green-7" text-color="white" icon="dns" class="status-chip">
          Banco de Dados
        </q-chip>
        <q-chip dense size="sm" color="blue-7" text-color="white" icon="cloud" class="status-chip">
          Elasticsearch
        </q-chip>
        <q-chip
          dense
          size="sm"
          color="orange-8"
          text-color="white"
          icon="storage"
          class="status-chip"
        >
          Armazenamento: 72%
        </q-chip>
      </div>
    </div>
  </q-list>
</template>

<script>
export default {
  name: 'SideNavigation',
  methods: {
    clearSearch() {
      // Emitir evento para limpar a busca
      this.$router.push('/')
    },
  },
}
</script>

<style lang="scss" scoped>
@import 'src/css/quasar.variables.scss';

.intelligence-nav {
  .q-item-label.header {
    color: rgba(255, 255, 255, 0.5);
    font-size: 0.7rem;
    letter-spacing: 1px;
    margin-top: 12px;
    margin-bottom: 8px;
  }

  .nav-item {
    border-radius: 4px;
    margin: 2px 8px;

    &.q-router-link--active {
      background-color: rgba(0, 160, 176, 0.15);
      border-left: 3px solid $accent;

      .q-icon {
        color: $accent;
      }
    }
  }

  .nav-expansion {
    .nav-expansion-header {
      border-radius: 4px;
      margin: 2px 8px;
    }
  }

  .system-status {
    background-color: rgba(0, 0, 0, 0.3);
    border-radius: 4px;
    border: 1px solid rgba(255, 255, 255, 0.1);

    .text-caption {
      color: rgba(255, 255, 255, 0.7);
      font-size: 0.7rem;
      font-weight: 500;
      letter-spacing: 1px;
    }

    .status-chip {
      font-weight: 500;
      letter-spacing: 0.5px;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
    }
  }
}
</style>

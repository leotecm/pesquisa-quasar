<!-- src/components/SideNavigation.vue -->
<template>
  <q-list padding class="intelligence-nav">
    <q-item-label header class="text-uppercase">Operações</q-item-label>

    <q-item to="/" exact clickable v-ripple class="nav-item">
      <q-item-section avatar>
        <q-icon name="search" />
      </q-item-section>
      <q-item-section>Busca Avançada</q-item-section>
    </q-item>

    <q-item to="/recentes" clickable v-ripple class="nav-item">
      <q-item-section avatar>
        <q-icon name="update" />
      </q-item-section>
      <q-item-section>Documentos Recentes</q-item-section>
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

    <q-item-label header class="text-uppercase">Classificação</q-item-label>

    <q-item to="/tags" clickable v-ripple class="nav-item">
      <q-item-section avatar>
        <q-icon name="local_offer" color="accent" />
      </q-item-section>
      <q-item-section>Sistema de Tags</q-item-section>
    </q-item>

    <q-item-label header class="text-uppercase">Recursos</q-item-label>

    <q-item to="/favoritos" clickable v-ripple class="nav-item">
      <q-item-section avatar>
        <q-icon name="star" color="amber-6" />
      </q-item-section>
      <q-item-section>Favoritos</q-item-section>
    </q-item>

    <q-item to="/historico" clickable v-ripple class="nav-item">
      <q-item-section avatar>
        <q-icon name="history" />
      </q-item-section>
      <q-item-section>Histórico de Buscas</q-item-section>
    </q-item>

    <!-- Status do sistema -->
    <div class="system-status q-mt-xl q-mb-md q-mx-sm q-pa-sm">
      <div class="text-caption q-mb-xs">STATUS DO SISTEMA</div>
      <div class="row items-center q-gutter-xs">
        <q-chip dense size="sm" color="positive" text-color="white" icon="dns">
          Banco de Dados
        </q-chip>
        <q-chip dense size="sm" color="positive" text-color="white" icon="cloud">
          Elasticsearch
        </q-chip>
        <q-chip dense size="sm" color="warning" text-color="white" icon="storage">
          Armazenamento: 72%
        </q-chip>
      </div>
    </div>
  </q-list>
</template>

<script>
export default {
  name: 'SideNavigation',
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
    background-color: rgba(0, 0, 0, 0.2);
    border-radius: 4px;
    border: 1px solid rgba(255, 255, 255, 0.05);

    .text-caption {
      color: rgba(255, 255, 255, 0.5);
      font-size: 0.65rem;
      letter-spacing: 1px;
    }
  }
}
</style>

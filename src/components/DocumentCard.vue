<!-- src/components/DocumentCard.vue -->
<template>
  <q-card
    class="intelligence-document-card cursor-pointer rounded-card"
    @click="$emit('click')"
    v-ripple
  >
    <div class="card-status-indicator" :class="getDocumentPriority()"></div>

    <q-card-section class="text-center">
      <!-- Ícone baseado no tipo de documento -->
      <q-icon
        :name="getDocumentIcon(document.type)"
        size="42px"
        :color="getDocumentColor(document.type)"
        class="document-icon"
      />
    </q-card-section>

    <q-card-section>
      <div class="document-title ellipsis">{{ document.name }}</div>

      <div class="document-meta">
        <div class="text-caption">
          <q-icon name="update" size="12px" class="q-mr-xs" />
          <span>{{ formatDate(document.lastModified) }}</span>
        </div>

        <div class="classification">
          <q-chip size="xs" dense outline color="accent" class="rounded-chip">Confidencial</q-chip>
        </div>
      </div>
    </q-card-section>

    <q-card-actions align="right" class="card-actions">
      <q-btn flat round dense size="sm" color="info" icon="visibility" class="action-button">
        <q-tooltip>Visualizar</q-tooltip>
      </q-btn>
      <q-btn flat round dense size="sm" color="accent" icon="download" class="action-button">
        <q-tooltip>Download</q-tooltip>
      </q-btn>
      <q-btn flat round dense size="sm" color="grey" icon="more_vert" class="action-button">
        <q-tooltip>Mais opções</q-tooltip>
      </q-btn>
    </q-card-actions>
  </q-card>
</template>

<script>
import { date } from 'quasar'

export default {
  name: 'DocumentCard',
  props: {
    document: {
      type: Object,
      required: true,
    },
  },
  emits: ['click'],
  methods: {
    getDocumentIcon(type) {
      const icons = {
        doc: 'mdi-file-word',
        docx: 'mdi-file-word',
        pdf: 'mdi-file-pdf',
        txt: 'mdi-file-document',
        default: 'mdi-file',
      }
      return icons[type] || icons.default
    },
    getDocumentColor(type) {
      const colors = {
        doc: 'blue-6',
        docx: 'blue-6',
        pdf: 'red-6',
        txt: 'grey-6',
        default: 'grey-7',
      }
      return colors[type] || colors.default
    },
    formatDate(dateString) {
      return date.formatDate(dateString, 'DD/MM/YYYY HH:mm')
    },
    getDocumentPriority() {
      // Simulando prioridades diferentes para diferentes documentos
      const fileName = this.document.name.toLowerCase()
      if (fileName.includes('urgent') || fileName.includes('important')) {
        return 'priority-high'
      } else if (fileName.includes('review') || fileName.includes('check')) {
        return 'priority-medium'
      } else {
        return 'priority-normal'
      }
    },
  },
}
</script>

<style lang="scss" scoped>
@import 'src/css/quasar.variables.scss';

.intelligence-document-card {
  position: relative;
  overflow: hidden;
  transition:
    transform 0.2s,
    box-shadow 0.2s;
  height: 100%;
  border-radius: 16px !important;

  &.rounded-card {
    border-radius: 16px !important;
  }

  &:hover {
    transform: translateY(-4px);
    box-shadow:
      0 8px 16px rgba(0, 0, 0, 0.2),
      0 0 0 1px rgba(0, 160, 176, 0.2);

    .document-icon {
      transform: scale(1.1);
    }

    .action-button {
      opacity: 1;
    }
  }

  .card-status-indicator {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 3px;

    &.priority-high {
      background-color: $negative;
    }

    &.priority-medium {
      background-color: $warning;
    }

    &.priority-normal {
      background-color: $info;
    }
  }

  .document-icon {
    transition: transform 0.2s;
  }

  .document-title {
    font-weight: 500;
    font-size: 1rem;
    margin-bottom: 8px;
    color: white;
  }

  .document-meta {
    display: flex;
    justify-content: space-between;
    align-items: center;

    .text-caption {
      color: rgba(255, 255, 255, 0.6);
      font-size: 0.75rem;
      display: flex;
      align-items: center;
    }

    .classification {
      .rounded-chip {
        font-size: 0.65rem;
        height: 18px;
        border-radius: 9px !important;
      }
    }
  }

  .card-actions {
    padding-top: 0;
    padding-bottom: 8px;

    .action-button {
      opacity: 0.7;
      transition:
        opacity 0.2s,
        transform 0.2s;

      &:hover {
        transform: scale(1.1);
      }
    }
  }

  &:hover .card-actions .action-button {
    opacity: 1;
  }
}
</style>

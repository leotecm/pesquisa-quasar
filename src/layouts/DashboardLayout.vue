<!-- src/layouts/DashboardLayout.vue -->
<template>
  <q-layout view="hHh LpR fFf">
    <!-- Cabeçalho -->
    <q-header elevated class="intelligence-header">
      <q-toolbar>
        <q-btn flat dense round icon="menu" aria-label="Menu" @click="toggleLeftDrawer" />
        <q-toolbar-title>
          <div class="header-title">
            <q-icon name="mdi-shield-search" size="28px" class="q-mr-sm text-accent" />
            CORREGEDORIA - CPM 2
          </div>
        </q-toolbar-title>

        <q-space />

        <!-- Ícones de status -->
        <q-btn round flat icon="notifications" size="sm" class="glow-hover">
          <q-badge color="negative" floating>2</q-badge>
          <q-tooltip>Notificações</q-tooltip>
        </q-btn>

        <q-btn round flat icon="person" size="sm" class="glow-hover">
          <q-tooltip>Perfil do Usuário</q-tooltip>
        </q-btn>

        <q-btn round flat icon="settings" size="sm" class="glow-hover">
          <q-tooltip>Configurações</q-tooltip>
        </q-btn>
      </q-toolbar>

      <!-- Linha decorativa -->
      <div class="header-line"></div>
    </q-header>

    <!-- Menu lateral retrátil -->
    <q-drawer
      v-model="leftDrawerOpen"
      bordered
      :width="250"
      :breakpoint="500"
      show-if-above
      class="intelligence-drawer"
    >
      <div class="drawer-header q-py-md q-px-sm flex flex-center">
        <q-avatar
          size="40px"
          color="dark"
          text-color="accent"
          icon="mdi-shield-search"
          class="glow"
        />
        <div class="q-ml-sm text-weight-bold">Sistema de Documentos</div>
      </div>

      <q-separator dark />

      <side-navigation />
    </q-drawer>

    <!-- Conteúdo principal -->
    <q-page-container class="page-container">
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script>
import { ref } from 'vue'
import SideNavigation from 'components/SideNavigation.vue'

export default {
  name: 'DashboardLayout',
  components: {
    SideNavigation,
  },
  setup() {
    const leftDrawerOpen = ref(false)

    return {
      leftDrawerOpen,
      toggleLeftDrawer() {
        leftDrawerOpen.value = !leftDrawerOpen.value
      },
    }
  },
}
</script>

<style lang="scss" scoped>
@import 'src/css/quasar.variables.scss';

.intelligence-header {
  background-color: $dark;
  position: relative;
  box-shadow: 0 2px 15px rgba(0, 242, 254, 0.1);

  .header-title {
    display: flex;
    align-items: center;
    font-size: 1.2rem;
    font-weight: 600;
    letter-spacing: 1px;
    color: $text-color;
    text-shadow: 0 0 10px rgba(0, 242, 254, 0.3);
  }

  .header-line {
    height: 2px;
    background: linear-gradient(90deg, rgba($accent, 0.9), rgba($accent, 0.3), transparent);
    box-shadow: 0 0 15px rgba($accent, 0.5);
  }
}

.intelligence-drawer {
  background-color: $dark;
  border-right: 1px solid rgba($accent, 0.1);

  .drawer-header {
    padding: 16px;
    background-color: rgba($primary, 0.5);
    color: $text-color;
    border-bottom: 1px solid rgba($accent, 0.1);
  }

  :deep(.q-item) {
    color: rgba($text-color, 0.7);
    transition: all 0.3s ease;

    &:hover {
      background-color: $menu-hover;
      color: $accent;
      text-shadow: 0 0 8px rgba($accent, 0.5);
    }

    &.q-item--active {
      color: $accent;
      background-color: rgba($menu-active, 0.1);
      border-left: 2px solid $accent;

      .q-item__section--avatar {
        color: $accent;
      }
    }
  }
}

.page-container {
  background-color: $background;
  min-height: 100vh;
  padding: 20px;
}

// Efeitos especiais
.glow {
  box-shadow: 0 0 10px rgba($accent, 0.3);
}

.glow-hover {
  transition: all 0.3s ease;

  &:hover {
    color: $accent !important;
    text-shadow: 0 0 8px rgba($accent, 0.5);
  }
}

:deep(.bg-blue-1) {
  background: rgba($accent, 0.05) !important;
  color: $accent !important;
  border: 1px solid rgba($accent, 0.1);
  backdrop-filter: blur(5px);
}

// Estilo do botão de busca
:deep(.q-btn) {
  &.primary {
    background: linear-gradient(135deg, $accent, darken($accent, 15%)) !important;
    border: 1px solid rgba($accent, 0.3);
    color: $dark !important;
    text-shadow: 0 0 10px rgba($accent, 0.5);
    box-shadow: 0 0 15px rgba($accent, 0.2);
    transition: all 0.3s ease;

    &:hover {
      background: linear-gradient(135deg, lighten($accent, 10%), $accent) !important;
      box-shadow: 0 0 20px rgba($accent, 0.4);
      transform: translateY(-1px);
    }

    .q-icon {
      color: $dark !important;
    }
  }
}
</style>

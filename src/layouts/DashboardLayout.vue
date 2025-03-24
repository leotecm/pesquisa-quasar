<!-- src/layouts/DashboardLayout.vue -->
<template>
  <q-layout view="hHh LpR fFf">
    <!-- Cabeçalho -->
    <q-header elevated class="intelligence-header">
      <q-toolbar>
        <q-btn flat dense round icon="menu" aria-label="Menu" @click="toggleLeftDrawer" />
        <q-toolbar-title>
          <div class="header-title">
            <q-icon name="mdi-shield-search" size="28px" class="q-mr-sm" />
            SISTEMA DE INTELIGÊNCIA DOCUMENTAL
          </div>
        </q-toolbar-title>

        <q-space />

        <!-- Ícones de status -->
        <q-btn round flat icon="notifications" size="sm">
          <q-badge color="negative" floating>2</q-badge>
          <q-tooltip>Notificações</q-tooltip>
        </q-btn>

        <q-btn round flat icon="person" size="sm">
          <q-tooltip>Perfil do Usuário</q-tooltip>
        </q-btn>

        <q-btn round flat icon="settings" size="sm">
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
        <q-avatar size="40px" color="accent" text-color="white" icon="mdi-shield-search" />
        <div class="q-ml-sm text-weight-bold">Sistema de Documentos</div>
      </div>

      <q-separator dark />

      <side-navigation />
    </q-drawer>

    <!-- Conteúdo principal -->
    <q-page-container>
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
  background-color: $primary;
  position: relative;

  .header-title {
    display: flex;
    align-items: center;
    font-size: 1.2rem;
    font-weight: 500;
    letter-spacing: 0.5px;
  }

  .header-line {
    height: 2px;
    background: linear-gradient(
      90deg,
      rgba(0, 160, 176, 0.8),
      rgba(0, 160, 176, 0.2),
      rgba(0, 160, 176, 0)
    );
  }
}

.intelligence-drawer {
  .drawer-header {
    padding: 12px;
    background-color: lighten($primary, 3%);
  }
}
</style>

// src/router/routes.js
const routes = [
  {
    path: '/',
    component: () => import('layouts/DashboardLayout.vue'),
    children: [
      {
        path: '',
        component: () => import('pages/SearchResults.vue'),
      },
      {
        path: 'recentes',
        component: () => import('pages/SearchResults.vue'),
        props: { filter: 'recent' },
      },
      {
        path: 'favoritos',
        component: () => import('pages/SearchResults.vue'),
        props: { filter: 'favorites' },
      },
      {
        path: 'documentos/:type',
        component: () => import('pages/SearchResults.vue'),
        props: (route) => ({ type: route.params.type }),
      },
      {
        path: 'periodo/:timeframe',
        component: () => import('pages/SearchResults.vue'),
        props: (route) => ({ timeframe: route.params.timeframe }),
      },
      {
        path: 'historico',
        component: () => import('pages/SearchHistory.vue'),
      },
      // Novas rotas para o sistema de tags
      {
        path: 'tags',
        component: () => import('pages/TagsPage.vue'),
      },
      {
        path: 'tags/:tagId',
        component: () => import('pages/SearchResults.vue'),
        props: (route) => ({ tagId: route.params.tagId }),
      },
    ],
  },

  // Rota para erros (404)
  {
    path: '/:catchAll(.*)*',
    component: () => import('pages/ErrorNotFound.vue'),
  },
]

export default routes

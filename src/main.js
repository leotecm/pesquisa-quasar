import { createApp } from 'vue'
import { Quasar, Notify } from 'quasar'

// Import icon libraries
import '@quasar/extras/material-icons/material-icons.css'
import '@quasar/extras/material-icons-outlined/material-icons-outlined.css'
import '@quasar/extras/mdi-v6/mdi-v6.css'

// Import Quasar css
import 'quasar/src/css/index.sass'

// Importar CSS customizado
import './css/app.scss'

// Importar a aplicação
import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(Quasar, {
  plugins: {
    Notify,
  },
  config: {
    dark: true, // Ativar modo escuro para toda a aplicação
    brand: {
      primary: '#0A192F',
      secondary: '#2C3E50',
      accent: '#00A0B0',
      positive: '#005F73',
      negative: '#B71C1C',
      info: '#00838F',
      warning: '#C77800',
    },
    notify: {
      position: 'top',
      timeout: 2500,
      textColor: 'white',
      actions: [{ icon: 'close', color: 'white' }],
    },
  },
})

app.use(router)
app.mount('#app')

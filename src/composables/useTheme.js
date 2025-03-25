import { ref } from 'vue'

const isDark = ref(true) // Começa com tema escuro por padrão

export function useTheme() {
  // Carregar preferência do usuário do localStorage
  const savedTheme = localStorage.getItem('theme')
  if (savedTheme) {
    isDark.value = savedTheme === 'dark'
  }

  // Aplicar tema inicial
  applyTheme()

  // Função para alternar o tema
  function toggleTheme() {
    isDark.value = !isDark.value
    applyTheme()
    // Salvar preferência do usuário
    localStorage.setItem('theme', isDark.value ? 'dark' : 'light')
  }

  // Função para aplicar o tema
  function applyTheme() {
    document.body.classList.remove('theme-light', 'theme-dark')
    document.body.classList.add(isDark.value ? 'theme-dark' : 'theme-light')
  }

  return {
    isDark,
    toggleTheme,
  }
}

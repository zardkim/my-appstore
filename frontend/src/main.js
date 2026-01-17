import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import i18n from './locales'
import App from './App.vue'
import './style.css'
import { useLocaleStore } from './store/locale'

const app = createApp(App)

const pinia = createPinia()
app.use(pinia)
app.use(router)
app.use(i18n)

// Initialize locale store and apply saved language preference
const localeStore = useLocaleStore()
localeStore.setLocale(localeStore.locale)

app.mount('#app')

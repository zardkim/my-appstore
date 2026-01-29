import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [
    vue({
      template: {
        compilerOptions: {
          // Vue 내장 컴포넌트를 커스텀 엘리먼트로 처리하지 않도록 설정
          isCustomElement: () => false
        }
      }
    })
  ],
  server: {
    host: true,
    port: 5900,
    watch: {
      usePolling: true
    }
  }
})

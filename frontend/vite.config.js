import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { readFileSync } from 'fs'
import { fileURLToPath } from 'url'
import { dirname, join } from 'path'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

// Read version from package.json
const packageJson = JSON.parse(
  readFileSync(join(__dirname, 'package.json'), 'utf-8')
)

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
  define: {
    __APP_VERSION__: JSON.stringify(packageJson.version),
  },
  server: {
    host: true,
    port: 5900,
    watch: {
      usePolling: true
    }
  }
})

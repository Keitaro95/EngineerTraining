import { defineConfig } from 'vite'

// ai-swift.com/dance-movie-app/ から Nuxt の routeRules で中継して配信するため、
// アセットのパスにサブパスを付ける（vercel.app を直接開くとアセットが 404 になる）
export default defineConfig({
  base: '/dance-movie-app/',
})

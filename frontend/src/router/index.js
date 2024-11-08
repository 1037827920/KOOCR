import { createRouter, createWebHistory } from 'vue-router'
import IndexPage from '../views/Index.vue'

const routes = [
  {
    path: '/',
    name: 'Index',
    component: IndexPage
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router
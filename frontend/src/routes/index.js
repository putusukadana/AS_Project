import { createRouter, createWebHistory } from 'vue-router'
import authRoutes from './auth-routes'

const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  ...authRoutes
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router

import { createRouter, createWebHistory } from 'vue-router'
import authRoutes from './auth-routes'

const routes = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/data-engine',
    name: 'DataEngine',
    component: () => import('@/views/DataEngine.vue'),
    meta: { requiresAuth: true }
  },
  ...authRoutes
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router

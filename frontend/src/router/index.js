import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

import HomeView from '@/views/HomeView.vue'
import LoginView from '@/views/LoginView.vue'
import SignupView from '@/views/SignupView.vue'
import ProfileView from '@/views/ProfileView.vue'

import DepositsView from '@/views/DepositsView.vue'
import MetalsView from '@/views/MetalsView.vue'
import StocksView from '@/views/StocksView.vue'
import MapView from '@/views/MapView.vue'
import CommunityView from '@/views/CommunityView.vue'
import ProductDetailView from '@/views/ProductDetailView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: HomeView },
    { path: '/login', component: LoginView },
    { path: '/signup', component: SignupView },
    { path: '/profile', component: ProfileView, meta: { requiresAuth: true } },
    { path: '/deposits', component: DepositsView },
    { path: '/metals', component: MetalsView },
    { path: '/stocks', component: StocksView },
    { path: '/map', component: MapView },
    { path: '/community', component: CommunityView },
    { path: '/products/:id', component: ProductDetailView },
  ],
})


router.beforeEach((to => {
  const auth = useAuthStore()
  if (to.meta.requiresAuth && !auth.isLoggedIn) return '/login'
}))


export default router

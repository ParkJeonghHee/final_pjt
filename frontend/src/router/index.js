import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

import HomeView from '@/views/HomeView.vue'
import LoginView from '@/views/LoginView.vue'
import SignupView from '@/views/SignupView.vue'
import ProfileView from '@/views/ProfileView.vue'

import DepositsView from '@/views/DepositsView.vue'
import LoansView from '@/views/LoansView.vue'
import LoanDetailView from '@/views/LoanDetailView.vue'
import MetalsView from '@/views/MetalsView.vue'
import StocksView from '@/views/StocksView.vue'
import MapView from '@/views/MapView.vue'

import ProductDetailView from '@/views/ProductDetailView.vue'
import StockDetailView from '@/views/StockDetailView.vue'


import CommunityListView from '@/views/CommunityListView.vue'
import CommunityDetailView from '@/views/CommunityDetailView.vue'
import CommunityCreateView from '@/views/CommunityCreateView.vue'
import CommunityEditView from '@/views/CommunityEditView.vue'


const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: HomeView },
    { path: '/login', component: LoginView },
    { path: '/signup', component: SignupView },
    { path: '/profile', component: ProfileView, meta: { requiresAuth: true } },
    { path: '/deposits', component: DepositsView },
    { path: '/loans', component: LoansView },
    { path: '/loans/:finPrdtCd', component: LoanDetailView },
    { path: '/metals', component: MetalsView },
    { path: '/stocks', component: StocksView },
    { path: '/map', component: MapView },

    { path: '/products/:id', component: ProductDetailView },
    { path: '/stocks/:videoId', component: StockDetailView},

    { path: '/community', name: 'community-list', component: CommunityListView,},
    { path: '/community/create', name: 'community-cretae', component: CommunityCreateView,},
    { path: '/community/:id', name: 'community-detail', component: CommunityDetailView,},
    { path: '/community/:id/edit', name: 'community-edit', component: CommunityEditView,},

  ],
})


router.beforeEach((to => {
  const auth = useAuthStore()
  if (to.meta.requiresAuth && !auth.isLoggedIn) return '/login'
}))


export default router

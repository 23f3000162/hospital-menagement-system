import { createRouter, createWebHistory } from 'vue-router'

import Login from '../views/Login.vue'
import PatientDashboard from '../views/PatientDashboard.vue'  // 1, this file define client side route for my vew app
import DoctorDashboard from '../views/DoctorDashboard.vue'
import AdminDashboard from '../views/AdminDashboard.vue'  // 2 mapping urls to vue component without loading the page 

const routes = [    
  { path: '/', component: Login },
  { path: '/register', component: () => import('../views/Register.vue') },
  { path: '/patient', component: PatientDashboard },
  { path: '/doctor', component: DoctorDashboard },
  { path: '/admin', component: AdminDashboard }
]


const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router

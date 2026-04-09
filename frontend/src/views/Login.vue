<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import authService from '../services/auth-service'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import Card from 'primevue/card'
import Message from 'primevue/message'

const router = useRouter()

const email = ref('')
const password = ref('')
const error = ref('')
const success = ref('')
const loading = ref(false)

const handleLogin = async () => {
  loading.value = true
  error.value = ''
  success.value = ''
  try {
    const data = await authService.login({
      email: email.value,
      password: password.value
    })
    
    localStorage.setItem('user', JSON.stringify(data.data))
    success.value = data.message || 'Login successful!'
    console.log('User logged in:', data.data)
  } catch (err) {
    error.value = err
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="flex items-center justify-center min-h-screen bg-slate-100 p-4">
    <Card class="w-full max-w-md shadow-lg">
      <template #title>
        <h2 class="text-2xl font-bold text-center text-white-800">AS Project - Welcome Back</h2>
      </template>
      <template #content>
        <form @submit.prevent="handleLogin" class="flex flex-col gap-4">
          <div class="flex flex-col gap-2">
            <label for="email" class="text-sm font-medium text-white-600">Email Address</label>
            <InputText id="email" type="email" v-model="email" placeholder="Enter your email" class="w-full" required />
          </div>
          <div class="flex flex-col gap-2">
            <label for="password" class="text-sm font-medium text-white-600">Password</label>
            <Password id="password" v-model="password" toggleMask :feedback="false" placeholder="Enter your password" class="w-full" inputClass="w-full" required />
          </div>
          <Button type="submit" label="Login" :loading="loading" class="mt-2" />
        </form>
        <Message v-if="error" severity="error" class="mt-4">{{ error }}</Message>
        <Message v-if="success" severity="success" class="mt-4">{{ success }}</Message>
        
        <div class="mt-6 text-center text-sm text-white-600">
          Don't have an account? 
          <router-link to="/register" class="text-blue-600 hover:underline font-semibold">Register here</router-link>
        </div>
      </template>
    </Card>
  </div>
</template>

<style scoped>
:deep(.p-card-body) {
  padding: 2rem;
}
</style>

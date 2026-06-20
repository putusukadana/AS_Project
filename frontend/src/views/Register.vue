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

const username = ref('')
const email = ref('')
const password = ref('')
const error = ref('')
const success = ref('')
const loading = ref(false)

const handleRegister = async () => {
  loading.value = true
  error.value = ''
  success.value = ''
  try {
    const data = await authService.register({
      username: username.value,
      email: email.value,
      password: password.value
    })
    success.value = data.message || 'User created successfully'
    // Automatically redirect to login after success
    setTimeout(() => router.push('/login'), 2000)
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
        <h2 class="text-2xl font-bold text-center text-slate-800">AS Project - Create Account</h2>
      </template>
      <template #content>
        <form @submit.prevent="handleRegister" class="flex flex-col gap-4">
          <div class="flex flex-col gap-2">
            <label for="username" class="text-sm font-medium text-slate-600">Username</label>
            <InputText id="username" v-model="username" placeholder="Enter your username" class="w-full" required />
          </div>
          <div class="flex flex-col gap-2">
            <label for="email" class="text-sm font-medium text-slate-600">Email</label>
            <InputText id="email" type="email" v-model="email" placeholder="Enter your email" class="w-full" required />
          </div>
          <div class="flex flex-col gap-2">
            <label for="password" class="text-sm font-medium text-slate-600">Password</label>
            <Password id="password" v-model="password" toggleMask placeholder="Enter your password" class="w-full" inputClass="w-full" required />
            <small class="text-xs text-slate-500">Min 8 characters, include symbols and mix cases for better security.</small>
          </div>
          <Button type="submit" label="Register" :loading="loading" class="mt-2" />
        </form>
        <Message v-if="error" severity="error" class="mt-4">{{ error }}</Message>
        <Message v-if="success" severity="success" class="mt-4">{{ success }}</Message>
        
        <div class="mt-6 text-center text-sm text-slate-600">
          Already have an account? 
          <router-link to="/login" class="text-blue-600 hover:underline font-semibold">Login here</router-link>
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

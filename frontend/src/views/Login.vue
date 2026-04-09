<script setup>
import { ref } from 'vue'
import axios from 'axios'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import Card from 'primevue/card'
import Message from 'primevue/message'

const emit = defineEmits(['toggleView'])

const email = ref('')
const password = ref('')
const error = ref('')
const success = ref('')
const loading = ref(false)

const login = async () => {
  loading.value = true
  error.value = ''
  success.value = ''
  try {
    const response = await axios.post('http://localhost:8000/api/v1/users/login', {
      email: email.value,
      password: password.value
    })
    const { message, data } = response.data
    // For this boilerplate, we'll store the object ID or email
    localStorage.setItem('user', JSON.stringify(data))
    success.value = message || 'Login successful!'
    console.log('User logged in:', data)
  } catch (err) {
    error.value = err.response?.data?.detail?.message || 'An error occurred during login.'
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
        <form @submit.prevent="login" class="flex flex-col gap-4">
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
          <a @click.prevent="$emit('toggleView')" href="#" class="text-blue-600 hover:underline font-semibold">Register here</a>
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

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import Card from 'primevue/card'
import Message from 'primevue/message'

const emit = defineEmits(['toggleView'])

const username = ref('')
const email = ref('')
const password = ref('')
const error = ref('')
const success = ref('')
const loading = ref(false)

const register = async () => {
  loading.value = true
  error.value = ''
  success.value = ''
  try {
    const response = await axios.post('http://localhost:8000/api/v1/users', {
      username: username.value,
      email: email.value,
      password: password.value
    })
    success.value = response.data.message || 'User created successfully'
    // Optionally switch to login view after success delay
    setTimeout(() => emit('toggleView'), 3000)
  } catch (err) {
    error.value = err.response?.data?.detail?.message || 'An error occurred during registration.'
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
        <form @submit.prevent="register" class="flex flex-col gap-4">
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
          <a @click.prevent="$emit('toggleView')" href="#" class="text-blue-600 hover:underline font-semibold">Login here</a>
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

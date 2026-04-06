# AS Project - Vue 3 + FastAPI + MongoDB

This project is a boilerplate implementation for a full-stack application with JWT Authentication.

## Prerequisites
- **Node.js**: v20 or later
- **Python**: v3.10 or later
- **MongoDB**: A running instance (local or Atlas)

## Project Structure
- `/backend`: FastAPI server with JWT Auth and MongoDB integration.
- `/frontend`: Vue 3 application styled with Tailwind CSS and PrimeVue.

## Getting Started

### 1. Backend Setup
1. Arahkan ke folder `backend`:
   ```bash
   cd backend
   ```
2. Pastikan file `.env` sudah dikonfigurasi dengan `MONGODB_URL` Anda.
3. Jalankan server:
   ```bash
   python main.py
   ```
   API akan berjalan di `http://localhost:8000`. Dokumentasi Swagger tersedia di `http://localhost:8000/docs`.

### 2. Frontend Setup
1. Arahkan ke folder `frontend`:
   ```bash
   cd frontend
   ```
2. Jalankan development server:
   ```bash
   npm run dev
   ```
   Aplikasi akan berjalan di `http://localhost:5173`.

## Teknologi yang Digunakan
- **Backend**: FastAPI, Motor (Async MongoDB), Jose (JWT), Passlib (Bcrypt).
- **Frontend**: Vue.js, Vite, Tailwind CSS, PrimeVue (Aura Theme), Axios.
- **Monitoring**: Logging siap diintegrasikan dengan Better Stack.

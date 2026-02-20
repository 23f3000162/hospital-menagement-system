<!--
Milestone-HMS-V2 Auth-RBAC
Role-based redirection implemented here.
-->
<template>
  <div class="login-wrapper d-flex align-items-center justify-content-center">
    <div class="login-card shadow-lg p-4 rounded">

      <h3 class="text-center text-white mb-2">Sign In to Your Account</h3>
      <p class="text-center text-muted mb-4">
        Hospital Management System
      </p>

      <!-- USERNAME -->
      <div class="mb-3">
        <label class="form-label text-light">Username</label>
        <input
          v-model="username"
          class="form-control login-input"
          placeholder="Enter your username"
        />
      </div>

      <!-- PASSWORD -->
      <div class="mb-3">
        <label class="form-label text-light">Password</label>
        <div class="input-group">
          <input
            :type="showPassword ? 'text' : 'password'"
            v-model="password"
            class="form-control login-input"
            placeholder="Enter your password"
          />
          <button
            class="btn btn-outline-secondary"
            @click="showPassword = !showPassword"
            type="button"
          >
            👁
          </button>
        </div>
      </div>

      <!-- ERROR -->
      <p v-if="error" class="text-danger text-center small">
        {{ error }}
      </p>

      <!-- LOGIN BUTTON -->
      <button class="btn btn-primary w-100 mt-3" @click="login">
        Sign In
      </button>

      <!-- REGISTER -->
      <p class="text-center mt-3 text-muted">
        New patient?
        <span class="text-primary cursor-pointer" @click="goToRegister">
          Register here
        </span>
      </p>

    </div>
  </div>
</template>

<script>
import axios from "axios"
const API = "http://127.0.0.1:5000"    

export default {
  data() {
    return {
      username: "",
      password: "",
      error: "",
      showPassword: false
    }
  },

  methods: {
    async login() {
      this.error = ""
      try {
        const res = await axios.post(`${API}/api/auth/login`, {
          username: this.username,
          password: this.password
        })

        localStorage.setItem("token", res.data.access_token)
        localStorage.setItem("role", res.data.role)
        localStorage.setItem("username", this.username)

        if (res.data.role === "admin") this.$router.push("/admin")
        else if (res.data.role === "doctor") this.$router.push("/doctor")
        else this.$router.push("/patient")

      } catch {
        this.error = "Invalid username or password"
      }
    },

    goToRegister() {
      this.$router.push("/register")
    }
  }
}
</script>

<style scoped>
.login-wrapper {
  min-height: 100vh;
  background: radial-gradient(circle at top, #4e73df, #0b132b);
}

.login-card {
  width: 100%;
  max-width: 420px;
  background: rgba(20, 20, 30, 0.9);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.login-input {
  background: #1f2937;
  color: #fff;
  border: 1px solid #374151;
}

.login-input::placeholder {
  color: #9ca3af;
}

.login-input:focus {
  background: #1f2937;
  color: #fff;
  border-color: #4e73df;
  box-shadow: none;
}

.cursor-pointer {
  cursor: pointer;
}
</style>

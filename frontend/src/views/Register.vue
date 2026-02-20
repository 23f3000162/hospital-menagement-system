<template>
  <div class="container d-flex justify-content-center align-items-center min-vh-100">
    <div class="col-md-5">

      <!-- CARD -->
      <div class="card shadow-lg border-0">
        
        <!-- HEADER -->
        <div
          class="card-header text-center text-white fw-bold"
          style="background: linear-gradient(90deg, #1cc88a, #4e73df);"
        >
          <h4 class="mb-0">Patient Registration page</h4>
          <small>Hospital Management System by anshu sharma</small>
        </div>

        <!-- BODY -->
        <div class="card-body p-4">

          <input
            v-model="form.username"
            class="form-control mb-3"
            placeholder="Username"
          />

          <input
            v-model="form.password"
            type="password"
            class="form-control mb-3"
            placeholder="Password"
          />

          <input
            v-model="form.full_name"
            class="form-control mb-3"
            placeholder="Full Name"
          />

          <div class="row">
            <div class="col-md-6 mb-3">
              <input
                v-model="form.age"
                type="number"
                class="form-control"
                placeholder="Age"
              />
            </div>

            <div class="col-md-6 mb-3">
              <input
                v-model="form.contact"
                class="form-control"
                placeholder="Contact"
              />
            </div>
          </div>

          <button class="btn btn-success w-100 fw-bold" @click="register">
            Register
          </button>

          <!-- MESSAGES -->
          <p v-if="error" class="text-danger text-center mt-3">
            {{ error }}
          </p>

          <p v-if="success" class="text-success text-center mt-3">
            {{ success }}
          </p>

        </div>

        <!-- FOOTER -->
        <div class="card-footer text-center bg-light">
          <small>
            Already registered?
            <span
              class="text-primary fw-bold"
              style="cursor:pointer"
              @click="$router.push('/')"
            >
              Login here
            </span>
          </small>
        </div>

      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'Register',
  data() {
    return {
      form: {
        username: '',
        password: '',
        full_name: '',
        age: '',
        contact: ''
      },
      error: '',
      success: ''
    }
  },
  methods: {
    async register() {
      try {
        await axios.post(
          'http://127.0.0.1:5000/api/auth/register',
          this.form
        )

        this.success = 'Registration successful! Redirecting to login...'
        this.error = ''

        setTimeout(() => {
          this.$router.push('/')
        }, 2000)

      } catch (err) {
        this.error = 'Registration failed'
        this.success = ''
      }
    }
  }
}
</script>

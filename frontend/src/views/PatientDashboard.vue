<template>
  <div class="patient-dashboard container-fluid px-4 mt-3">

    <!-- HEADER -->
     <!--
to add comment to make chnages to push the code on github
-->
    <div class="d-flex justify-content-between align-items-center mb-4 p-3 rounded"
      style="background: linear-gradient(90deg, #4e73df, #36b9cc); color: white;">
      <div>
        <h3 class="mb-0">Patient Dashboard</h3>
        <small>Welcome, {{ patientName }}</small>
      </div>
      <button class="btn btn-light text-danger fw-bold" @click="logout">
        Logout
      </button>
    </div>

    <div class="tab-bar mb-4">
      <button
        class="tab-btn"
        :class="{ active: activeTab === 'book' }"
        @click="openDepartments"
      >Book</button>
      <button
        class="tab-btn"
        :class="{ active: activeTab === 'appointments' }"
        @click="openAppointments"
      >Appointments</button>
      <button
        class="tab-btn"
        :class="{ active: activeTab === 'history' }"
        @click="openHistory"
      >History</button>
      <button
        class="tab-btn"
        :class="{ active: activeTab === 'profile' }"
        @click="openProfile"
      >Edit Profile</button>
    </div>

    <!-- DEPARTMENTS -->
    <div v-if="activeTab === 'book' && view === 'departments'" class="card shadow mb-4">
      <div class="card-header bg-primary text-white">Departments</div>
      <ul class="list-group list-group-flush">
        <li v-for="d in departments" :key="d.id"
          class="list-group-item d-flex justify-content-between">
          {{ d.name }}
          <button class="btn btn-sm btn-outline-primary" @click="loadDoctors(d.name)">
            View Doctors
          </button>
        </li>
      </ul>
    </div>

    <!-- DOCTORS -->
    <div v-if="activeTab === 'book' && view === 'doctors'" class="card shadow mb-4">
      <div class="card-header bg-info text-white">Doctors</div>

      <ul v-if="doctors.length" class="list-group list-group-flush">
        <li v-for="doc in doctors" :key="doc.id"
          class="list-group-item d-flex justify-content-between">
          <div>
            <strong>{{ doc.name }}</strong><br />
            <small class="text-muted">{{ doc.specialization }}</small>
          </div>
          <button class="btn btn-sm btn-success" @click="selectDoctor(doc)">
            Check Availability
          </button>
        </li>
      </ul>

      <div v-else class="p-3 text-center text-danger fw-bold">
        No doctors available for this department
      </div>

      <button class="btn btn-secondary m-3" @click="openDepartments">Back</button>
    </div>

    <!-- AVAILABILITY -->
    <div v-if="activeTab === 'book' && view === 'availability'" class="card shadow mb-4">
      <div class="card-header bg-success text-white">
        Availability – {{ selectedDoctor.name }}
      </div>

      <div class="card-body">

        <div v-if="!availability || Object.keys(availability).length === 0"
          class="text-center text-danger fw-bold">
          No availability has been provided by this doctor.
        </div>

        <div v-else>
          <div v-for="(slots, date) in availability" :key="date" class="mb-3">
            <strong>{{ date }}</strong>

            <div class="mt-2">
              <div v-for="s in slots" :key="s.time" class="d-inline-block me-2 mb-2">

                <button
                  class="btn btn-sm"
                  :class="isSelected(date, s.time)
                    ? 'btn-success'
                    : s.booked ? 'btn-outline-danger' : 'btn-outline-secondary'"
                  :disabled="s.booked"
                  @click="selectSlot(date, s.time)"
                >
                  {{ formatTime(s.time) }}
                </button>

                <div v-if="s.booked" class="text-danger small">
                  Appointment already booked
                </div>

              </div>
            </div>
          </div>

          <button class="btn btn-primary"
            :disabled="!selectedSlot"
            @click="bookAppointment">
            Book Appointment
          </button>
        </div>

        <button class="btn btn-secondary mt-3" @click="view = 'doctors'">
          Back
        </button>
      </div>
    </div>

    <!-- APPOINTMENTS -->
    <div v-if="activeTab === 'appointments'" class="card shadow mb-4">
      <div class="card-header bg-dark text-white">My Appointments</div>
      <ul class="list-group list-group-flush">
        <li v-for="a in appointments" :key="a.appointment_id"
          class="list-group-item d-flex justify-content-between">
          <div>
            Doctor {{ a.doctor_id }}<br />
            <small>{{ a.date }} {{ formatTime(a.time) }}</small>
          </div>
          <button class="btn btn-sm btn-outline-danger"
            @click="cancelAppointment(a.appointment_id)">
            Cancel
          </button>
        </li>
      </ul>
    </div>

    <!--  ENHANCED TREATMENT HISTORY -->
    <div v-if="activeTab === 'history'" class="mb-4">

      <div class="card shadow mb-3">
        <div class="card-header bg-secondary text-white d-flex justify-content-between align-items-center">
          <span>🩺 Treatment History</span>
          <button class="btn btn-sm btn-light text-primary fw-bold" @click="exportCSV">
            Export CSV
          </button>
        </div>
      </div>

      <div v-if="!history.length" class="text-center text-muted">
        No treatment history available.
      </div>

      <div v-for="(h, i) in history" :key="i" class="card shadow mb-3 border-0">
        <div class="card-body">

          <h6 class="text-primary mb-2">
            <i class="bi bi-heart-pulse"></i> Diagnosis
          </h6>
          <p class="fw-bold">{{ h.diagnosis }}</p>
          <div class="small text-muted mb-2">
            Doctor: {{ h.doctor_name }} | {{ h.date }} {{ formatTime(h.time) }}
          </div>

          <h6 class="text-success mb-2">
            <i class="bi bi-capsule"></i> Prescription
          </h6>
          <span class="badge bg-success fs-6">{{ h.prescription }}</span>

          <div v-if="h.notes" class="mt-3">
            <h6 class="text-secondary">
              <i class="bi bi-journal-text"></i> Notes
            </h6>
            <p class="mb-0">{{ h.notes }}</p>
          </div>

        </div>
      </div>
    </div>

    <div v-if="activeTab === 'profile'" class="card shadow mb-4">
      <div class="card-header bg-warning text-dark fw-bold">Edit My Profile</div>
      <div class="card-body">
        <label class="form-label">Username</label>
        <input v-model="profileForm.username" class="form-control mb-2" placeholder="Username" />

        <label class="form-label">Full Name</label>
        <input v-model="profileForm.full_name" class="form-control mb-2" placeholder="Full Name" />

        <label class="form-label">Age</label>
        <input v-model="profileForm.age" type="number" class="form-control mb-2" placeholder="Age" />

        <label class="form-label">Contact</label>
        <input v-model="profileForm.contact" class="form-control mb-3" placeholder="Contact" />

        <button class="btn btn-primary" @click="updateProfile">Save Changes</button>
      </div>
    </div>
	
  </div>
</template>

<script>
import axios from "axios"
const API = "http://127.0.0.1:5000"

export default {
  data() {
    return {
      patientName: "Patient",
      view: "",
      departments: [],
      doctors: [],
      selectedDoctor: null,
      availability: null,
      selectedSlot: null,
      appointments: [],
      history: [],
      activeTab: "book",
      profileForm: {
        username: "",
        full_name: "",
        age: "",
        contact: ""
      }
    }
  },

  methods: {
    authHeader() {
      return {
        headers: { Authorization: "Bearer " + localStorage.getItem("token") }
      }
    },

    logout() {
      localStorage.clear()
      this.$router.push("/")
    },

    formatTime(t) {
      if (!t) return ""
      const h = parseInt(t.split(":")[0], 10)
      return `${(h - 1) % 12 + 1}:00 ${h < 12 ? "AM" : "PM"}`
    },

    async openDepartments() {
      this.view = "departments"
      this.activeTab = "book"
      const res = await axios.get(`${API}/api/patient/departments`, this.authHeader())
      this.departments = res.data
    },

    async loadDoctors(dept) {
      this.view = "doctors"
      this.activeTab = "book"
      const res = await axios.get(`${API}/api/patient/doctors?specialization=${dept}`, this.authHeader())
      this.doctors = res.data
    },

    async selectDoctor(doc) {
      this.selectedDoctor = doc
      this.selectedSlot = null
      this.view = "availability"
      this.activeTab = "book"

      const res = await axios.get(`${API}/api/doctor/availability/${doc.id}`, this.authHeader())
      this.availability = res.data
    },

    selectSlot(date, time) {
      this.selectedSlot = { date, time }
    },

    isSelected(date, time) {
      return this.selectedSlot &&
        this.selectedSlot.date === date &&
        this.selectedSlot.time === time
    },

    async bookAppointment() {
      try {
        await axios.post(`${API}/api/patient/appointments`, {
          doctor_id: this.selectedDoctor.id,
          date: this.selectedSlot.date,
          time: this.selectedSlot.time
        }, this.authHeader())

        alert("Appointment booked successfully")
        this.openAppointments()
        this.activeTab = "appointments"

      } catch (err) {
        alert(err.response?.data?.error || "Booking failed")
      }
    },

    async openAppointments() {
      this.view = "appointments"
      const res = await axios.get(`${API}/api/patient/appointments`, this.authHeader())
      this.appointments = res.data
      this.activeTab = "appointments"
    },

    async cancelAppointment(id) {
      await axios.put(`${API}/api/patient/appointments/${id}/cancel`, {}, this.authHeader())
      this.openAppointments()
    },

    async openHistory() {
      this.view = "history"
      const res = await axios.get(`${API}/api/patient/treatments`, this.authHeader())
      this.history = res.data
      this.activeTab = "history"
    },

    async openProfile() {
      this.view = "profile"
      this.activeTab = "profile"
      await this.loadProfile()
    },

    async loadProfile() {
      const res = await axios.get(`${API}/api/patient/profile`, this.authHeader())
      this.profileForm = {
        username: res.data.username || "",
        full_name: res.data.full_name || "",
        age: res.data.age ?? "",
        contact: res.data.contact || ""
      }
    },

    async updateProfile() {
      try {
        const payload = {
          username: this.profileForm.username,
          full_name: this.profileForm.full_name,
          age: this.profileForm.age,
          contact: this.profileForm.contact
        }

        const res = await axios.put(`${API}/api/patient/profile`, payload, this.authHeader())
        const updated = res.data.profile || payload
        this.patientName = updated.username || this.patientName
        localStorage.setItem("username", this.patientName)
        this.profileForm = {
          username: updated.username || "",
          full_name: updated.full_name || "",
          age: updated.age ?? "",
          contact: updated.contact || ""
        }
        alert(res.data.message || "Profile updated successfully")
      } catch (err) {
        alert(err.response?.data?.error || "Profile update failed")
      }
    },

    // ✅ CSV EXPORT FIX
    async exportCSV() {
      try {
        const token = localStorage.getItem("token")

        await axios.post(`${API}/api/patient/export-csv`, {}, {
          headers: { Authorization: `Bearer ${token}` }
        })

        let response = null
        const maxAttempts = 12
        const delayMs = 1000

        for (let attempt = 0; attempt < maxAttempts; attempt += 1) {
          try {
            response = await axios.get(`${API}/api/patient/download-csv`, {
              headers: { Authorization: `Bearer ${token}` },
              responseType: "blob"
            })
            if (response.status === 202 && attempt < maxAttempts - 1) {
              response = null
              await new Promise((resolve) => setTimeout(resolve, delayMs))
              continue
            }
            break
          } catch (err) {
            const status = err.response?.status
            if (status === 404 && attempt < maxAttempts - 1) {
              await new Promise((resolve) => setTimeout(resolve, delayMs))
              continue
            }
            throw err
          }
        }

        if (!response) {
          alert("CSV export not ready. Please try again in a moment.")
          return
        }

        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement("a")
        link.href = url
        link.setAttribute("download", "patients.csv")
        document.body.appendChild(link)
        link.click()
        link.remove()

      } catch (err) {
        alert(err.response?.data?.error || "CSV export failed")
        console.error(err)
      }
    }
  },

  mounted() {
    this.patientName = localStorage.getItem("username") || "Patient"
    this.openAppointments()
  }
}
</script>

<style scoped>
.tab-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.tab-btn {
  border: 1px solid rgba(148, 163, 184, 0.5);
  background: #fff;
  color: #0f172a;
  padding: 0.45rem 0.9rem;
  border-radius: 999px;
  font-weight: 600;
}

.tab-btn.active {
  background: linear-gradient(120deg, #4f46e5, #06b6d4);
  color: #fff;
  border-color: transparent;
}
</style>

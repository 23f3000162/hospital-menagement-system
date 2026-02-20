<template>
  <div class="admin-dashboard container-fluid px-4 mt-3">

    <div class="admin-hero d-flex justify-content-between align-items-center mb-4 p-4 rounded-4">
      <div>
        <div class="hero-kicker">Hospital Management</div>
        <h3 class="mb-1">Admin Dashboard</h3>
        <small class="opacity-75">Manage doctors, patients, and appointments in one place</small>
      </div>
      <button class="btn btn-outline-light fw-semibold" @click="logout">
        Logout
      </button>
    </div>

    <div class="card shadow-sm border-0 search-panel mb-4">
      <div class="card-body d-flex flex-wrap align-items-center gap-2">
        <div class="search-title">Quick Search</div>
        <select v-model="searchType" class="form-select search-select">
          <option value="doctor">Doctors</option>
          <option value="patient">Patients</option>
          <option value="appointment">Appointments</option>
        </select>
        <input
          v-model="searchQuery"
          @keyup.enter="applySearch"
          class="form-control search-input"
          placeholder="Type name, specialization, or patient..."
        />
        <button class="btn btn-brand" @click="applySearch">Search</button>
      </div>
      <div v-if="searchFeedback.message" class="card-footer search-feedback" :class="searchFeedback.found ? 'text-success' : 'text-danger'">
        {{ searchFeedback.message }}
      </div>
    </div>

    <div class="tab-bar mb-4">
      <button
        class="tab-btn"
        :class="{ active: activeTab === 'overview' }"
        @click="activeTab = 'overview'"
      >Overview</button>
      <button
        class="tab-btn"
        :class="{ active: activeTab === 'doctors' }"
        @click="activeTab = 'doctors'"
      >Doctors</button>
      <button
        class="tab-btn"
        :class="{ active: activeTab === 'addDoctor' }"
        @click="activeTab = 'addDoctor'"
      >Add Doctor</button>
      <button
        class="tab-btn"
        :class="{ active: activeTab === 'patients' }"
        @click="activeTab = 'patients'"
      >Patients</button>
      <button
        class="tab-btn"
        :class="{ active: activeTab === 'appointments' }"
        @click="activeTab = 'appointments'"
      >Appointments</button>
      <button
        class="tab-btn"
        :class="{ active: activeTab === 'history' }"
        @click="activeTab = 'history'"
      >History</button>
    </div>

    <div v-if="activeTab === 'overview'">
      <div class="row mb-4">
        <div class="col-md-4">
          <div class="stat-card stat-indigo">
            <div class="stat-title">Total Doctors</div>
            <div class="stat-value">{{ stats.total_doctors }}</div>
            <div class="stat-sub">Registered and active</div>
          </div>
        </div>

        <div class="col-md-4">
          <div class="stat-card stat-green">
            <div class="stat-title">Total Patients</div>
            <div class="stat-value">{{ stats.total_patients }}</div>
            <div class="stat-sub">Care records on file</div>
          </div>
        </div>

        <div class="col-md-4">
          <div class="stat-card stat-amber">
            <div class="stat-title">Total Appointments</div>
            <div class="stat-value">{{ stats.total_appointments }}</div>
            <div class="stat-sub">All-time bookings</div>
          </div>
        </div>
      </div>

      <div class="row mb-4">
        <div class="col-md-6">
          <div class="card shadow-sm border-0 chart-card">
            <div class="card-header bg-transparent border-0 chart-header">
              Appointment Status
            </div>
            <div class="card-body">
              <canvas id="appointmentChart"></canvas>
            </div>
          </div>
        </div>

        <div class="col-md-6">
          <div class="card shadow-sm border-0 chart-card">
            <div class="card-header bg-transparent border-0 chart-header">
              System Overview
            </div>
            <div class="card-body">
              <canvas id="overviewChart"></canvas>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="activeTab === 'doctors'" class="card shadow-sm border-0 mb-4 section-card">
      <div class="card-header section-header">Registered Doctors</div>

      <ul class="list-group list-group-flush">
        <li v-for="d in filteredDoctors" :key="d.id"
          class="list-group-item d-flex justify-content-between align-items-center">
          <div>
            <strong>{{ d.name }}</strong>
            <span class="badge ms-2" :class="d.active ? 'bg-success' : 'bg-danger'">
              {{ d.active ? 'Active' : 'Blocked' }}
            </span><br />
            <small>{{ d.specialization }} | {{ d.experience }} yrs</small>
          </div>
          <div class="btn-group">
            <button class="btn btn-sm btn-outline-warning" @click="openEditDoctor(d)">Edit</button>
            <button class="btn btn-sm"
              :class="d.active ? 'btn-secondary' : 'btn-success'"
              @click="blockUser(d.user_id)">
              {{ d.active ? 'Block' : 'Unblock' }}
            </button>
            <button class="btn btn-sm btn-outline-danger" @click="deleteDoctor(d.id)">Delete</button>
          </div>
        </li>
      </ul>
    </div>

    <div v-if="activeTab === 'addDoctor'" class="card shadow-sm border-0 mb-4 section-card">
      <div class="card-header section-header">Add New Doctor</div>
      <div class="card-body">
        <input v-model="newDoctor.username" class="form-control mb-2" placeholder="Username" />
        <input v-model="newDoctor.password" type="password" class="form-control mb-2" placeholder="Password" />
        <input v-model="newDoctor.full_name" class="form-control mb-2" placeholder="Full Name" />
        <input v-model="newDoctor.specialization" class="form-control mb-2" placeholder="Specialization" />
        <input v-model="newDoctor.experience_years" type="number" class="form-control mb-3" placeholder="Experience" />
        <button class="btn btn-brand w-100" @click="addDoctor">Create Doctor</button>
      </div>
    </div>

    <div v-if="activeTab === 'patients'" class="card shadow-sm border-0 mb-4 section-card">
      <div class="card-header section-header">Registered Patients</div>
      <ul class="list-group list-group-flush">
        <li v-for="p in filteredPatients" :key="p.id"
          class="list-group-item d-flex justify-content-between align-items-center">
          <div>
            <strong>{{ p.username }}</strong>
            <span class="badge ms-2" :class="p.active ? 'bg-success' : 'bg-danger'">
              {{ p.active ? 'Active' : 'Blocked' }}
            </span><br />
            <small>{{ p.full_name }} | Age: {{ p.age || "N/A" }} | Contact: {{ p.contact || "N/A" }}</small>
          </div>
          <div class="btn-group">
            <button class="btn btn-sm btn-outline-warning" @click="openEditPatient(p)">Edit</button>
            <button class="btn btn-sm"
              :class="p.active ? 'btn-secondary' : 'btn-success'"
              @click="blockUser(p.user_id)">
              {{ p.active ? 'Block' : 'Unblock' }}
            </button>
            <button class="btn btn-sm btn-outline-danger" @click="deletePatient(p.id)">Delete</button>
            <button class="btn btn-sm btn-outline-primary"
              @click="viewHistory(p.id, p.username)">
              View History
            </button>
          </div>
        </li>
      </ul>
    </div>

    <div v-if="activeTab === 'appointments'" class="card shadow-sm border-0 mb-4 section-card">
      <div class="card-header section-header">Appointments</div>
      <table v-if="filteredAppointments.length" class="table table-hover align-middle mb-0">
        <thead>
          <tr>
            <th>ID</th>
            <th>Patient</th>
            <th>Doctor</th>
            <th>Date</th>
            <th>Status</th>
            <th>History</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="a in filteredAppointments" :key="a.appointment_id">
            <td>{{ a.appointment_id }}</td>
            <td>{{ a.patient_name }}</td>
            <td>{{ a.doctor_name }}</td>
            <td>{{ a.date }}</td>
            <td>
              <span class="badge"
                :class="a.status==='Completed' ? 'bg-success'
                  : a.status==='Cancelled' ? 'bg-danger'
                  : 'bg-warning text-dark'">
                {{ a.status }}
              </span>
            </td>
            <td>
              <button class="btn btn-sm btn-outline-primary"
                @click="viewHistory(a.patient_id, a.patient_name)">
                View
              </button>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-else class="card-body text-muted fw-semibold">
        No appointments till now.
      </div>
    </div>

    <div v-if="activeTab === 'history'" class="card shadow-sm border-0 mb-4 section-card">
      <div class="card-header section-header">
        Patient History – {{ historyPatientName }}
      </div>
      <div class="card-body">
        <button class="btn btn-outline-secondary mb-3" @click="history=[]">Back</button>
        <div v-if="!history.length" class="text-muted">
          No history available for this patient.
        </div>
        <ul v-else class="list-group">
          <li v-for="(h,i) in history" :key="i" class="list-group-item">
            <strong>Diagnosis:</strong> {{ h.diagnosis }}<br />
            <strong>Prescription:</strong> {{ h.prescription }}<br />
            <strong>Notes:</strong> {{ h.notes }}
          </li>
        </ul>
      </div>
    </div>

    <div class="modal fade" id="editDoctorModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header bg-warning">
            <h5 class="modal-title">Edit Doctor</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <label class="form-label">Full Name</label>
            <input v-model="editDoctor.full_name" class="form-control mb-2" placeholder="Full Name" />
            
            <label class="form-label">Specialization</label>
            <input v-model="editDoctor.specialization" class="form-control mb-2" placeholder="Specialization" />
            
            <label class="form-label">Experience (Years)</label>
            <input v-model="editDoctor.experience_years" type="number" class="form-control mb-2" placeholder="Experience" />
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button class="btn btn-success" @click="updateDoctor">Update</button>
          </div>
        </div>
      </div>
    </div>

    <div class="modal fade" id="editPatientModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header bg-info text-white">
            <h5 class="modal-title">Edit Patient</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <label class="form-label">Username</label>
            <input v-model="editPatient.username" class="form-control mb-2" placeholder="Username" />

            <label class="form-label">Full Name</label>
            <input v-model="editPatient.full_name" class="form-control mb-2" placeholder="Full Name" />

            <label class="form-label">Age</label>
            <input v-model="editPatient.age" type="number" class="form-control mb-2" placeholder="Age" />

            <label class="form-label">Contact</label>
            <input v-model="editPatient.contact" class="form-control mb-2" placeholder="Contact" />
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button class="btn btn-success" @click="updatePatient">Update</button>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
import axios from "axios"
import { Chart } from "chart.js/auto"
import * as bootstrap from "bootstrap"

const API = "http://127.0.0.1:5000"

export default {
  data() {
    return {
      stats: {},
      doctors: [],
      patients: [],
      appointments: [],
      history: [],
      historyPatientName: "",
      searchQuery: "",
      searchType: "doctor",
      activeTab: "overview",

      modalInstance: null,
      patientModalInstance: null,

      newDoctor: {
        username: "",
        password: "",
        full_name: "",
        specialization: "",
        experience_years: ""
      },

      editDoctor: {
        id: null,
        full_name: "",
        specialization: "",
        experience_years: ""
      },

      editPatient: {
        id: null,
        username: "",
        full_name: "",
        age: "",
        contact: ""
      }
    }
  },

  computed: {
    filteredDoctors() {
      if (this.searchType !== "doctor") return this.doctors
      return this.doctors.filter(d =>
        (d.name && d.name.toLowerCase().includes(this.searchQuery.toLowerCase())) ||
        (d.specialization && d.specialization.toLowerCase().includes(this.searchQuery.toLowerCase()))
      )
    },

    filteredAppointments() {
      if (this.searchType !== "appointment") return this.appointments
      return this.appointments.filter(a =>
        a.patient_name.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
        a.doctor_name.toLowerCase().includes(this.searchQuery.toLowerCase())
      )
    },

    filteredPatients() {
      const q = this.searchQuery.toLowerCase()
      return this.patients.filter(p =>
        this.searchType !== "patient"
        || (p.username && p.username.toLowerCase().includes(q))
        || (p.full_name && p.full_name.toLowerCase().includes(q))
      )
    },

    searchFeedback() {
      const query = (this.searchQuery || "").trim()
      if (!query) return { found: false, message: "" }

      const labels = {
        doctor: "doctor",
        patient: "patient",
        appointment: "appointment"
      }

      const resultMap = {
        doctor: this.filteredDoctors.length,
        patient: this.filteredPatients.length,
        appointment: this.filteredAppointments.length
      }

      const count = resultMap[this.searchType] || 0
      const label = labels[this.searchType] || "record"

      if (count > 0) {
        return {
          found: true,
          message: `Result found: ${count} ${label}${count > 1 ? "s" : ""}`
        }
      }

      return {
        found: false,
        message: "No result found"
      }
    }
  },

  methods: {
    applySearch() {
      if (this.searchType === "doctor") this.activeTab = "doctors"
      else if (this.searchType === "patient") this.activeTab = "patients"
      else this.activeTab = "appointments"
    },

    authHeader() {
      return { headers: { Authorization: "Bearer " + localStorage.getItem("token") } }
    },

    logout() {
      localStorage.clear()
      this.$router.push("/")
    },

    async loadAll() {
      try {
        const h = this.authHeader()
        this.stats = (await axios.get(`${API}/api/admin/dashboard`, h)).data
        this.doctors = (await axios.get(`${API}/api/admin/doctors`, h)).data
        this.patients = (await axios.get(`${API}/api/admin/patients`, h)).data
        this.appointments = (await axios.get(`${API}/api/admin/appointments`, h)).data
        this.$nextTick(() => {
          if (this.activeTab === "overview") {
            this.renderCharts()
          }
        })
      } catch (e) {
        console.error("Error loading data:", e)
      }
    },

    renderCharts() {
      const chart1 = Chart.getChart("appointmentChart")
      if (chart1) chart1.destroy()

      const chart2 = Chart.getChart("overviewChart")
      if (chart2) chart2.destroy()

      new Chart(document.getElementById("appointmentChart"), {
        type: "doughnut",
        data: {
          labels: ["Booked", "Completed", "Cancelled"],
          datasets: [{
            data: [
              this.appointments.filter(a => a.status === "Booked").length,
              this.appointments.filter(a => a.status === "Completed").length,
              this.appointments.filter(a => a.status === "Cancelled").length
            ]
          }]
        }
      })

      new Chart(document.getElementById("overviewChart"), {
        type: "bar",
        data: {
          labels: ["Doctors", "Patients", "Appointments"],
          datasets: [{
            data: [
              this.stats.total_doctors,
              this.stats.total_patients,
              this.stats.total_appointments
            ]
          }]
        }
      })
    },

    async addDoctor() {
      try {
        await axios.post(`${API}/api/admin/doctors`, this.newDoctor, this.authHeader())
        alert("Doctor added successfully!")
        this.newDoctor = { username:"", password:"", full_name:"", specialization:"", experience_years:"" }
        this.loadAll()
      } catch (error) {
        alert("Error adding doctor")
      }
    },

    openEditDoctor(d) {
      this.editDoctor = {
        id: d.id,
        full_name: d.name, 
        specialization: d.specialization,
        experience_years: d.experience
      }
      
      const element = document.getElementById("editDoctorModal")
      if (!this.modalInstance) {
        this.modalInstance = new bootstrap.Modal(element)
      }
      this.modalInstance.show()
    },

    async updateDoctor() {
      try {
        //  Send Update to Server
        await axios.put(
          `${API}/api/admin/doctors/${this.editDoctor.id}`,
          {
            name: this.editDoctor.full_name,
            full_name: this.editDoctor.full_name,
            specialization: this.editDoctor.specialization,
            experience_years: this.editDoctor.experience_years
          },
          this.authHeader()
        )
        
        
        const index = this.doctors.findIndex(d => d.id === this.editDoctor.id)
        if (index !== -1) {
          this.doctors[index] = {
            ...this.doctors[index],
            name: this.editDoctor.full_name,
            specialization: this.editDoctor.specialization,
            experience: this.editDoctor.experience_years
          }
        }

        alert("Doctor updated successfully!")
        
        // 3. Hide Modal
        if (this.modalInstance) {
          this.modalInstance.hide()
        }
        
        
        
      } catch (error) {
        console.error("Update failed:", error)
        alert("Failed to update! Check console for details.")
      }
    },

    openEditPatient(p) {
      this.editPatient = {
        id: p.id,
        username: p.username || "",
        full_name: p.full_name || "",
        age: p.age ?? "",
        contact: p.contact || ""
      }

      const element = document.getElementById("editPatientModal")
      if (!this.patientModalInstance) {
        this.patientModalInstance = new bootstrap.Modal(element)
      }
      this.patientModalInstance.show()
    },

    async updatePatient() {
      try {
        await axios.put(
          `${API}/api/admin/patients/${this.editPatient.id}`,
          {
            username: this.editPatient.username,
            full_name: this.editPatient.full_name,
            age: this.editPatient.age,
            contact: this.editPatient.contact
          },
          this.authHeader()
        )

        alert("Patient updated successfully!")
        if (this.patientModalInstance) {
          this.patientModalInstance.hide()
        }
        this.loadAll()
      } catch (error) {
        console.error("Patient update failed:", error)
        alert(error?.response?.data?.error || "Failed to update patient")
      }
    },

    async deleteDoctor(id) {
      if (confirm("Delete doctor?")) {
        await axios.delete(`${API}/api/admin/doctors/${id}`, this.authHeader())
        this.loadAll()
      }
    },

    async deletePatient(id) {
      if (confirm("Delete patient?")) {
        await axios.delete(`${API}/api/admin/patients/${id}`, this.authHeader())
        this.loadAll()
      }
    },

    async blockUser(id) {
      await axios.put(`${API}/api/admin/users/${id}/toggle`, {}, this.authHeader())
      this.loadAll()
    },

    async viewHistory(pid, name) {
      this.historyPatientName = name
      this.activeTab = "history"
      this.history = (await axios.get(
        `${API}/api/admin/patients/${pid}/history`,
        this.authHeader()
      )).data.history
    }
  },

  mounted() {
    this.loadAll()
    this.$watch(
      () => this.activeTab,
      (next) => {
        if (next === "overview") {
          this.$nextTick(this.renderCharts)
        }
      }
    )
  }
}
</script>

<style scoped>
@import url("https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700;800&display=swap");

.admin-dashboard {
  font-family: "Manrope", "Segoe UI", sans-serif;
  color: #1f2937;
  background:
    radial-gradient(1200px 400px at 20% -10%, rgba(16, 185, 129, 0.12), transparent 70%),
    radial-gradient(900px 380px at 90% 0%, rgba(79, 70, 229, 0.12), transparent 60%);
}

.admin-hero {
  background: linear-gradient(120deg, #111827, #1f2937, #0f766e);
  color: #f8fafc;
  box-shadow: 0 14px 40px rgba(15, 23, 42, 0.25);
}

.hero-kicker {
  text-transform: uppercase;
  letter-spacing: 0.12em;
  font-size: 0.72rem;
  opacity: 0.8;
}

.search-panel {
  background: #ffffff;
}

.search-title {
  font-weight: 700;
  color: #0f172a;
  margin-right: 0.25rem;
}

.search-select {
  max-width: 200px;
}

.search-input {
  flex: 1 1 320px;
}

.search-feedback {
  font-weight: 700;
  background: #f8fafc;
}

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

.btn-brand {
  background: linear-gradient(120deg, #4f46e5, #06b6d4);
  color: #fff;
  border: none;
}

.btn-brand:hover {
  opacity: 0.92;
  color: #fff;
}

.stat-card {
  padding: 1.25rem;
  border-radius: 16px;
  color: #fff;
  box-shadow: 0 10px 30px rgba(15, 23, 42, 0.15);
}

.stat-title {
  font-weight: 600;
  opacity: 0.85;
}

.stat-value {
  font-size: 2rem;
  font-weight: 800;
  margin: 0.25rem 0;
}

.stat-sub {
  font-size: 0.85rem;
  opacity: 0.8;
}

.stat-indigo { background: linear-gradient(135deg, #4f46e5, #6366f1); }
.stat-green { background: linear-gradient(135deg, #059669, #10b981); }
.stat-amber { background: linear-gradient(135deg, #f59e0b, #fbbf24); color: #1f2937; }

.chart-card {
  border-radius: 18px;
}

.chart-header {
  font-weight: 700;
  color: #0f172a;
  padding: 1rem 1.25rem 0.5rem 1.25rem;
}

.section-card {
  border-radius: 18px;
}

.section-header {
  background: transparent;
  font-weight: 700;
  color: #0f172a;
  border-bottom: 1px solid rgba(148, 163, 184, 0.25);
}

.list-group-item {
  padding: 1rem 1.25rem;
}

@media (max-width: 768px) {
  .admin-hero {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
}
</style>

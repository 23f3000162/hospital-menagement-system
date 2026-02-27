<template>
  <div class="doctor-dashboard container-fluid px-4 mt-3">
   <!---this commnet is use for push the code on github -->
    <!-- HEADER -->
    <div class="d-flex justify-content-between align-items-center mb-4 p-3 rounded"
      style="background: linear-gradient(90deg, #36b9cc, #1cc88a); color: white;">
      <div>
        <h3 class="mb-0">Doctor Dashboard</h3>
        <small>Welcome, {{ doctorName }}</small>
      </div>
      <button class="btn btn-light text-danger fw-bold" @click="logout">
        Logout
      </button>
    </div>

    <div class="tab-bar mb-4">
      <button
        class="tab-btn"
        :class="{ active: activeTab === 'overview' }"
        @click="activeTab = 'overview'"
      >Overview</button>
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
      <button
        class="tab-btn"
        :class="{ active: activeTab === 'availability' }"
        @click="activeTab = 'availability'"
      >Availability</button>
    </div>

    <div v-if="activeTab === 'overview'">
      <!-- STATS -->
      <div class="row mb-4">
        <div class="col-md-4">
          <div class="card shadow border-0 text-white" style="background:#4e73df;">
            <div class="card-body text-center">
              <h6>Today's Appointments</h6>
              <h2>{{ todayCount }}</h2>
            </div>
          </div>
        </div>

        <div class="col-md-4">
          <div class="card shadow border-0 text-white" style="background:#1cc88a;">
            <div class="card-body text-center">
              <h6>Upcoming</h6>
              <h2>{{ upcomingCount }}</h2>
            </div>
          </div>
        </div>

        <div class="col-md-4">
          <div class="card shadow border-0 text-white" style="background:#36b9cc;">
            <div class="card-body text-center">
              <h6>Completed</h6>
              <h2>{{ completedCount }}</h2>
            </div>
          </div>
        </div>
      </div>

      <!-- MONTHLY REPORT -->
      <div class="card shadow mb-4">
        <div class="card-header bg-dark text-white">
          Monthly Report (CSV)
        </div>
        <div class="card-body d-flex flex-wrap align-items-end gap-2">
          <div>
            <label class="form-label mb-1">Select Month</label>
            <input type="month" class="form-control" v-model="reportMonth" />
          </div>
          <button class="btn btn-dark" @click="exportMonthlyReport">
            Export CSV
          </button>
        </div>
      </div>
    </div>

    <!-- APPOINTMENTS -->
    <div v-if="activeTab === 'appointments'" class="card shadow mb-4">
      <div class="card-header bg-primary text-white">
        My Appointments
      </div>

      <div class="table-responsive">
        <table class="table table-bordered mb-0">
          <thead class="table-light">
            <tr>
              <th>ID</th>
              <th>Patient</th>
              <th>Date</th>
              <th>Time</th>
              <th>Status</th>
              <th width="260">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="a in appointments" :key="a.appointment_id">
              <td>{{ a.appointment_id }}</td>
              <td>{{ a.patient_name }}</td>
              <td>{{ a.date }}</td>
              <td>{{ formatTime(a.time) }}</td>
              <td>
                <span
                  class="badge"
                  :class="a.status === 'Completed'
                    ? 'bg-success'
                    : a.status === 'Cancelled'
                    ? 'bg-danger'
                    : 'bg-warning text-dark'"
                >
                  {{ a.status }}
                </span>
              </td>
              <td>
                <button
                  class="btn btn-sm btn-primary me-1"
                  @click="openUpdateForm(a)"
                >
                  Update
                </button>

                <button
                  class="btn btn-sm btn-success me-1"
                  @click="updateStatus(a.appointment_id, 'Completed')"
                >
                  Complete
                </button>

                <button
                  class="btn btn-sm btn-danger"
                  @click="updateStatus(a.appointment_id, 'Cancelled')"
                >
                  Cancel
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- UPDATE PATIENT HISTORY -->
    <div v-if="activeTab === 'appointments' && showUpdateForm" class="card shadow mb-4 border-info">
      <div class="card-header bg-info text-white">
        Update Patient History
      </div>

      <div class="card-body">
        <p><strong>Patient:</strong> {{ selectedAppointment?.patient_name }}</p>


        <input
          class="form-control mb-2"
          placeholder="Diagnosis"
          v-model="historyForm.diagnosis"
        />

        <input
          class="form-control mb-2"
          placeholder="Prescription"
          v-model="historyForm.prescription"
        />

        <textarea
          class="form-control mb-3"
          placeholder="Notes"
          v-model="historyForm.notes"
        ></textarea>

        <button class="btn btn-success me-2" @click="saveHistory">
          Save
        </button>

        <button class="btn btn-secondary" @click="showUpdateForm = false">
          Cancel
        </button>
      </div>
    </div>

    <!-- ASSIGNED PATIENTS -->
    <div v-if="activeTab === 'history'" class="card shadow mb-4">
      <div class="card-header bg-info text-white">
        Assigned Patients
      </div>

      <ul class="list-group list-group-flush">
        <li
          v-for="p in assignedPatients"
          :key="p"
          class="list-group-item d-flex justify-content-between align-items-center"
        >
          {{ p }}
          <button class="btn btn-sm btn-outline-primary" @click="viewHistoryByName(p)">
            View History
          </button>
        </li>
      </ul>
    </div>

    <!-- PROVIDE AVAILABILITY -->
    <div v-if="activeTab === 'availability'" class="card shadow mb-4">
      <div class="card-header bg-success text-white">
        Provide Availability
      </div>

      <div class="card-body">
        <input type="date" class="form-control mb-3" v-model="availabilityDate" />

        <div class="row mb-3">
          <div class="col-md-6">
            <label>Start Time</label>
            <select class="form-control" v-model="startTime">
              <option disabled value="">Select start</option>
              <option v-for="t in timeSlots" :key="t.value" :value="t.value">
                {{ t.label }}
              </option>
            </select>
          </div>

          <div class="col-md-6">
            <label>End Time</label>
            <select class="form-control" v-model="endTime">
              <option disabled value="">Select end</option>
              <option v-for="t in timeSlots" :key="t.value" :value="t.value">
                {{ t.label }}
              </option>
            </select>
          </div>
        </div>

        <button class="btn btn-success w-100" @click="addAvailability">
          Add Availability
        </button>
      </div>
    </div>

    <!-- HISTORY VIEW -->
    <div v-if="activeTab === 'history' && historyViewOpen" class="card shadow mb-4">
      <div class="card-header bg-secondary text-white">
        Patient History
      </div>

      <div class="card-body">
        <button class="btn btn-secondary mb-3" @click="closeHistory">
          Back
        </button>

        <div v-if="!history.length" class="text-muted">
          No history available for this patient.
        </div>

        <ul v-else class="list-group">
          <li class="list-group-item" v-for="(h, i) in history" :key="i">
            <strong>Diagnosis:</strong> {{ h.diagnosis }} <br />
            <strong>Prescription:</strong> {{ h.prescription }} <br />
            <strong>Notes:</strong> {{ h.notes }}
          </li>
        </ul>
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
      doctorName: "Doctor",
      appointments: [],
      assignedPatients: [],
      history: [],

      showUpdateForm: false,
      selectedAppointment: null,
      historyForm: { diagnosis: "", prescription: "", notes: "" },

      availabilityDate: "",
      startTime: "",
      endTime: "",
      reportMonth: new Date().toISOString().slice(0, 7),
      timeSlots: [
        { value: "09:00", label: "9:00 AM" },
        { value: "10:00", label: "10:00 AM" },
        { value: "11:00", label: "11:00 AM" },
        { value: "12:00", label: "12:00 PM" },
        { value: "13:00", label: "1:00 PM" },
        { value: "14:00", label: "2:00 PM" },
        { value: "15:00", label: "3:00 PM" },
        { value: "16:00", label: "4:00 PM" },
        { value: "17:00", label: "5:00 PM" },
        { value: "18:00", label: "6:00 PM" },
        { value: "19:00", label: "7:00 PM" },
        { value: "20:00", label: "8:00 PM" }
      ],
      availability: {},
      historyViewOpen: false,
      activeTab: "overview"
    }
  },

  computed: {
    todayCount() {
      const today = new Date().toISOString().slice(0, 10)
      return this.appointments.filter(a => a.date === today).length
    },
    upcomingCount() {
      return this.appointments.filter(a => a.status === "Booked").length
    },
    completedCount() {
      return this.appointments.filter(a => a.status === "Completed").length
    }
  },

  methods: {
    authHeader() {
      return { headers: { Authorization: "Bearer " + localStorage.getItem("token") } }
    },

    logout() {
      localStorage.clear()
      this.$router.push("/")
    },

    formatTime(t) {
      const h = parseInt(t.split(":")[0])
      return `${(h - 1) % 12 + 1}:00 ${h < 12 ? "AM" : "PM"}`
    },

    async loadAppointments() {
      const res = await axios.get(`${API}/api/doctor/appointments`, this.authHeader())
      this.appointments = res.data
      this.assignedPatients = [...new Set(res.data.map(a => a.patient_name))]
    },

    async updateStatus(id, status) {
      await axios.put(
        `${API}/api/doctor/appointments/${id}/status`,
        { status },
        this.authHeader()
      )
      this.loadAppointments()
    },

    openUpdateForm(a) {
      this.selectedAppointment = a
      this.historyForm = { diagnosis: "", prescription: "", notes: "" }
      this.showUpdateForm = true
    },

    async saveHistory() {
      await axios.post(
        `${API}/api/doctor/appointments/${this.selectedAppointment.appointment_id}/treatment`,
        this.historyForm,
        this.authHeader()
      )
      alert("Patient history updated")
      this.showUpdateForm = false
      this.loadAppointments()
    },

    async viewHistoryByName(name) {
      const a = this.appointments.find(x => x.patient_name === name)
      if (!a) return

      const res = await axios.get(
        `${API}/api/doctor/patients/${a.patient_id}/history`,
        this.authHeader()
      )
      this.history = res.data
      this.historyViewOpen = true
      this.activeTab = "history"
    },

    closeHistory() {
      this.history = []
      this.historyViewOpen = false
    },

    addAvailability() {
      if (!this.availabilityDate || !this.startTime || !this.endTime) {
        alert("Select date and time")
        return
      }

      const range = `${this.startTime}-${this.endTime}`
      this.availability[this.availabilityDate] = [range]

      axios.post(
        `${API}/api/doctor/availability`,
        this.availability,
        this.authHeader()
      )

      alert("Availability added")
      this.availabilityDate = ""
      this.startTime = ""
      this.endTime = ""
    },
    async exportMonthlyReport() {
      try {
        const [yearStr, monthStr] = this.reportMonth.split("-")
        const year = parseInt(yearStr, 10)
        const month = parseInt(monthStr, 10)

        const res = await axios.get(
          `${API}/api/doctor/monthly-report`,
          {
            ...this.authHeader(),
            params: { year, month },
            responseType: "blob"
          }
        )

        const blob = new Blob([res.data], { type: "text/csv" })
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement("a")
        link.href = url
        link.setAttribute("download", `doctor_monthly_report_${year}_${monthStr}.csv`)
        document.body.appendChild(link)
        link.click()
        link.remove()
        window.URL.revokeObjectURL(url)
      } catch (err) {
        alert(err.response?.data?.error || "Monthly report export failed")
      }
    }
  },

  mounted() {
    this.loadAppointments()
    this.doctorName = localStorage.getItem("username") || "Doctor"
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

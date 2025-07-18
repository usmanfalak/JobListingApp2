import axios from "axios";

const API_BASE_URL = "http://localhost:5000";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export const jobsApi = {
  // Get all jobs with optional filters
  getJobs: async (filters) => {
    const params = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value) params.append(key, value);
      });
    }
    const response = await api.get(`/jobs?${params.toString()}`);
    return response.data;
  },

  // Get single job by ID
  getJob: async (id) => {
    const response = await api.get(`/jobs/${id}`);
    return response.data;
  },

  // Create new job
  createJob: async (jobData) => {
    const response = await api.post("/jobs", {
      ...jobData,
      tags: jobData.tags
        .split(",")
        .map((tag) => tag.trim())
        .filter((tag) => tag),
    });
    return response.data;
  },

  // Update job
  updateJob: async (id, jobData) => {
    const response = await api.put(`/jobs/${id}`, {
      ...jobData,
      tags: jobData.tags
        .split(",")
        .map((tag) => tag.trim())
        .filter((tag) => tag),
    });
    return response.data;
  },

  // Delete job
  deleteJob: async (id) => {
    await api.delete(`/jobs/${id}`);
  },
  
  // Scrape jobs from ActuaryList
  scrapeJobs: async (maxJobs = 20) => {
    const response = await api.post("/scrape-jobs", { max_jobs: maxJobs });
    return response.data;
  },
};

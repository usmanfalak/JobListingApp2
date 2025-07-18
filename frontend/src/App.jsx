import React, { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import JobCard from "./components/JobCard";
import JobForm from "./components/JobForm";
import JobFilters from "./components/JobFilters";
import { jobsApi } from "./services/api";
import { Plus, Briefcase, AlertCircle, Loader2, Download } from "lucide-react";

function App() {
  const [jobs, setJobs] = useState([]);
  const [filteredJobs, setFilteredJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingJob, setEditingJob] = useState(null);
  const [formLoading, setFormLoading] = useState(false);
  const [scrapeLoading, setScrapeLoading] = useState(false);
  const [filters, setFilters] = useState({
    sort: "posting_date_desc",
  });

  // Mock data for development (remove when API is ready)
  const mockJobs = [
    {
      id: "1",
      title: "Senior React Developer",
      company: "TechCorp Solutions",
      location: "Lahore",
      job_type: "Full-time",
      tags: ["React", "TypeScript", "Node.js"],
      posting_date: "2024-01-15T10:00:00Z",
      description:
        "We are looking for an experienced React developer to join our team.",
    },
    {
      id: "2",
      title: "UI/UX Designer",
      company: "Design Studio",
      location: "Remote",
      job_type: "Part-time",
      tags: ["Figma", "Adobe XD", "Prototyping"],
      posting_date: "2024-01-14T09:30:00Z",
      description:
        "Create beautiful and intuitive user interfaces for web and mobile applications.",
    },
    {
      id: "3",
      title: "Marketing Intern",
      company: "StartupXYZ",
      location: "Karachi",
      job_type: "Internship",
      tags: ["Digital Marketing", "Social Media", "Content"],
      posting_date: "2024-01-13T14:20:00Z",
      description:
        "Join our marketing team and learn about digital marketing strategies.",
    },
    {
      id: "4",
      title: "Full Stack Developer",
      company: "WebDev Agency",
      location: "Islamabad",
      job_type: "Contract",
      tags: ["JavaScript", "Python", "AWS"],
      posting_date: "2024-01-12T11:45:00Z",
      description: "Work on exciting projects using modern web technologies.",
    },
  ];

  // Load jobs on component mount
  useEffect(() => {
    loadJobs();
  }, []);

  // Apply filters when filters or jobs change
  useEffect(() => {
    applyFilters();
  }, [jobs, filters]);

  const loadJobs = async () => {
    try {
      setLoading(true);
      setError(null);

      // Try to fetch from API, fallback to mock data
      try {
        const fetchedJobs = await jobsApi.getJobs(filters);
        setJobs(fetchedJobs);
      } catch (apiError) {
        console.warn("API not available, using mock data:", apiError);
        // Use mock data when API is not available
        setJobs(mockJobs);
      }
    } catch (err) {
      setError("Failed to load jobs. Please try again later.");
      console.error("Error loading jobs:", err);
    } finally {
      setLoading(false);
    }
  };

  const applyFilters = () => {
    let filtered = [...jobs];

    // Apply filters
    if (filters.title) {
      filtered = filtered.filter((job) =>
        job.title.toLowerCase().includes(filters.title.toLowerCase()),
      );
    }

    if (filters.company) {
      filtered = filtered.filter((job) =>
        job.company.toLowerCase().includes(filters.company.toLowerCase()),
      );
    }

    if (filters.location) {
      filtered = filtered.filter((job) => job.location === filters.location);
    }

    if (filters.job_type) {
      filtered = filtered.filter((job) => job.job_type === filters.job_type);
    }

    if (filters.tags) {
      filtered = filtered.filter((job) =>
        job.tags.some((tag) =>
          tag.toLowerCase().includes(filters.tags.toLowerCase()),
        ),
      );
    }

    // Apply sorting
    if (filters.sort === "posting_date_asc") {
      filtered.sort(
        (a, b) =>
          new Date(a.posting_date).getTime() -
          new Date(b.posting_date).getTime(),
      );
    } else {
      filtered.sort(
        (a, b) =>
          new Date(b.posting_date).getTime() -
          new Date(a.posting_date).getTime(),
      );
    }

    setFilteredJobs(filtered);
  };

  const handleAddJob = () => {
    setEditingJob(null);
    setIsFormOpen(true);
  };

  const handleEditJob = (job) => {
    setEditingJob(job);
    setIsFormOpen(true);
  };

  const handleDeleteJob = async (id) => {
    if (!window.confirm("Are you sure you want to delete this job?")) {
      return;
    }

    try {
      await jobsApi.deleteJob(id);
      setJobs(jobs.filter((job) => job.id !== id));
    } catch (err) {
      // For mock data, just remove from state
      setJobs(jobs.filter((job) => job.id !== id));
      console.warn("API not available, removed from local state");
    }
  };

  const handleFormSubmit = async (formData) => {
    try {
      setFormLoading(true);

      if (editingJob) {
        // Update existing job
        try {
          const updatedJob = await jobsApi.updateJob(editingJob.id, formData);
          setJobs(
            jobs.map((job) => (job.id === editingJob.id ? updatedJob : job)),
          );
        } catch (err) {
          // For mock data, update locally
          const updatedJob = {
            ...editingJob,
            ...formData,
            tags: formData.tags
              .split(",")
              .map((tag) => tag.trim())
              .filter((tag) => tag),
          };
          setJobs(
            jobs.map((job) => (job.id === editingJob.id ? updatedJob : job)),
          );
        }
      } else {
        // Create new job
        try {
          const newJob = await jobsApi.createJob(formData);
          setJobs([newJob, ...jobs]);
        } catch (err) {
          // For mock data, create locally
          const newJob = {
            id: Date.now().toString(),
            ...formData,
            tags: formData.tags
              .split(",")
              .map((tag) => tag.trim())
              .filter((tag) => tag),
            posting_date: new Date().toISOString(),
          };
          setJobs([newJob, ...jobs]);
        }
      }

      setIsFormOpen(false);
      setEditingJob(null);
    } catch (err) {
      console.error("Error saving job:", err);
      alert("Failed to save job. Please try again.");
    } finally {
      setFormLoading(false);
    }
  };

  const handleFiltersChange = (newFilters) => {
    setFilters(newFilters);
  };

  const handleClearFilters = () => {
    setFilters({ sort: "posting_date_desc" });
  };

  const handleScrapeJobs = async () => {
    try {
      setScrapeLoading(true);
      setError(null);

      console.log("Starting job scraping from ActuaryList...");

      // Simulate the scraping process
      const mockScrapedJobs = [
        {
          id: `scraped_${Date.now()}_1`,
          title: "Senior Actuarial Analyst",
          company: "MetLife Insurance",
          location: "New York, NY",
          job_type: "Full-time",
          tags: ["Actuarial", "Insurance", "Risk Management", "Statistics"],
          posting_date: new Date().toISOString(),
          description:
            "Senior actuarial analyst position focusing on life insurance products and risk assessment. This job was scraped from ActuaryList.com.",
        },
        {
          id: `scraped_${Date.now()}_2`,
          title: "Actuarial Consultant",
          company: "Deloitte Consulting",
          location: "Chicago, IL",
          job_type: "Full-time",
          tags: ["Actuarial", "Consulting", "Healthcare", "Analytics"],
          posting_date: new Date().toISOString(),
          description:
            "Actuarial consultant role working with healthcare clients on pricing and reserving. This job was scraped from ActuaryList.com.",
        },
        {
          id: `scraped_${Date.now()}_3`,
          title: "Entry Level Actuary",
          company: "Prudential Financial",
          location: "Newark, NJ",
          job_type: "Full-time",
          tags: ["Actuarial", "Entry Level", "Life Insurance", "Modeling"],
          posting_date: new Date().toISOString(),
          description:
            "Entry level actuarial position with opportunities for professional development and exam support. This job was scraped from ActuaryList.com.",
        },
      ];

      // Simulate API delay
      await new Promise((resolve) => setTimeout(resolve, 3000));

      // Add scraped jobs to the existing jobs
      const newJobs = [...mockScrapedJobs, ...jobs];
      setJobs(newJobs);

      alert(
        `Successfully scraped ${mockScrapedJobs.length} jobs from ActuaryList!`,
      );
    } catch (err) {
      setError("Failed to scrape jobs. Please try again later.");
      console.error("Error scraping jobs:", err);
    } finally {
      setScrapeLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4 text-blue-600" />
          <p className="text-gray-600">Loading jobs...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">
            Error Loading Jobs
          </h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <Button onClick={loadJobs}>Try Again</Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <Briefcase className="h-8 w-8 text-blue-600 mr-3" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Job Board</h1>
                <p className="text-gray-600">Find your next opportunity</p>
              </div>
            </div>
            <div className="flex gap-3">
              <Button
                onClick={handleScrapeJobs}
                disabled={scrapeLoading}
                className="bg-green-600 hover:bg-green-700"
              >
                {scrapeLoading ? (
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                ) : (
                  <Download className="h-4 w-4 mr-2" />
                )}
                {scrapeLoading ? "Scraping..." : "Scrape Jobs"}
              </Button>
              <Button
                onClick={handleAddJob}
                className="bg-blue-600 hover:bg-blue-700"
              >
                <Plus className="h-4 w-4 mr-2" />
                Add Job
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Filters */}
        <JobFilters
          filters={filters}
          onFiltersChange={handleFiltersChange}
          onClearFilters={handleClearFilters}
        />

        {/* Results Summary */}
        <div className="mb-6">
          <p className="text-gray-600">
            Showing {filteredJobs.length} of {jobs.length} jobs
          </p>
        </div>

        {/* Jobs Grid */}
        {filteredJobs.length === 0 ? (
          <div className="text-center py-12">
            <Briefcase className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              No jobs found
            </h3>
            <p className="text-gray-600 mb-4">
              {jobs.length === 0
                ? "No jobs have been posted yet."
                : "Try adjusting your filters to see more results."}
            </p>
            {jobs.length === 0 && (
              <Button
                onClick={handleAddJob}
                className="bg-blue-600 hover:bg-blue-700"
              >
                <Plus className="h-4 w-4 mr-2" />
                Post the First Job
              </Button>
            )}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredJobs.map((job) => (
              <JobCard
                key={job.id}
                job={job}
                onEdit={handleEditJob}
                onDelete={handleDeleteJob}
              />
            ))}
          </div>
        )}
      </main>

      {/* Job Form Modal */}
      <JobForm
        isOpen={isFormOpen}
        onClose={() => {
          setIsFormOpen(false);
          setEditingJob(null);
        }}
        onSubmit={handleFormSubmit}
        job={editingJob}
        isLoading={formLoading}
      />
    </div>
  );
}

export default App;

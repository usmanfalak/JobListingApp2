import React from "react";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Search, X } from "lucide-react";

const JOB_TYPES = ["Full-time", "Part-time", "Internship", "Contract"];
const LOCATIONS = ["Lahore", "Karachi", "Islamabad", "Remote", "Hybrid"];
const SORT_OPTIONS = [
  { value: "posting_date_desc", label: "Newest First" },
  { value: "posting_date_asc", label: "Oldest First" },
];

export default function JobFilters({
  filters,
  onFiltersChange,
  onClearFilters,
}) {
  const updateFilter = (key, value) => {
    // Handle special "all" values by converting them to undefined
    const filterValue =
      value === "all-locations" || value === "all-types"
        ? undefined
        : value || undefined;
    onFiltersChange({
      ...filters,
      [key]: filterValue,
    });
  };

  const hasActiveFilters = Object.values(filters).some(
    (value) => value && value !== "posting_date_desc",
  );

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border mb-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">
          Filters & Search
        </h3>
        {hasActiveFilters && (
          <Button
            variant="outline"
            size="sm"
            onClick={onClearFilters}
            className="text-gray-600 hover:text-gray-800"
          >
            <X className="h-4 w-4 mr-1" />
            Clear All
          </Button>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
        {/* Search by Title */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          <Input
            placeholder="Search jobs..."
            value={filters.title || ""}
            onChange={(e) => updateFilter("title", e.target.value)}
            className="pl-10"
          />
        </div>

        {/* Company Filter */}
        <div>
          <Input
            placeholder="Company name"
            value={filters.company || ""}
            onChange={(e) => updateFilter("company", e.target.value)}
          />
        </div>

        {/* Location Filter */}
        <div>
          <Select
            value={filters.location || "all-locations"}
            onValueChange={(value) => updateFilter("location", value)}
          >
            <SelectTrigger>
              <SelectValue placeholder="Location" />
            </SelectTrigger>
            <SelectContent className="bg-white">
              <SelectItem value="all-locations">All Locations</SelectItem>
              {LOCATIONS.map((location) => (
                <SelectItem key={location} value={location}>
                  {location}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Job Type Filter */}
        <div>
          <Select
            value={filters.job_type || "all-types"}
            onValueChange={(value) => updateFilter("job_type", value)}
          >
            <SelectTrigger>
              <SelectValue placeholder="Job Type" />
            </SelectTrigger>
            <SelectContent className="bg-white">
              <SelectItem value="all-types">All Types</SelectItem>
              {JOB_TYPES.map((type) => (
                <SelectItem key={type} value={type}>
                  {type}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Tags Filter */}
        <div>
          <Input
            placeholder="Tags (e.g. React)"
            value={filters.tags || ""}
            onChange={(e) => updateFilter("tags", e.target.value)}
          />
        </div>

        {/* Sort */}
        <div>
          <Select
            value={filters.sort || "posting_date_desc"}
            onValueChange={(value) => updateFilter("sort", value)}
          >
            <SelectTrigger>
              <SelectValue placeholder="Sort by" />
            </SelectTrigger>
            <SelectContent className="bg-white">
              {SORT_OPTIONS.map((option) => (
                <SelectItem key={option.value} value={option.value}>
                  {option.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>
    </div>
  );
}

import { useState } from "react";
import axios from "axios";

const API_BASE = "http://localhost:8000/api/v1";

export default function App() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [history, setHistory] = useState(null);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState("match");
  const [dragOver, setDragOver] = useState(false);

  // ── Handle file selection ──────────────────────────────────────────
  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setResults(null);
    setError(null);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const dropped = e.dataTransfer.files[0];
    if (dropped) {
      setFile(dropped);
      setResults(null);
      setError(null);
    }
  };

  // ── Match against all roles ────────────────────────────────────────
  const handleMatch = async () => {
    if (!file) {
      setError("Please upload a resume first.");
      return;
    }

    setLoading(true);
    setError(null);
    setResults(null);

    const formData = new FormData();
    formData.append("resume", file);
    formData.append("top_n", 9);

    try {
      const res = await axios.post(`${API_BASE}/match/all`, formData);
      setResults(res.data);
    } catch (err) {
      if (err.response?.status === 413) {
        setError("File too large. Maximum size is 5MB.");
      } else if (err.response?.status === 415) {
        setError("Unsupported file type. Upload PDF, DOCX, JPG or PNG.");
      } else {
        setError("Something went wrong. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  };

  // ── Fetch history ──────────────────────────────────────────────────
  const handleHistory = async () => {
    setActiveTab("history");
    try {
      const res = await axios.get(`${API_BASE}/history`);
      setHistory(res.data);
    } catch {
      setError("Failed to load history.");
    }
  };

  // ── Score color ────────────────────────────────────────────────────
  const getScoreColor = (score) => {
    if (score >= 70) return "bg-green-500";
    if (score >= 40) return "bg-yellow-400";
    return "bg-red-400";
  };

  const getScoreText = (score) => {
    if (score >= 70) return "text-green-600";
    if (score >= 40) return "text-yellow-600";
    return "text-red-500";
  };

  const getMedal = (index) => {
    if (index === 0) return "🥇";
    if (index === 1) return "🥈";
    if (index === 2) return "🥉";
    return `#${index + 1}`;
  };

  // ── Render ─────────────────────────────────────────────────────────
  return (
    <div className="min-h-screen bg-gray-50 font-sans">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="max-w-3xl mx-auto flex items-center justify-between">
          <div>
            <h1 className="text-xl font-semibold text-gray-800">
              Resume Skill Matcher
            </h1>
            <p className="text-sm text-gray-500">
              Upload your resume and find your best matching roles
            </p>
          </div>
          <span className="text-xs bg-gray-100 text-gray-500 px-3 py-1 rounded-full">
            v1.0.0
          </span>
        </div>
      </header>

      {/* Tabs */}
      <div className="max-w-3xl mx-auto px-6 mt-6">
        <div className="flex gap-2 border-b border-gray-200">
          <button
            onClick={() => setActiveTab("match")}
            className={`pb-2 px-4 text-sm font-medium border-b-2 transition-all ${
              activeTab === "match"
                ? "border-gray-800 text-gray-800"
                : "border-transparent text-gray-400 hover:text-gray-600"
            }`}
          >
            Match Resume
          </button>
          <button
            onClick={handleHistory}
            className={`pb-2 px-4 text-sm font-medium border-b-2 transition-all ${
              activeTab === "history"
                ? "border-gray-800 text-gray-800"
                : "border-transparent text-gray-400 hover:text-gray-600"
            }`}
          >
            History
          </button>
        </div>
      </div>

      <main className="max-w-3xl mx-auto px-6 py-6">
        {/* ── MATCH TAB ── */}
        {activeTab === "match" && (
          <div className="space-y-6">
            {/* Upload Box */}
            <div
              onDragOver={(e) => {
                e.preventDefault();
                setDragOver(true);
              }}
              onDragLeave={() => setDragOver(false)}
              onDrop={handleDrop}
              className={`border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition-all ${
                dragOver
                  ? "border-gray-400 bg-gray-100"
                  : "border-gray-300 bg-white hover:border-gray-400"
              }`}
              onClick={() => document.getElementById("fileInput").click()}
            >
              <input
                id="fileInput"
                type="file"
                accept=".pdf,.docx,.jpg,.jpeg,.png"
                className="hidden"
                onChange={handleFileChange}
              />
              <div className="text-4xl mb-3">📄</div>
              {file ? (
                <div>
                  <p className="text-gray-800 font-medium">{file.name}</p>
                  <p className="text-gray-400 text-sm mt-1">
                    {(file.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>
              ) : (
                <div>
                  <p className="text-gray-600 font-medium">
                    Drag & drop your resume here
                  </p>
                  <p className="text-gray-400 text-sm mt-1">
                    or click to browse — PDF, DOCX, JPG, PNG (max 5MB)
                  </p>
                </div>
              )}
            </div>

            {/* Error */}
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-600 rounded-lg px-4 py-3 text-sm">
                {error}
              </div>
            )}

            {/* Match Button */}
            <button
              onClick={handleMatch}
              disabled={loading || !file}
              className={`w-full py-3 rounded-xl text-sm font-medium transition-all ${
                loading || !file
                  ? "bg-gray-200 text-gray-400 cursor-not-allowed"
                  : "bg-gray-800 text-white hover:bg-gray-700"
              }`}
            >
              {loading ? "Analyzing resume..." : "Match Now →"}
            </button>

            {/* Loading */}
            {loading && (
              <div className="text-center py-6">
                <div className="inline-block w-8 h-8 border-4 border-gray-200 border-t-gray-800 rounded-full animate-spin" />
                <p className="text-gray-500 text-sm mt-3">
                  Extracting skills and matching roles...
                </p>
              </div>
            )}

            {/* Results */}
            {results && (
              <div className="space-y-4">
                {/* Extracted Skills */}
                <div className="bg-white rounded-xl border border-gray-200 p-5">
                  <h2 className="text-sm font-semibold text-gray-600 uppercase tracking-wide mb-3">
                    Extracted Skills ({results.extracted_skills.length})
                  </h2>
                  <div className="flex flex-wrap gap-2">
                    {results.extracted_skills.map((skill) => (
                      <span
                        key={skill}
                        className="bg-gray-100 text-gray-700 text-xs px-3 py-1 rounded-full"
                      >
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Role Matches */}
                <div className="bg-white rounded-xl border border-gray-200 p-5">
                  <h2 className="text-sm font-semibold text-gray-600 uppercase tracking-wide mb-4">
                    Best Matching Roles
                  </h2>
                  <div className="space-y-5">
                    {results.top_matches.map((role, index) => (
                      <div key={role.role_id}>
                        {/* Role Header */}
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center gap-2">
                            <span className="text-lg">{getMedal(index)}</span>
                            <span className="text-sm font-medium text-gray-800">
                              {role.role_title}
                            </span>
                          </div>
                          <span
                            className={`text-sm font-bold ${getScoreText(role.match_percentage)}`}
                          >
                            {role.match_percentage}%
                          </span>
                        </div>

                        {/* Progress Bar */}
                        <div className="w-full bg-gray-100 rounded-full h-2 mb-3">
                          <div
                            className={`h-2 rounded-full transition-all ${getScoreColor(role.match_percentage)}`}
                            style={{ width: `${role.match_percentage}%` }}
                          />
                        </div>

                        {/* Matched + Missing */}
                        <div className="flex gap-4 text-xs">
                          <div>
                            <span className="text-green-600 font-medium">
                              ✅ Matched:{" "}
                            </span>
                            <span className="text-gray-600">
                              {role.matched_required.length > 0
                                ? role.matched_required.join(", ")
                                : "none"}
                            </span>
                          </div>
                          {role.missing_required.length > 0 && (
                            <div>
                              <span className="text-red-500 font-medium">
                                ❌ Missing:{" "}
                              </span>
                              <span className="text-gray-600">
                                {role.missing_required.join(", ")}
                              </span>
                            </div>
                          )}
                        </div>

                        {/* Divider */}
                        {index < results.top_matches.length - 1 && (
                          <hr className="mt-4 border-gray-100" />
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* ── HISTORY TAB ── */}
        {activeTab === "history" && (
          <div className="bg-white rounded-xl border border-gray-200 p-5">
            <h2 className="text-sm font-semibold text-gray-600 uppercase tracking-wide mb-4">
              Match History ({history?.total || 0})
            </h2>
            {history?.results?.length === 0 ? (
              <p className="text-gray-400 text-sm text-center py-6">
                No history yet. Match a resume first!
              </p>
            ) : (
              <div className="space-y-3">
                {history?.results?.map((r) => (
                  <div
                    key={r.id}
                    className="flex items-center justify-between py-3 border-b border-gray-100 last:border-0"
                  >
                    <div>
                      <p className="text-sm font-medium text-gray-800">
                        {r.filename}
                      </p>
                      <p className="text-xs text-gray-400 mt-0.5">
                        {r.role_title} •{" "}
                        {new Date(r.created_at + "Z").toLocaleString("en-IN", {
                          timeZone: "Asia/Kolkata",
                        })}
                      </p>
                    </div>
                    <span
                      className={`text-sm font-bold ${getScoreText(r.match_percentage)}`}
                    >
                      {r.match_percentage}%
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}

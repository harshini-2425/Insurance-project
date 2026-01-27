import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/Claims.css";

export default function Claims() {
    const token = localStorage.getItem("token");
    const navigate = useNavigate();

    const [activeTab, setActiveTab] = useState("file"); // "file" or "list"
    const [userPolicies, setUserPolicies] = useState([]);
    const [claimsList, setClaimsList] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const [success, setSuccess] = useState("");

    // Form state
    const [selectedPolicy, setSelectedPolicy] = useState("");
    const [claimType, setClaimType] = useState("medical");
    const [incidentDate, setIncidentDate] = useState("");
    const [amountClaimed, setAmountClaimed] = useState("");
    const [description, setDescription] = useState("");
    const [documents, setDocuments] = useState([]);
    const [currentClaimId, setCurrentClaimId] = useState(null);

    if (!token) {
        navigate("/login");
        return null;
    }

    // Load user's policies
    useEffect(() => {
        fetchUserPolicies();
    }, []);

    // Load claims when tab changes to "list"
    useEffect(() => {
        if (activeTab === "list") {
            fetchClaims();
        }
    }, [activeTab]);

    const fetchUserPolicies = async () => {
        try {
            const response = await fetch(
                `http://localhost:8000/user-policies?token=${token}`
            );
            const data = await response.json();
            setUserPolicies(data);
        } catch (err) {
            setError("Failed to load policies");
        }
    };

    const fetchClaims = async () => {
        setLoading(true);
        try {
            const response = await fetch(
                `http://localhost:8000/claims?token=${token}`
            );
            const data = await response.json();
            setClaimsList(data);
        } catch (err) {
            setError("Failed to load claims");
        } finally {
            setLoading(false);
        }
    };

    const handleCreateClaim = async (e) => {
        e.preventDefault();
        setError("");
        setSuccess("");

        if (!selectedPolicy || !claimType || !incidentDate || !amountClaimed) {
            setError("Please fill in all required fields");
            return;
        }

        setLoading(true);
        try {
            const response = await fetch(`http://localhost:8000/claims?token=${token}`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                body: new URLSearchParams({
                    user_policy_id: selectedPolicy,
                    claim_type: claimType,
                    incident_date: incidentDate,
                    amount_claimed: amountClaimed,
                    description: description,
                }),
            });

            const data = await response.json();

            if (!response.ok) {
                setError(data.detail || "Failed to create claim");
                return;
            }

            setCurrentClaimId(data.id);
            setSuccess(`Claim created: ${data.claim_number}. Upload documents to continue.`);
            // Reset form
            setSelectedPolicy("");
            setClaimType("medical");
            setIncidentDate("");
            setAmountClaimed("");
            setDescription("");
        } catch (err) {
            setError("Error creating claim: " + err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleAddDocument = () => {
        setDocuments([...documents, { type: "prescription", file: null, fileName: "" }]);
    };

    const handleRemoveDocument = (index) => {
        setDocuments(documents.filter((_, i) => i !== index));
    };

    const handleDocumentChange = (index, field, value) => {
        const newDocs = [...documents];
        newDocs[index][field] = value;
        setDocuments(newDocs);
    };

    const handleUploadDocuments = async () => {
        if (!currentClaimId) {
            setError("No claim ID found");
            return;
        }

        if (documents.length === 0) {
            setError("Please add at least one document");
            return;
        }

        setLoading(true);
        try {
            for (const doc of documents) {
                if (!doc.fileName) {
                    setError("Please provide file names for all documents");
                    return;
                }

                const response = await fetch(
                    `http://localhost:8000/claims/${currentClaimId}/documents?token=${token}`,
                    {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/x-www-form-urlencoded",
                        },
                        body: new URLSearchParams({
                            doc_type: doc.type,
                            file_name: doc.fileName,
                            file_content: "file_reference", // For now, just store reference
                        }),
                    }
                );

                if (!response.ok) {
                    const data = await response.json();
                    setError(data.detail || "Failed to upload document");
                    return;
                }
            }

            setSuccess("Documents uploaded successfully!");
            setDocuments([]);
        } catch (err) {
            setError("Error uploading documents: " + err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleSubmitClaim = async () => {
        if (!currentClaimId) {
            setError("No claim to submit");
            return;
        }

        setLoading(true);
        try {
            const response = await fetch(
                `http://localhost:8000/claims/${currentClaimId}/submit?token=${token}`,
                {
                    method: "PUT",
                }
            );

            const data = await response.json();

            if (!response.ok) {
                setError(data.detail || "Failed to submit claim");
                return;
            }

            setSuccess("Claim submitted successfully!");
            setCurrentClaimId(null);
            // Reload claims list
            fetchClaims();
            setActiveTab("list");
        } catch (err) {
            setError("Error submitting claim: " + err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="claims-container">
            <div className="claims-header">
                <h1>📋 Insurance Claims</h1>
                <p>File a claim and track its status</p>
            </div>

            <div className="claims-tabs">
                <button
                    className={`tab-btn ${activeTab === "file" ? "active" : ""}`}
                    onClick={() => setActiveTab("file")}
                >
                    📝 File Claim
                </button>
                <button
                    className={`tab-btn ${activeTab === "list" ? "active" : ""}`}
                    onClick={() => setActiveTab("list")}
                >
                    📊 My Claims
                </button>
            </div>

            {error && <div className="alert alert-error">{error}</div>}
            {success && <div className="alert alert-success">{success}</div>}

            {/* File Claim Tab */}
            {activeTab === "file" && (
                <div className="claims-content">
                    <div className="claim-form-card">
                        <h2>File a New Claim</h2>

                        <form onSubmit={handleCreateClaim}>
                            <div className="form-group">
                                <label>Policy *</label>
                                <select
                                    value={selectedPolicy}
                                    onChange={(e) => setSelectedPolicy(e.target.value)}
                                    disabled={loading}
                                >
                                    <option value="">Select a policy</option>
                                    {userPolicies.map((policy) => (
                                        <option key={policy.id} value={policy.id}>
                                            {policy.policy.title} (#{policy.policy_number})
                                        </option>
                                    ))}
                                </select>
                            </div>

                            <div className="form-row">
                                <div className="form-group">
                                    <label>Claim Type *</label>
                                    <select
                                        value={claimType}
                                        onChange={(e) => setClaimType(e.target.value)}
                                        disabled={loading}
                                    >
                                        <option value="medical">Medical</option>
                                        <option value="accident">Accident</option>
                                        <option value="damage">Property Damage</option>
                                        <option value="theft">Theft/Loss</option>
                                        <option value="other">Other</option>
                                    </select>
                                </div>

                                <div className="form-group">
                                    <label>Incident Date *</label>
                                    <input
                                        type="date"
                                        value={incidentDate}
                                        onChange={(e) => setIncidentDate(e.target.value)}
                                        disabled={loading}
                                    />
                                </div>
                            </div>

                            <div className="form-group">
                                <label>Amount Claimed ($) *</label>
                                <input
                                    type="number"
                                    step="0.01"
                                    value={amountClaimed}
                                    onChange={(e) => setAmountClaimed(e.target.value)}
                                    disabled={loading}
                                    placeholder="0.00"
                                />
                            </div>

                            <div className="form-group">
                                <label>Description</label>
                                <textarea
                                    value={description}
                                    onChange={(e) => setDescription(e.target.value)}
                                    disabled={loading}
                                    placeholder="Describe the incident..."
                                    rows="4"
                                />
                            </div>

                            <button type="submit" className="btn btn-primary" disabled={loading}>
                                {loading ? "Creating..." : "Create Claim"}
                            </button>
                        </form>
                    </div>

                    {/* Document Upload */}
                    {currentClaimId && (
                        <div className="claim-documents-card">
                            <h2>📁 Upload Documents</h2>
                            <p className="card-subtitle">
                                Upload supporting documents (prescriptions, receipts, invoices, etc.)
                            </p>

                            {documents.map((doc, index) => (
                                <div key={index} className="document-item">
                                    <select
                                        value={doc.type}
                                        onChange={(e) => handleDocumentChange(index, "type", e.target.value)}
                                    >
                                        <option value="prescription">Prescription</option>
                                        <option value="receipt">Receipt</option>
                                        <option value="invoice">Invoice</option>
                                        <option value="report">Report</option>
                                        <option value="other">Other</option>
                                    </select>

                                    <input
                                        type="text"
                                        placeholder="File name"
                                        value={doc.fileName}
                                        onChange={(e) => handleDocumentChange(index, "fileName", e.target.value)}
                                    />

                                    <button
                                        type="button"
                                        className="btn btn-secondary btn-small"
                                        onClick={() => handleRemoveDocument(index)}
                                    >
                                        ✕
                                    </button>
                                </div>
                            ))}

                            <div className="document-actions">
                                <button
                                    type="button"
                                    className="btn btn-secondary"
                                    onClick={handleAddDocument}
                                    disabled={loading}
                                >
                                    + Add Document
                                </button>

                                {documents.length > 0 && (
                                    <button
                                        type="button"
                                        className="btn btn-success"
                                        onClick={handleUploadDocuments}
                                        disabled={loading}
                                    >
                                        {loading ? "Uploading..." : "Upload Documents"}
                                    </button>
                                )}
                            </div>

                            {documents.length > 0 && (
                                <button
                                    type="button"
                                    className="btn btn-primary"
                                    onClick={handleSubmitClaim}
                                    disabled={loading}
                                >
                                    {loading ? "Submitting..." : "Submit Claim"}
                                </button>
                            )}
                        </div>
                    )}
                </div>
            )}

            {/* Claims List Tab */}
            {activeTab === "list" && (
                <div className="claims-content">
                    {loading ? (
                        <p className="loading">Loading claims...</p>
                    ) : claimsList.length === 0 ? (
                        <p className="no-data">No claims filed yet</p>
                    ) : (
                        <div className="claims-list">
                            {claimsList.map((claim) => (
                                <div key={claim.id} className="claim-card">
                                    <div className="claim-header">
                                        <h3>{claim.policy.title}</h3>
                                        <span className={`status-badge status-${claim.status}`}>
                                            {claim.status.replace("_", " ")}
                                        </span>
                                    </div>

                                    <div className="claim-details">
                                        <div className="detail-row">
                                            <span className="label">Claim #:</span>
                                            <span className="value">{claim.claim_number}</span>
                                        </div>
                                        <div className="detail-row">
                                            <span className="label">Type:</span>
                                            <span className="value">{claim.claim_type}</span>
                                        </div>
                                        <div className="detail-row">
                                            <span className="label">Amount:</span>
                                            <span className="value">${claim.amount_claimed.toFixed(2)}</span>
                                        </div>
                                        <div className="detail-row">
                                            <span className="label">Incident Date:</span>
                                            <span className="value">{claim.incident_date}</span>
                                        </div>
                                        <div className="detail-row">
                                            <span className="label">Documents:</span>
                                            <span className="value">{claim.documents_count} uploaded</span>
                                        </div>
                                        <div className="detail-row">
                                            <span className="label">Filed:</span>
                                            <span className="value">
                                                {new Date(claim.created_at).toLocaleDateString()}
                                            </span>
                                        </div>
                                    </div>

                                    <div className="claim-actions">
                                        <button className="btn btn-secondary btn-small">
                                            View Details
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}

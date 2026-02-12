import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/Claims.css";

// Document requirements mapping
const DOCUMENT_REQUIREMENTS = {
    "health": {
        name: "Health Claim",
        icon: "🏥",
        documents: ["medical_report", "hospital_bills", "discharge_summary"]
    },
    "accident": {
        name: "Accident / Auto Claim",
        icon: "🚗",
        documents: ["accident_report", "police_fir", "repair_estimate"]
    },
    "life": {
        name: "Life Claim",
        icon: "❤️",
        documents: ["death_certificate", "nominee_id"]
    },
    "travel": {
        name: "Travel Claim",
        icon: "✈️",
        documents: ["travel_tickets", "delay_proof"]
    },
    "home": {
        name: "Home/Property Claim",
        icon: "🏠",
        documents: ["accident_report", "police_report", "photos", "repair_estimate"]
    }
};

const DOC_TYPE_LABELS = {
    "medical_report": "Medical Report",
    "hospital_bills": "Hospital Bills",
    "discharge_summary": "Discharge Summary",
    "accident_report": "Accident Report",
    "police_fir": "Police FIR",
    "police_report": "Police Report",
    "repair_estimate": "Repair Estimate",
    "death_certificate": "Death Certificate",
    "nominee_id": "Nominee ID Proof",
    "travel_tickets": "Travel Tickets",
    "delay_proof": "Delay/Cancellation Proof",
    "photos": "Photographs",
    "other": "Other Document"
};

function ClaimsPage() {
    const token = localStorage.getItem("token");
    const navigate = useNavigate();

    const [activeTab, setActiveTab] = useState("list");
    const [userPolicies, setUserPolicies] = useState([]);
    const [claimsList, setClaimsList] = useState([]);
    const [selectedClaim, setSelectedClaim] = useState(null);
    const [loadingDetail, setLoadingDetail] = useState(false);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const [success, setSuccess] = useState("");

    // Form state
    const [formData, setFormData] = useState({
        userPolicyId: "",
        claimType: "",
        incidentDate: "",
        amountClaimed: "",
        description: ""
    });
    const [uploadedFiles, setUploadedFiles] = useState([]);
    const [currentClaimId, setCurrentClaimId] = useState(null);
    const [wizardStep, setWizardStep] = useState(1);

    // Load user's policies and claims
    useEffect(() => {
        if (!token) {
            navigate("/login");
            return;
        }
        fetchUserPolicies();
        if (activeTab === "list") fetchClaims();
    }, [activeTab, token, navigate]);

    const fetchUserPolicies = async () => {
        try {
            const response = await fetch(
                `http://localhost:8000/user-policies?token=${token}`
            );
            if (!response.ok) throw new Error("Failed to fetch policies");
            const data = await response.json();
            setUserPolicies(data);
        } catch (err) {
            console.error("Error:", err);
            setError("Failed to load your policies");
        }
    };

    const fetchClaims = async () => {
        setLoading(true);
        try {
            const response = await fetch(
                `http://localhost:8000/claims?token=${token}`
            );
            if (!response.ok) throw new Error("Failed to fetch claims");
            const data = await response.json();
            setClaimsList(data.claims || []);
        } catch (err) {
            console.error("Error:", err);
            setError("Failed to load claims");
        } finally {
            setLoading(false);
        }
    };

    const fetchClaimDetail = async (claimId) => {
        try {
            setLoadingDetail(true);
            const response = await fetch(
                `http://localhost:8000/claims/${claimId}?token=${token}`
            );
            if (!response.ok) throw new Error("Failed to fetch claim details");
            const data = await response.json();
            setSelectedClaim(data);
        } catch (err) {
            console.error("Error:", err);
            setError("Failed to load claim details");
        } finally {
            setLoadingDetail(false);
        }
    };

    const handleFormChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: name === "amountClaimed" ? (value ? parseFloat(value) : "") : value
        }));
        setError("");
    };

    const handleFileInputChange = (e, docType) => {
        const file = e.target.files?.[0];
        if (!file) return;

        // Validate file type
        const validTypes = ["application/pdf", "image/jpeg", "image/png"];
        if (!validTypes.includes(file.type)) {
            setError("Only PDF, JPG, and PNG files are allowed");
            return;
        }

        // Validate file size (5MB max)
        if (file.size > 5 * 1024 * 1024) {
            setError("File size must be less than 5MB");
            return;
        }

        setUploadedFiles(prev => {
            const filtered = prev.filter(f => f.docType !== docType);
            return [...filtered, { docType, fileName: file.name, file }];
        });
        setError("");
    };

    const handleRemoveFile = (docType) => {
        setUploadedFiles(prev => prev.filter(f => f.docType !== docType));
    };

    const isStep1Valid = () => {
        return formData.userPolicyId && formData.claimType &&
            formData.incidentDate && formData.amountClaimed;
    };

    const isStep2Valid = () => {
        const requiredDocs = DOCUMENT_REQUIREMENTS[formData.claimType]?.documents || [];
        const uploadedDocTypes = new Set(uploadedFiles.map(f => f.docType));
        return requiredDocs.length > 0 && uploadedFiles.length >= requiredDocs.length &&
            requiredDocs.every(doc => uploadedDocTypes.has(doc));
    };

    const handleCreateClaim = async (e) => {
        e.preventDefault();
        setError("");

        if (!isStep1Valid()) {
            setError("Please fill in all required fields");
            return;
        }

        setLoading(true);
        try {
            const response = await fetch(
                `http://localhost:8000/claims?token=${token}`,
                {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        user_policy_id: parseInt(formData.userPolicyId),
                        claim_type: formData.claimType,
                        incident_date: formData.incidentDate,
                        amount_claimed: parseFloat(formData.amountClaimed),
                        description: formData.description || null
                    })
                }
            );

            if (!response.ok) {
                const data = await response.json();
                setError(data.detail || "Failed to create claim");
                return;
            }

            const data = await response.json();
            setCurrentClaimId(data.id);
            setSuccess(`Claim created: ${data.claim_number}`);
            setWizardStep(2);
        } catch (err) {
            setError("Error creating claim: " + err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleUploadDocuments = async () => {
        if (uploadedFiles.length === 0) {
            setError("Please upload at least one document");
            return;
        }

        setLoading(true);
        try {
            for (const fileData of uploadedFiles) {
                const formDataObj = new FormData();
                formDataObj.append("file", fileData.file);
                formDataObj.append("doc_type", fileData.docType);

                const response = await fetch(
                    `http://localhost:8000/claims/${currentClaimId}/documents?token=${token}&doc_type=${fileData.docType}`,
                    {
                        method: "POST",
                        body: formDataObj
                    }
                );

                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({}));
                    setError(errorData.detail || `Failed to upload ${fileData.fileName}`);
                    return;
                }
            }

            setSuccess("✅ Documents uploaded successfully! Proceeding to review...");
            setTimeout(() => setWizardStep(3), 1000);
        } catch (err) {
            setError("Error uploading documents: " + err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleSubmitClaim = async () => {
        setLoading(true);
        try {
            const response = await fetch(
                `http://localhost:8000/claims/${currentClaimId}/submit?token=${token}`,
                { method: "POST" }
            );

            if (!response.ok) {
                const data = await response.json();
                setError(data.detail || "Failed to submit claim");
                return;
            }

            const data = await response.json();
            setSuccess("✅ Claim submitted successfully! You can track status in My Claims.");
            setTimeout(() => {
                resetWizard();
                setActiveTab("list");
                fetchClaims();
            }, 2500);
        } catch (err) {
            setError("Error submitting claim: " + err.message);
        } finally {
            setLoading(false);
        }
    };

    const resetWizard = () => {
        setCurrentClaimId(null);
        setWizardStep(1);
        setFormData({
            userPolicyId: "",
            claimType: "",
            incidentDate: "",
            amountClaimed: "",
            description: ""
        });
        setUploadedFiles([]);
        setError("");
        setSuccess("");
    };

    const handleSubmitDraftClaim = async (claimId) => {
        setLoading(true);
        try {
            const response = await fetch(
                `http://localhost:8000/claims/${claimId}/submit?token=${token}`,
                { method: "POST" }
            );

            if (!response.ok) {
                const data = await response.json();
                setError(data.detail || "Failed to submit claim");
                return;
            }

            setSuccess("✅ Claim submitted successfully!");
            await fetchClaimDetail(claimId);
        } catch (err) {
            setError("Error submitting claim: " + err.message);
        } finally {
            setLoading(false);
        }
    };

    const selectedPolicyData = userPolicies.find(p => p.id === parseInt(formData.userPolicyId));
    const claimTypeInfo = DOCUMENT_REQUIREMENTS[formData.claimType];
    const requiredDocs = claimTypeInfo?.documents || [];

    // ========== RENDER ==========
    if (!token) {
        return (
            <div style={{
                minHeight: "100vh",
                background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                padding: "20px"
            }}>
                <div style={{ color: "white", fontSize: "18px" }}>⏳ Redirecting to login...</div>
            </div>
        );
    }

    return (
        <div className="claims-container">
            <div className="claims-header">
                <h1>📋 Insurance Claims</h1>
                <p>File and track your insurance claims</p>
            </div>

            <div className="claims-tabs">
                <button
                    className={`tab-btn ${activeTab === "file" ? "active" : ""}`}
                    onClick={() => { setActiveTab("file"); setSelectedClaim(null); }}
                >
                    📝 File Claim
                </button>
                <button
                    className={`tab-btn ${activeTab === "list" ? "active" : ""}`}
                    onClick={() => { setActiveTab("list"); setSelectedClaim(null); }}
                >
                    📊 My Claims
                </button>
            </div>

            {error && (
                <div className="alert alert-error">
                    <span>⚠️ {error}</span>
                    <button onClick={() => setError("")}>✕</button>
                </div>
            )}
            {success && (
                <div className="alert alert-success">
                    <span>{success}</span>
                    <button onClick={() => setSuccess("")}>✕</button>
                </div>
            )}

            {/* File Claim Tab */}
            {activeTab === "file" && (
                <div className="claims-content">
                    {currentClaimId === null ? (
                        // Step 1: Create Claim
                        <div className="claim-form-card">
                            <h2>📝 Step 1: Select Policy & Claim Details</h2>
                            <form onSubmit={handleCreateClaim}>
                                {/* Policy Selection */}
                                <div className="form-group">
                                    <label>Select Policy *</label>
                                    {userPolicies.length === 0 ? (
                                        <div className="alert alert-info">
                                            You don't have any active policies to claim.{" "}
                                            <button
                                                type="button"
                                                className="btn btn-link"
                                                onClick={() => navigate("/browse")}
                                            >
                                                Browse and purchase a policy
                                            </button>
                                        </div>
                                    ) : (
                                        <>
                                            <select
                                                name="userPolicyId"
                                                value={formData.userPolicyId}
                                                onChange={handleFormChange}
                                                disabled={loading}
                                            >
                                                <option value="">-- Select a policy --</option>
                                                {userPolicies.map((policy) => (
                                                    <option key={policy.id} value={policy.id}>
                                                        {policy.policy.title} (#{policy.policy_number})
                                                    </option>
                                                ))}
                                            </select>
                                            {selectedPolicyData && (
                                                <div className="selected-policy-info">
                                                    <span>Policy Number: {selectedPolicyData.policy_number}</span>
                                                    <span>Type: {selectedPolicyData.policy.policy_type}</span>
                                                    <span>Status: {selectedPolicyData.status}</span>
                                                </div>
                                            )}
                                        </>
                                    )}
                                </div>

                                {/* Claim Type */}
                                <div className="form-group">
                                    <label>Claim Type *</label>
                                    <select
                                        name="claimType"
                                        value={formData.claimType}
                                        onChange={handleFormChange}
                                        disabled={loading}
                                    >
                                        <option value="">-- Select claim type --</option>
                                        {Object.entries(DOCUMENT_REQUIREMENTS).map(([key, value]) => (
                                            <option key={key} value={key}>
                                                {value.icon} {value.name}
                                            </option>
                                        ))}
                                    </select>
                                    {claimTypeInfo && (
                                        <p className="form-hint">
                                            Required documents: {requiredDocs.map(d => DOC_TYPE_LABELS[d]).join(", ")}
                                        </p>
                                    )}
                                </div>

                                {/* Incident Date & Amount */}
                                <div className="form-row">
                                    <div className="form-group">
                                        <label>Incident Date *</label>
                                        <input
                                            type="date"
                                            name="incidentDate"
                                            value={formData.incidentDate}
                                            onChange={handleFormChange}
                                            disabled={loading}
                                            max={new Date().toISOString().split('T')[0]}
                                        />
                                    </div>

                                    <div className="form-group">
                                        <label>Amount Claimed (₹) *</label>
                                        <input
                                            type="number"
                                            name="amountClaimed"
                                            value={formData.amountClaimed}
                                            onChange={handleFormChange}
                                            disabled={loading}
                                            min="0"
                                            step="1000"
                                            placeholder="0"
                                        />
                                    </div>
                                </div>

                                {/* Description */}
                                <div className="form-group">
                                    <label>Description (Optional)</label>
                                    <textarea
                                        name="description"
                                        value={formData.description}
                                        onChange={handleFormChange}
                                        disabled={loading}
                                        placeholder="Describe the incident in detail..."
                                        rows="3"
                                    />
                                </div>

                                {/* Validation Message */}
                                {!isStep1Valid() && (
                                    <div className="alert alert-warning">
                                        ⚠️ Please fill in all required fields marked with *
                                    </div>
                                )}

                                <button
                                    type="submit"
                                    className="btn btn-primary"
                                    disabled={loading || !isStep1Valid() || userPolicies.length === 0}
                                >
                                    {loading ? "Creating..." : "Continue to Documents →"}
                                </button>
                            </form>
                        </div>
                    ) : wizardStep === 2 ? (
                        // Step 2: Upload Documents
                        <div className="claim-form-card">
                            <h2>📄 Step 2: Upload Required Documents</h2>

                            <div className="document-requirements">
                                <h3>{claimTypeInfo?.icon} {claimTypeInfo?.name}</h3>
                                <p className="subtitle">Upload all required documents</p>

                                {requiredDocs.map(docType => (
                                    <div key={docType} className="doc-requirement">
                                        <div className="doc-requirement-header">
                                            <label className="doc-label">
                                                {uploadedFiles.find(f => f.docType === docType) ? "✅" : "❌"}{" "}
                                                {DOC_TYPE_LABELS[docType]}
                                            </label>
                                            <span className="doc-type">{docType}</span>
                                        </div>

                                        {uploadedFiles.find(f => f.docType === docType) ? (
                                            <div className="doc-uploaded">
                                                <span>📎 {uploadedFiles.find(f => f.docType === docType)?.fileName}</span>
                                                <button
                                                    type="button"
                                                    className="btn btn-small btn-delete"
                                                    onClick={() => handleRemoveFile(docType)}
                                                >
                                                    ✕ Remove
                                                </button>
                                            </div>
                                        ) : (
                                            <div className="file-input-wrapper">
                                                <input
                                                    id={`file-input-${docType}`}
                                                    type="file"
                                                    accept=".pdf,.jpg,.jpeg,.png"
                                                    onChange={(e) => handleFileInputChange(e, docType)}
                                                    disabled={loading}
                                                />
                                                <label
                                                    htmlFor={`file-input-${docType}`}
                                                    className="file-input-label"
                                                >
                                                    Click to select PDF, JPG, or PNG
                                                </label>
                                            </div>
                                        )}
                                    </div>
                                ))}
                            </div>

                            <div className="upload-status">
                                <p>
                                    Documents uploaded: <strong>{uploadedFiles.length} / {requiredDocs.length}</strong>
                                </p>
                            </div>

                            {!isStep2Valid() && (
                                <div className="alert alert-warning">
                                    ⚠️ Please upload all required documents before continuing
                                </div>
                            )}

                            <div className="form-actions">
                                <button
                                    type="button"
                                    className="btn btn-secondary"
                                    onClick={() => {
                                        if (window.confirm("Going back will lose unsaved documents. Continue?")) {
                                            resetWizard();
                                        }
                                    }}
                                    disabled={loading}
                                >
                                    ← Cancel
                                </button>
                                <button
                                    type="button"
                                    className="btn btn-primary"
                                    onClick={handleUploadDocuments}
                                    disabled={loading || !isStep2Valid()}
                                >
                                    {loading ? "Uploading..." : "Continue to Review →"}
                                </button>
                            </div>
                        </div>
                    ) : (
                        // Step 3: Review & Submit
                        <div className="claim-form-card">
                            <h2>✅ Step 3: Review & Submit</h2>

                            <div className="review-section">
                                <h3>Claim Summary</h3>
                                {selectedPolicyData && (
                                    <>
                                        <div className="review-row">
                                            <span className="label">Policy:</span>
                                            <span className="value">{selectedPolicyData.policy.title}</span>
                                        </div>
                                        <div className="review-row">
                                            <span className="label">Policy Number:</span>
                                            <span className="value">{selectedPolicyData.policy_number}</span>
                                        </div>
                                        <div className="review-row">
                                            <span className="label">Policy Type:</span>
                                            <span className="value">{selectedPolicyData.policy.policy_type}</span>
                                        </div>
                                    </>
                                )}
                                <div className="review-row">
                                    <span className="label">Claim Type:</span>
                                    <span className="value">{claimTypeInfo?.name}</span>
                                </div>
                                <div className="review-row">
                                    <span className="label">Incident Date:</span>
                                    <span className="value">{formData.incidentDate}</span>
                                </div>
                                <div className="review-row">
                                    <span className="label">Amount Claimed:</span>
                                    <span className="value" style={{ color: "#d32f2f", fontWeight: "bold" }}>
                                        ₹{parseFloat(formData.amountClaimed).toLocaleString()}
                                    </span>
                                </div>
                            </div>

                            <div className="review-section">
                                <h3>Uploaded Documents ({uploadedFiles.length})</h3>
                                {uploadedFiles.map((file, idx) => (
                                    <div key={idx} className="review-row">
                                        <span className="label">📎 {DOC_TYPE_LABELS[file.docType]}</span>
                                        <span className="value">{file.fileName}</span>
                                    </div>
                                ))}
                            </div>

                            <div className="alert alert-info">
                                After submission, our team will review your claim within 5-7 business days.
                                We'll notify you about the status via email.
                            </div>

                            <div className="form-actions">
                                <button
                                    type="button"
                                    className="btn btn-secondary"
                                    onClick={() => setWizardStep(2)}
                                    disabled={loading}
                                >
                                    ← Back to Documents
                                </button>
                                <button
                                    type="button"
                                    className="btn btn-primary"
                                    onClick={handleSubmitClaim}
                                    disabled={loading}
                                    style={{ flex: 1 }}
                                >
                                    {loading ? "Submitting..." : "Submit Claim"}
                                </button>
                            </div>
                        </div>
                    )}
                </div>
            )}

            {/* Claims List Tab */}
            {activeTab === "list" && !selectedClaim && (
                <div className="claims-content">
                    {loading ? (
                        <p className="loading">⏳ Loading claims...</p>
                    ) : claimsList.length === 0 ? (
                        <div className="empty-state">
                            <p>📭 No claims filed yet</p>
                            <button className="btn btn-primary" onClick={() => setActiveTab("file")}>
                                File Your First Claim
                            </button>
                        </div>
                    ) : (
                        <div className="claims-list">
                            {claimsList.map((claim) => (
                                <div key={claim.id} className="claim-card">
                                    <div className="claim-header">
                                        <div>
                                            <h3>{claim.claim_number}</h3>
                                            <p className="claim-type">{claim.claim_type.toUpperCase()}</p>
                                        </div>
                                        <span className={`status-badge status-${claim.status}`}>
                                            {claim.status.replace(/_/g, " ").toUpperCase()}
                                        </span>
                                    </div>

                                    <div className="claim-details">
                                        <div className="detail-row">
                                            <span className="label">Amount:</span>
                                            <span className="value">₹{claim.amount_claimed.toLocaleString()}</span>
                                        </div>
                                        <div className="detail-row">
                                            <span className="label">Policy:</span>
                                            <span className="value">{claim.policy?.title || "N/A"}</span>
                                        </div>
                                        <div className="detail-row">
                                            <span className="label">Documents:</span>
                                            <span className="value">{claim.documents_count || 0} file(s)</span>
                                        </div>
                                        <div className="detail-row">
                                            <span className="label">Filed:</span>
                                            <span className="value">{new Date(claim.created_at).toLocaleDateString()}</span>
                                        </div>
                                    </div>

                                    <div className="claim-actions">
                                        <button
                                            className="btn btn-secondary"
                                            onClick={() => {
                                                fetchClaimDetail(claim.id);
                                            }}
                                        >
                                            View Details →
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}

            {/* Claim Detail View */}
            {selectedClaim && (
                <div className="claims-content">
                    {loadingDetail ? (
                        <p className="loading">⏳ Loading claim details...</p>
                    ) : (
                        <>
                            <button
                                className="btn btn-back"
                                onClick={() => {
                                    setSelectedClaim(null);
                                    fetchClaims();
                                }}
                            >
                                ← Back to Claims
                            </button>

                            <div className="claim-detail-card">
                                <div className="detail-header">
                                    <div>
                                        <h2>{selectedClaim.claim_number}</h2>
                                        <p>{selectedClaim.claim_type.toUpperCase()}</p>
                                    </div>
                                    <span className={`status-badge-large status-${selectedClaim.status}`}>
                                        {selectedClaim.status.replace(/_/g, " ").toUpperCase()}
                                    </span>
                                </div>

                                <div className="detail-grid">
                                    <div className="detail-box">
                                        <h3>Claim Information</h3>
                                        <div className="detail-row">
                                            <span className="label">Claim #:</span>
                                            <span className="value">{selectedClaim.claim_number}</span>
                                        </div>
                                        <div className="detail-row">
                                            <span className="label">Amount:</span>
                                            <span className="value">₹{selectedClaim.amount_claimed.toLocaleString()}</span>
                                        </div>
                                        <div className="detail-row">
                                            <span className="label">Incident Date:</span>
                                            <span className="value">{selectedClaim.incident_date}</span>
                                        </div>
                                        <div className="detail-row">
                                            <span className="label">Filed:</span>
                                            <span className="value">{new Date(selectedClaim.created_at).toLocaleDateString()}</span>
                                        </div>
                                    </div>

                                    <div className="detail-box">
                                        <h3>Policy Information</h3>
                                        <div className="detail-row">
                                            <span className="label">Policy:</span>
                                            <span className="value">{selectedClaim.policy?.title || "N/A"}</span>
                                        </div>
                                        <div className="detail-row">
                                            <span className="label">Policy #:</span>
                                            <span className="value">{selectedClaim.policy?.policy_number || "N/A"}</span>
                                        </div>
                                        <div className="detail-row">
                                            <span className="label">Provider:</span>
                                            <span className="value">{selectedClaim.policy?.provider || "N/A"}</span>
                                        </div>
                                        <div className="detail-row">
                                            <span className="label">Premium:</span>
                                            <span className="value">₹{selectedClaim.policy?.premium?.toLocaleString() || "N/A"}</span>
                                        </div>
                                    </div>
                                </div>

                                <div className="documents-section">
                                    <h3>Supporting Documents ({selectedClaim.documents?.length || 0})</h3>
                                    {selectedClaim.documents && selectedClaim.documents.length > 0 ? (
                                        <div className="documents-table">
                                            {selectedClaim.documents.map((doc) => (
                                                <div key={doc.id} className="doc-row">
                                                    <span className="doc-type">📎 {doc.doc_type}</span>
                                                    <span className="doc-file">{doc.file_url}</span>
                                                    <span className="doc-date">{new Date(doc.uploaded_at).toLocaleDateString()}</span>
                                                </div>
                                            ))}
                                        </div>
                                    ) : (
                                        <p className="text-muted">No documents uploaded</p>
                                    )}
                                </div>

                                {selectedClaim.status === "draft" && (
                                    <div className="claim-actions">
                                        {selectedClaim.documents_count === 0 && (
                                            <div className="alert alert-warning">
                                                ⚠️ Upload at least one document before submitting
                                            </div>
                                        )}
                                        <button
                                            className="btn btn-primary"
                                            onClick={() => handleSubmitDraftClaim(selectedClaim.id)}
                                            disabled={loading || selectedClaim.documents_count === 0}
                                        >
                                            {loading ? "Submitting..." : "Submit Claim for Review"}
                                        </button>
                                    </div>
                                )}

                                {selectedClaim.status === "submitted" && (
                                    <div className="alert alert-info">
                                        ℹ️ Your claim is under review. We'll notify you of any updates.
                                    </div>
                                )}

                                {selectedClaim.status === "approved" && (
                                    <div className="alert alert-success">
                                        ✅ Your claim has been approved! Payment will be processed within 7-10 business days.
                                    </div>
                                )}

                                {selectedClaim.status === "rejected" && (
                                    <div className="alert alert-error">
                                        ❌ Your claim has been rejected. Please contact support for more details.
                                    </div>
                                )}
                            </div>
                        </>
                    )}
                </div>
            )}
        </div>
    );
}

export default ClaimsPage;

import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";

export default function PolicyDetails() {
    const { policyId } = useParams();
    const navigate = useNavigate();
    const [policy, setPolicy] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        fetchPolicy();
    }, [policyId]);

    const fetchPolicy = async () => {
        try {
            setLoading(true);
            const res = await fetch(`http://localhost:8000/policies/${policyId}`);
            if (!res.ok) throw new Error("Failed to load policy");
            const data = await res.json();
            setPolicy(data);
            setError("");
        } catch (err) {
            console.error("Error:", err);
            setError("Error loading policy details: " + err.message);
        } finally {
            setLoading(false);
        }
    };

    if (loading) return (
        <div style={{
            minHeight: "100vh",
            background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            padding: "20px"
        }}>
            <div style={{ color: "white", fontSize: "18px" }}>⏳ Loading policy details...</div>
        </div>
    );

    if (error) return (
        <div style={{
            minHeight: "100vh",
            background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            padding: "20px"
        }}>
            <div style={{
                backgroundColor: "white",
                padding: "30px",
                borderRadius: "12px",
                maxWidth: "500px",
                textAlign: "center"
            }}>
                <h2 style={{ color: "#d32f2f", margin: "0 0 15px 0" }}>⚠️ Error</h2>
                <p style={{ color: "#666", marginBottom: "20px" }}>{error}</p>
                <button
                    onClick={() => navigate("/browse")}
                    style={{
                        padding: "10px 20px",
                        backgroundColor: "#667eea",
                        color: "white",
                        border: "none",
                        borderRadius: "8px",
                        cursor: "pointer",
                        fontWeight: "600"
                    }}
                >
                    ← Back to Browse
                </button>
            </div>
        </div>
    );

    if (!policy) return null;

    const getCoverageIcon = (key) => {
        const icons = {
            "Medical": "🏥",
            "Dental": "🦷",
            "Vision": "👁️",
            "Collision": "🚗",
            "Theft": "🔓",
            "Liability": "⚖️",
            "Death Benefit": "💰",
            "Hospitalization": "🏥",
            "Emergency": "🚑",
            "Accidental": "🆘",
            "Buildings": "🏠",
            "Contents": "📦",
            "Flights": "✈️",
            "Luggage": "🧳",
            "Medical Coverage": "🏥"
        };
        return icons[key] || "✓";
    };

    const getCoverageValue = (value) => {
        if (typeof value === "boolean") return value ? "✅ Covered" : "❌ Not Covered";
        if (typeof value === "number") return `$${value.toLocaleString()}`;
        if (typeof value === "string") return value;
        return "Included";
    };

    return (
        <div style={{
            minHeight: "100vh",
            background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
            padding: "clamp(15px, 3vw, 30px)",
            fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
        }}>
            <div style={{ maxWidth: "900px", margin: "0 auto" }}>
                {/* Header */}
                <button
                    onClick={() => navigate("/browse")}
                    style={{
                        padding: "8px 16px",
                        backgroundColor: "rgba(255,255,255,0.2)",
                        color: "white",
                        border: "1px solid rgba(255,255,255,0.3)",
                        borderRadius: "6px",
                        cursor: "pointer",
                        fontWeight: "600",
                        marginBottom: "20px",
                        transition: "all 0.3s ease"
                    }}
                    onMouseEnter={(e) => {
                        e.target.style.backgroundColor = "rgba(255,255,255,0.3)";
                    }}
                    onMouseLeave={(e) => {
                        e.target.style.backgroundColor = "rgba(255,255,255,0.2)";
                    }}
                >
                    ← Back to Browse
                </button>

                {/* Main Content Card */}
                <div style={{
                    backgroundColor: "white",
                    borderRadius: "16px",
                    boxShadow: "0 12px 40px rgba(0,0,0,0.2)",
                    overflow: "hidden"
                }}>
                    {/* Policy Header */}
                    <div style={{
                        background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                        padding: "40px 30px",
                        color: "white"
                    }}>
                        <div style={{ display: "flex", alignItems: "center", gap: "20px", marginBottom: "20px" }}>
                            <div style={{
                                width: "80px",
                                height: "80px",
                                backgroundColor: "rgba(255,255,255,0.2)",
                                borderRadius: "12px",
                                display: "flex",
                                alignItems: "center",
                                justifyContent: "center",
                                fontSize: "40px"
                            }}>
                                {policy.policy_type === "auto" && "🚗"}
                                {policy.policy_type === "health" && "🏥"}
                                {policy.policy_type === "life" && "❤️"}
                                {policy.policy_type === "home" && "🏠"}
                                {policy.policy_type === "travel" && "✈️"}
                            </div>
                            <div>
                                <h1 style={{ margin: "0 0 8px 0", fontSize: "32px", fontWeight: "700" }}>
                                    {policy.title}
                                </h1>
                                <p style={{ margin: "0", fontSize: "16px", opacity: "0.9" }}>
                                    by <strong>{policy.provider?.name || "Insurance Provider"}</strong>
                                </p>
                            </div>
                        </div>
                    </div>

                    {/* Key Details */}
                    <div style={{ padding: "40px 30px", borderBottom: "1px solid #eee" }}>
                        <h2 style={{ margin: "0 0 25px 0", color: "#333", fontSize: "20px", fontWeight: "600" }}>
                            📊 Premium & Terms
                        </h2>
                        <div style={{
                            display: "grid",
                            gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
                            gap: "25px"
                        }}>
                            <div style={{
                                padding: "20px",
                                backgroundColor: "#f8f9ff",
                                borderRadius: "12px",
                                textAlign: "center",
                                borderLeft: "4px solid #667eea"
                            }}>
                                <p style={{ margin: "0 0 10px 0", color: "#999", fontSize: "13px", fontWeight: "600", textTransform: "uppercase" }}>
                                    Monthly Premium
                                </p>
                                <p style={{ margin: "0", color: "#667eea", fontSize: "28px", fontWeight: "700" }}>
                                    ${parseFloat(policy.premium).toFixed(2)}
                                </p>
                            </div>

                            <div style={{
                                padding: "20px",
                                backgroundColor: "#f8f9ff",
                                borderRadius: "12px",
                                textAlign: "center",
                                borderLeft: "4px solid #764ba2"
                            }}>
                                <p style={{ margin: "0 0 10px 0", color: "#999", fontSize: "13px", fontWeight: "600", textTransform: "uppercase" }}>
                                    Policy Term
                                </p>
                                <p style={{ margin: "0", color: "#764ba2", fontSize: "28px", fontWeight: "700" }}>
                                    {policy.term_months} months
                                </p>
                            </div>

                            <div style={{
                                padding: "20px",
                                backgroundColor: "#f8f9ff",
                                borderRadius: "12px",
                                textAlign: "center",
                                borderLeft: "4px solid #d32f2f"
                            }}>
                                <p style={{ margin: "0 0 10px 0", color: "#999", fontSize: "13px", fontWeight: "600", textTransform: "uppercase" }}>
                                    Deductible
                                </p>
                                <p style={{ margin: "0", color: "#d32f2f", fontSize: "28px", fontWeight: "700" }}>
                                    ${parseFloat(policy.deductible).toFixed(2)}
                                </p>
                            </div>
                        </div>
                    </div>

                    {/* Coverage Details */}
                    {policy.coverage && Object.keys(policy.coverage).length > 0 && (
                        <div style={{ padding: "40px 30px", borderBottom: "1px solid #eee" }}>
                            <h2 style={{ margin: "0 0 25px 0", color: "#333", fontSize: "20px", fontWeight: "600" }}>
                                🛡️ Coverage Details
                            </h2>
                            <div style={{
                                display: "grid",
                                gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))",
                                gap: "15px"
                            }}>
                                {Object.entries(policy.coverage).map(([key, value]) => (
                                    <div key={key} style={{
                                        padding: "16px",
                                        backgroundColor: "#f5f5f5",
                                        borderRadius: "8px",
                                        borderLeft: "4px solid #667eea",
                                        display: "flex",
                                        alignItems: "center",
                                        gap: "12px"
                                    }}>
                                        <span style={{ fontSize: "20px" }}>{getCoverageIcon(key)}</span>
                                        <div style={{ flex: 1 }}>
                                            <p style={{ margin: "0 0 4px 0", color: "#666", fontSize: "13px", fontWeight: "600" }}>
                                                {key}
                                            </p>
                                            <p style={{ margin: "0", color: "#333", fontSize: "14px", fontWeight: "700" }}>
                                                {getCoverageValue(value)}
                                            </p>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Policy Information */}
                    <div style={{ padding: "40px 30px", borderBottom: "1px solid #eee" }}>
                        <h2 style={{ margin: "0 0 15px 0", color: "#333", fontSize: "20px", fontWeight: "600" }}>
                            ℹ️ Policy Information
                        </h2>
                        <div style={{
                            backgroundColor: "#f9f9f9",
                            padding: "20px",
                            borderRadius: "8px",
                            color: "#666",
                            lineHeight: "1.8"
                        }}>
                            <p style={{ margin: "0 0 15px 0" }}>
                                <strong>Policy Type:</strong> {policy.policy_type?.toUpperCase()}
                            </p>
                            <p style={{ margin: "0 0 15px 0" }}>
                                <strong>Provider:</strong> {policy.provider?.name}
                            </p>
                            <p style={{ margin: "0" }}>
                                This {policy.policy_type} insurance policy provides comprehensive coverage with a monthly premium of <strong>${parseFloat(policy.premium).toFixed(2)}</strong>.
                                The policy has a deductible of <strong>${parseFloat(policy.deductible).toFixed(2)}</strong> and covers a term of <strong>{policy.term_months} months</strong>.
                            </p>
                        </div>
                    </div>

                    {/* Action Buttons */}
                    <div style={{
                        padding: "30px",
                        background: "#f9f9f9",
                        display: "flex",
                        gap: "15px",
                        justifyContent: "center",
                        flexWrap: "wrap"
                    }}>
                        <button
                            onClick={() => navigate("/browse")}
                            style={{
                                padding: "14px 32px",
                                backgroundColor: "#f5f5f5",
                                color: "#667eea",
                                border: "2px solid #667eea",
                                borderRadius: "8px",
                                cursor: "pointer",
                                fontWeight: "600",
                                fontSize: "15px",
                                transition: "all 0.3s ease"
                            }}
                            onMouseEnter={(e) => {
                                e.target.style.backgroundColor = "#667eea";
                                e.target.style.color = "white";
                            }}
                            onMouseLeave={(e) => {
                                e.target.style.backgroundColor = "#f5f5f5";
                                e.target.style.color = "#667eea";
                            }}
                        >
                            ← Back to Policies
                        </button>

                        <button
                            onClick={() => navigate(`/apply/${policy.id}`)}
                            style={{
                                padding: "14px 32px",
                                backgroundColor: "#4CAF50",
                                color: "white",
                                border: "none",
                                borderRadius: "8px",
                                cursor: "pointer",
                                fontWeight: "600",
                                fontSize: "15px",
                                transition: "all 0.3s ease",
                                boxShadow: "0 4px 12px rgba(76, 175, 80, 0.3)"
                            }}
                            onMouseEnter={(e) => {
                                e.target.style.backgroundColor = "#388E3C";
                                e.target.style.boxShadow = "0 6px 16px rgba(76, 175, 80, 0.4)";
                            }}
                            onMouseLeave={(e) => {
                                e.target.style.backgroundColor = "#4CAF50";
                                e.target.style.boxShadow = "0 4px 12px rgba(76, 175, 80, 0.3)";
                            }}
                        >
                            ✅ Apply Now
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}

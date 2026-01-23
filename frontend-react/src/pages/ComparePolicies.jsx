import { useState, useEffect } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";

export default function ComparePolicies() {
    const [searchParams] = useSearchParams();
    const [policies, setPolicies] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const navigate = useNavigate();

    useEffect(() => {
        const ids = searchParams.get("ids");
        if (ids) {
            fetchPolicies(ids);
        }
    }, [searchParams]);

    const fetchPolicies = async (ids) => {
        try {
            setLoading(true);
            const url = `http://localhost:8000/policies/compare?policy_ids=${ids}`;
            console.log("Fetching from:", url);
            const res = await fetch(url);
            if (!res.ok) {
                const errText = await res.text();
                throw new Error(`HTTP ${res.status}: ${errText}`);
            }
            const data = await res.json();
            console.log("Policies loaded:", data);
            setPolicies(data);
            setError("");
        } catch (err) {
            console.error("Error:", err);
            setError("Error loading policies: " + err.message);
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
            <div style={{ color: "white", fontSize: "18px" }}>⏳ Loading policies...</div>
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

    if (policies.length === 0) return (
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
                <h2 style={{ color: "#667eea", margin: "0 0 15px 0" }}>📊 No Policies</h2>
                <p style={{ color: "#666", marginBottom: "20px" }}>No policies selected to compare.</p>
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

    // Get all unique coverage fields
    const allCoverageKeys = new Set();
    policies.forEach(p => {
        if (p.coverage) {
            Object.keys(p.coverage).forEach(key => allCoverageKeys.add(key));
        }
    });

    return (
        <div style={{
            minHeight: "100vh",
            background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
            padding: "clamp(15px, 3vw, 30px)",
            fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
        }}>
            <div style={{ maxWidth: "1400px", margin: "0 auto" }}>
                {/* Header */}
                <div style={{
                    textAlign: "center",
                    color: "white",
                    marginBottom: "30px",
                    paddingTop: "20px"
                }}>
                    <h1 style={{
                        fontSize: "clamp(28px, 7vw, 42px)",
                        marginBottom: "10px",
                        fontWeight: "700",
                        textShadow: "2px 2px 4px rgba(0,0,0,0.2)",
                        margin: "0 0 10px 0"
                    }}>
                        📊 Compare Policies
                    </h1>
                    <p style={{
                        fontSize: "clamp(14px, 2vw, 18px)",
                        opacity: 0.95,
                        margin: "0 0 15px 0",
                        fontWeight: "300"
                    }}>
                        Side-by-side comparison of {policies.length} selected policies
                    </p>
                    <div style={{
                        fontSize: "clamp(13px, 1.8vw, 16px)",
                        backgroundColor: "rgba(255,255,255,0.15)",
                        padding: "15px 20px",
                        borderRadius: "8px",
                        backdropFilter: "blur(10px)",
                        display: "flex",
                        flexWrap: "wrap",
                        justifyContent: "center",
                        gap: "15px",
                        alignItems: "center"
                    }}>
                        {policies.map((policy, idx) => (
                            <span key={policy.id} style={{
                                backgroundColor: "rgba(255,255,255,0.25)",
                                padding: "8px 16px",
                                borderRadius: "20px",
                                fontWeight: "600",
                                display: "flex",
                                alignItems: "center",
                                gap: "8px"
                            }}>
                                {idx + 1}. <strong>{policy.title}</strong>
                                {idx < policies.length - 1 && <span style={{ margin: "0 5px" }}>|</span>}
                            </span>
                        ))}
                    </div>
                </div>

                {/* Back Button */}
                <button
                    onClick={() => navigate("/browse")}
                    style={{
                        marginBottom: "20px",
                        padding: "10px 20px",
                        backgroundColor: "rgba(255,255,255,0.2)",
                        color: "white",
                        border: "2px solid white",
                        borderRadius: "8px",
                        cursor: "pointer",
                        fontSize: "14px",
                        fontWeight: "600",
                        transition: "all 0.3s ease"
                    }}
                    onMouseEnter={(e) => {
                        e.target.style.backgroundColor = "white";
                        e.target.style.color = "#667eea";
                    }}
                    onMouseLeave={(e) => {
                        e.target.style.backgroundColor = "rgba(255,255,255,0.2)";
                        e.target.style.color = "white";
                    }}
                >
                    ← Back to Browse
                </button>

                {/* Comparison Table */}
                <div style={{
                    backgroundColor: "white",
                    borderRadius: "12px",
                    boxShadow: "0 8px 25px rgba(0,0,0,0.15)",
                    overflow: "auto",
                    marginBottom: "20px",
                    width: "fit-content",
                    maxWidth: "100%",
                    margin: "0 auto 20px auto"
                }}>
                    <table style={{
                        borderCollapse: "collapse",
                        backgroundColor: "white",
                        tableLayout: "auto"
                    }}>
                        <thead>
                            <tr style={{ backgroundColor: "#667eea", color: "white" }}>
                                <th style={{ padding: "18px 20px", textAlign: "left", fontWeight: "700", borderRight: "2px solid rgba(255,255,255,0.3)", minWidth: "180px", color: "white", fontSize: "14px", letterSpacing: "0.5px" }}>Feature</th>
                                {policies.map(policy => (
                                    <th key={policy.id} style={{ padding: "18px 20px", textAlign: "center", borderRight: "2px solid rgba(255,255,255,0.3)", color: "white", backgroundColor: "#667eea", minWidth: "200px" }}>
                                        <div>
                                            <strong style={{ display: "block", marginBottom: "6px", fontSize: "15px", color: "white", fontWeight: "700", letterSpacing: "0.3px" }}>
                                                {policy.title}
                                            </strong>
                                            <small style={{ color: "rgba(255,255,255,0.9)", display: "block", fontSize: "12px", fontWeight: "500" }}>
                                                {policy.provider.name}
                                            </small>
                                        </div>
                                    </th>
                                ))}
                            </tr>
                        </thead>
                        <tbody>
                            {/* Premium Row */}
                            <tr style={{ borderBottom: "2px solid #ddd", backgroundColor: "#f9f9f9" }}>
                                <td style={{ padding: "20px", fontWeight: "bold", color: "#333", minWidth: "180px" }}>💰 Monthly Premium</td>
                                {policies.map(policy => (
                                    <td key={policy.id} style={{
                                        padding: "20px",
                                        textAlign: "center",
                                        borderRight: "1px solid #ddd",
                                        backgroundColor: "#e8f5e9",
                                        fontWeight: "bold",
                                        fontSize: "20px",
                                        color: "#4CAF50",
                                        minWidth: "200px"
                                    }}>
                                        ${policy.premium}
                                    </td>
                                ))}
                            </tr>

                            {/* Term Row */}
                            <tr style={{ borderBottom: "1px solid #ddd" }}>
                                <td style={{ padding: "20px", fontWeight: "bold", color: "#333", minWidth: "180px" }}>📅 Term Length</td>
                                {policies.map(policy => (
                                    <td key={policy.id} style={{ padding: "20px", textAlign: "center", borderRight: "1px solid #ddd", minWidth: "200px" }}>
                                        {policy.term_months} months
                                    </td>
                                ))}
                            </tr>

                            {/* Deductible Row */}
                            <tr style={{ borderBottom: "1px solid #ddd", backgroundColor: "#f9f9f9" }}>
                                <td style={{ padding: "20px", fontWeight: "bold", color: "#333", minWidth: "180px" }}>💳 Deductible</td>
                                {policies.map(policy => (
                                    <td key={policy.id} style={{ padding: "20px", textAlign: "center", borderRight: "1px solid #ddd", minWidth: "200px" }}>
                                        ${policy.deductible}
                                    </td>
                                ))}
                            </tr>

                            {/* Coverage Details */}
                            {Array.from(allCoverageKeys).map((key, idx) => (
                                <tr key={key} style={{ borderBottom: "1px solid #ddd", backgroundColor: idx % 2 === 0 ? "white" : "#f9f9f9" }}>
                                    <td style={{ padding: "20px", fontWeight: "bold", color: "#333", textTransform: "capitalize", minWidth: "180px" }}>
                                        📋 {key.replace(/_/g, " ")}
                                    </td>
                                    {policies.map(policy => (
                                        <td key={policy.id} style={{ padding: "20px", textAlign: "center", borderRight: "1px solid #ddd", minWidth: "200px" }}>
                                            {policy.coverage && policy.coverage[key] !== undefined ? (
                                                <>
                                                    {typeof policy.coverage[key] === "boolean" ? (
                                                        <span style={{
                                                            color: policy.coverage[key] ? "#4CAF50" : "#d32f2f",
                                                            fontSize: "20px",
                                                            fontWeight: "bold"
                                                        }}>
                                                            {policy.coverage[key] ? "✅" : "❌"}
                                                        </span>
                                                    ) : (
                                                        <span style={{ fontWeight: "600", color: "#667eea" }}>{policy.coverage[key]}</span>
                                                    )}
                                                </>
                                            ) : (
                                                <span style={{ color: "#999" }}>—</span>
                                            )}
                                        </td>
                                    ))}
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>

                {/* Action Section */}
                <div style={{
                    backgroundColor: "white",
                    padding: "30px",
                    borderRadius: "12px",
                    boxShadow: "0 8px 25px rgba(0,0,0,0.15)",
                    textAlign: "center"
                }}>
                    <h3 style={{ color: "#667eea", marginTop: 0, fontSize: "20px" }}>🎯 Ready to Choose?</h3>
                    <p style={{ color: "#666", marginBottom: "20px" }}>
                        Select a policy below to purchase or get more details.
                    </p>
                    <div style={{ display: "flex", gap: "15px", flexWrap: "wrap", justifyContent: "center" }}>
                        {policies.map(policy => (
                            <button
                                key={policy.id}
                                onClick={() => navigate(`/policy/${policy.id}`)}
                                style={{
                                    padding: "12px 24px",
                                    backgroundColor: "#4CAF50",
                                    color: "white",
                                    border: "none",
                                    borderRadius: "8px",
                                    cursor: "pointer",
                                    fontWeight: "600",
                                    transition: "all 0.3s ease",
                                    boxShadow: "0 4px 12px rgba(76, 175, 80, 0.3)"
                                }}
                                onMouseEnter={(e) => {
                                    e.target.style.transform = "translateY(-2px)";
                                    e.target.style.boxShadow = "0 6px 16px rgba(76, 175, 80, 0.4)";
                                }}
                                onMouseLeave={(e) => {
                                    e.target.style.transform = "translateY(0)";
                                    e.target.style.boxShadow = "0 4px 12px rgba(76, 175, 80, 0.3)";
                                }}
                            >
                                💼 Choose {policy.title}
                            </button>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}

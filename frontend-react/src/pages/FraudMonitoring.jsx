import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

export default function FraudMonitoring() {
    const navigate = useNavigate();
    const [summary, setSummary] = useState(null);
    const [highRiskClaims, setHighRiskClaims] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const token = localStorage.getItem("token");

    useEffect(() => {
        if (!token) {
            navigate("/login");
            return;
        }
        fetchFraudData();
    }, [token, navigate]);

    const fetchFraudData = async () => {
        try {
            setLoading(true);

            // Fetch fraud summary
            const summaryRes = await fetch(
                `http://localhost:8000/fraud/summary?token=${token}`
            );
            if (!summaryRes.ok) throw new Error("Failed to fetch fraud summary");
            const summaryData = await summaryRes.json();
            setSummary(summaryData);

            // Fetch high-risk claims
            const claimsRes = await fetch(
                `http://localhost:8000/fraud/high-risk-claims?token=${token}`
            );
            if (!claimsRes.ok) throw new Error("Failed to fetch high-risk claims");
            const claimsData = await claimsRes.json();
            setHighRiskClaims(claimsData);

            setError("");
        } catch (err) {
            console.error("Error:", err);
            setError("Error loading fraud data: " + err.message);
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
            <div style={{ color: "white", fontSize: "18px" }}>⏳ Loading fraud data...</div>
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
                    onClick={() => navigate("/claims")}
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
                    ← Back
                </button>
            </div>
        </div>
    );

    return (
        <div style={{
            minHeight: "100vh",
            background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
            padding: "clamp(15px, 3vw, 30px)",
            fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
        }}>
            <div style={{ maxWidth: "1200px", margin: "0 auto" }}>
                {/* Header */}
                <div style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    marginBottom: "30px",
                    color: "white"
                }}>
                    <div>
                        <h1 style={{
                            fontSize: "clamp(24px, 5vw, 36px)",
                            margin: "0 0 10px 0"
                        }}>
                            🛡️ Fraud Monitoring Dashboard
                        </h1>
                        <p style={{ margin: "0", opacity: "0.9" }}>Week 7: Fraud Rules & Admin Analytics</p>
                    </div>
                    <button
                        onClick={() => navigate("/claims")}
                        style={{
                            padding: "10px 20px",
                            backgroundColor: "rgba(255,255,255,0.2)",
                            color: "white",
                            border: "1px solid rgba(255,255,255,0.3)",
                            borderRadius: "6px",
                            cursor: "pointer",
                            fontWeight: "600"
                        }}
                    >
                        ← Back
                    </button>
                </div>

                {/* Summary Statistics */}
                {summary && (
                    <div style={{
                        display: "grid",
                        gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
                        gap: "20px",
                        marginBottom: "30px"
                    }}>
                        <div style={{
                            backgroundColor: "white",
                            padding: "25px",
                            borderRadius: "12px",
                            boxShadow: "0 8px 25px rgba(0,0,0,0.15)",
                            borderTop: "4px solid #d32f2f"
                        }}>
                            <p style={{ margin: "0 0 10px 0", color: "#999", fontSize: "12px", fontWeight: "600", textTransform: "uppercase" }}>
                                Total Fraud Flags
                            </p>
                            <p style={{ margin: "0", color: "#d32f2f", fontSize: "28px", fontWeight: "700" }}>
                                {summary.total_flags}
                            </p>
                        </div>

                        <div style={{
                            backgroundColor: "white",
                            padding: "25px",
                            borderRadius: "12px",
                            boxShadow: "0 8px 25px rgba(0,0,0,0.15)",
                            borderTop: "4px solid #f57c00"
                        }}>
                            <p style={{ margin: "0 0 10px 0", color: "#999", fontSize: "12px", fontWeight: "600", textTransform: "uppercase" }}>
                                High Severity
                            </p>
                            <p style={{ margin: "0", color: "#f57c00", fontSize: "28px", fontWeight: "700" }}>
                                {summary.severity_distribution.high}
                            </p>
                        </div>

                        <div style={{
                            backgroundColor: "white",
                            padding: "25px",
                            borderRadius: "12px",
                            boxShadow: "0 8px 25px rgba(0,0,0,0.15)",
                            borderTop: "4px solid #fbc02d"
                        }}>
                            <p style={{ margin: "0 0 10px 0", color: "#999", fontSize: "12px", fontWeight: "600", textTransform: "uppercase" }}>
                                Medium Severity
                            </p>
                            <p style={{ margin: "0", color: "#fbc02d", fontSize: "28px", fontWeight: "700" }}>
                                {summary.severity_distribution.medium}
                            </p>
                        </div>

                        <div style={{
                            backgroundColor: "white",
                            padding: "25px",
                            borderRadius: "12px",
                            boxShadow: "0 8px 25px rgba(0,0,0,0.15)",
                            borderTop: "4px solid #4CAF50"
                        }}>
                            <p style={{ margin: "0 0 10px 0", color: "#999", fontSize: "12px", fontWeight: "600", textTransform: "uppercase" }}>
                                Claims Flagged
                            </p>
                            <p style={{ margin: "0", color: "#4CAF50", fontSize: "28px", fontWeight: "700" }}>
                                {summary.claims_flagged}
                            </p>
                        </div>
                    </div>
                )}

                {/* Top Fraud Rules */}
                {summary && summary.top_fraud_rules.length > 0 && (
                    <div style={{
                        backgroundColor: "white",
                        borderRadius: "12px",
                        boxShadow: "0 8px 25px rgba(0,0,0,0.15)",
                        padding: "30px",
                        marginBottom: "30px"
                    }}>
                        <h2 style={{ margin: "0 0 20px 0", color: "#333", fontSize: "20px", fontWeight: "600" }}>
                            📊 Top Fraud Rules Triggered
                        </h2>
                        <div style={{
                            display: "grid",
                            gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))",
                            gap: "15px"
                        }}>
                            {summary.top_fraud_rules.map((rule, idx) => (
                                <div key={idx} style={{
                                    padding: "15px",
                                    backgroundColor: "#f5f5f5",
                                    borderRadius: "8px",
                                    borderLeft: "4px solid #667eea"
                                }}>
                                    <p style={{ margin: "0 0 8px 0", color: "#666", fontSize: "13px", fontWeight: "600" }}>
                                        {rule.rule}
                                    </p>
                                    <p style={{ margin: "0", color: "#333", fontSize: "20px", fontWeight: "700" }}>
                                        {rule.count} triggers
                                    </p>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* High-Risk Claims Table */}
                {highRiskClaims.length > 0 && (
                    <div style={{
                        backgroundColor: "white",
                        borderRadius: "12px",
                        boxShadow: "0 8px 25px rgba(0,0,0,0.15)",
                        padding: "30px",
                        overflowX: "auto"
                    }}>
                        <h2 style={{ margin: "0 0 20px 0", color: "#333", fontSize: "20px", fontWeight: "600" }}>
                            ⚠️ High-Risk Claims Requiring Review
                        </h2>
                        <table style={{
                            width: "100%",
                            borderCollapse: "collapse",
                            fontSize: "14px"
                        }}>
                            <thead>
                                <tr style={{ borderBottom: "2px solid #eee" }}>
                                    <th style={{
                                        padding: "12px",
                                        textAlign: "left",
                                        color: "#666",
                                        fontWeight: "600",
                                        fontSize: "12px",
                                        textTransform: "uppercase"
                                    }}>Claim #</th>
                                    <th style={{
                                        padding: "12px",
                                        textAlign: "left",
                                        color: "#666",
                                        fontWeight: "600",
                                        fontSize: "12px",
                                        textTransform: "uppercase"
                                    }}>User</th>
                                    <th style={{
                                        padding: "12px",
                                        textAlign: "left",
                                        color: "#666",
                                        fontWeight: "600",
                                        fontSize: "12px",
                                        textTransform: "uppercase"
                                    }}>Type</th>
                                    <th style={{
                                        padding: "12px",
                                        textAlign: "right",
                                        color: "#666",
                                        fontWeight: "600",
                                        fontSize: "12px",
                                        textTransform: "uppercase"
                                    }}>Amount</th>
                                    <th style={{
                                        padding: "12px",
                                        textAlign: "center",
                                        color: "#666",
                                        fontWeight: "600",
                                        fontSize: "12px",
                                        textTransform: "uppercase"
                                    }}>Risk Level</th>
                                    <th style={{
                                        padding: "12px",
                                        textAlign: "center",
                                        color: "#666",
                                        fontWeight: "600",
                                        fontSize: "12px",
                                        textTransform: "uppercase"
                                    }}>High Flags</th>
                                    <th style={{
                                        padding: "12px",
                                        textAlign: "center",
                                        color: "#666",
                                        fontWeight: "600",
                                        fontSize: "12px",
                                        textTransform: "uppercase"
                                    }}>Status</th>
                                </tr>
                            </thead>
                            <tbody>
                                {highRiskClaims.map((claim) => (
                                    <tr key={claim.id} style={{
                                        borderBottom: "1px solid #eee",
                                        hoverBackgroundColor: "#f9f9f9"
                                    }}>
                                        <td style={{
                                            padding: "12px",
                                            color: "#667eea",
                                            fontWeight: "600",
                                            cursor: "pointer"
                                        }}>
                                            {claim.claim_number}
                                        </td>
                                        <td style={{ padding: "12px", color: "#333" }}>
                                            {claim.user_name}
                                        </td>
                                        <td style={{ padding: "12px", color: "#666" }}>
                                            {claim.claim_type}
                                        </td>
                                        <td style={{
                                            padding: "12px",
                                            textAlign: "right",
                                            color: "#d32f2f",
                                            fontWeight: "600"
                                        }}>
                                            ${claim.amount_claimed.toFixed(2)}
                                        </td>
                                        <td style={{
                                            padding: "12px",
                                            textAlign: "center"
                                        }}>
                                            <span style={{
                                                padding: "4px 12px",
                                                borderRadius: "12px",
                                                fontSize: "12px",
                                                fontWeight: "600",
                                                backgroundColor: claim.risk_level === "CRITICAL" ? "#ffebee" :
                                                    claim.risk_level === "HIGH" ? "#fff3e0" : "#f1f8e9",
                                                color: claim.risk_level === "CRITICAL" ? "#d32f2f" :
                                                    claim.risk_level === "HIGH" ? "#f57c00" : "#558b2f"
                                            }}>
                                                {claim.risk_level}
                                            </span>
                                        </td>
                                        <td style={{
                                            padding: "12px",
                                            textAlign: "center",
                                            color: "#d32f2f",
                                            fontWeight: "700"
                                        }}>
                                            {claim.high_severity_flags}
                                        </td>
                                        <td style={{
                                            padding: "12px",
                                            textAlign: "center",
                                            color: "#f57c00",
                                            fontWeight: "600",
                                            textTransform: "uppercase",
                                            fontSize: "12px"
                                        }}>
                                            {claim.status}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}

                {highRiskClaims.length === 0 && (
                    <div style={{
                        backgroundColor: "white",
                        borderRadius: "12px",
                        boxShadow: "0 8px 25px rgba(0,0,0,0.15)",
                        padding: "50px",
                        textAlign: "center"
                    }}>
                        <p style={{ color: "#999", fontSize: "16px", margin: "0" }}>
                            ✅ No high-risk claims at the moment
                        </p>
                    </div>
                )}
            </div>
        </div>
    );
}

import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

export default function BrowsePolicies() {
    const [policies, setPolicies] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [filters, setFilters] = useState({ policy_type: "", provider_id: "", min_premium: "", max_premium: "" });
    const [selectedPolicies, setSelectedPolicies] = useState([]);
    const navigate = useNavigate();
    const token = localStorage.getItem("token");

    // Icon mapping for policy types
    const policyIcons = {
        auto: "🚗",
        health: "🏥",
        life: "❤️",
        home: "🏠",
        travel: "✈️"
    };

    useEffect(() => {
        fetchPolicies();
    }, [filters]);

    const fetchPolicies = async () => {
        try {
            setLoading(true);
            let url = "http://localhost:8000/policies";
            const params = new URLSearchParams();

            if (filters.policy_type) params.append("policy_type", filters.policy_type);
            if (filters.provider_id) params.append("provider_id", filters.provider_id);
            if (filters.min_premium) params.append("min_premium", filters.min_premium);
            if (filters.max_premium) params.append("max_premium", filters.max_premium);

            if (params.toString()) url += "?" + params.toString();

            const res = await fetch(url);
            if (!res.ok) throw new Error("Failed to fetch policies");
            const data = await res.json();
            // Extract policies from paginated response
            const policiesList = data.policies || data || [];
            setPolicies(policiesList);
            setError("");
        } catch (err) {
            setError("Error loading policies: " + err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleCompare = () => {
        if (selectedPolicies.length < 2) {
            alert("Please select at least 2 policies to compare");
            return;
        }
        navigate(`/compare?ids=${selectedPolicies.join(",")}`);
    };

    const handleSelectPolicy = (id) => {
        setSelectedPolicies(prev =>
            prev.includes(id) ? prev.filter(p => p !== id) : [...prev, id]
        );
    };

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
                        🛡️ Browse Insurance Policies
                    </h1>
                    <p style={{
                        fontSize: "clamp(14px, 2vw, 18px)",
                        opacity: 0.95,
                        margin: "0",
                        fontWeight: "300"
                    }}>
                        Find the perfect coverage for your needs
                    </p>
                </div>

                {/* Filters Section */}
                <div style={{
                    backgroundColor: "white",
                    padding: "clamp(15px, 3vw, 25px)",
                    borderRadius: "12px",
                    marginBottom: "30px",
                    boxShadow: "0 8px 20px rgba(0,0,0,0.15)"
                }}>
                    <h2 style={{
                        fontSize: "clamp(16px, 3vw, 20px)",
                        color: "#667eea",
                        margin: "0 0 20px 0",
                        display: "flex",
                        alignItems: "center",
                        gap: "10px",
                        fontWeight: "600"
                    }}>
                        🔍 Filter Policies
                    </h2>

                    <div style={{
                        display: "grid",
                        gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))",
                        gap: "15px"
                    }}>
                        <div>
                            <label style={{
                                display: "block",
                                marginBottom: "8px",
                                fontWeight: "600",
                                color: "#333",
                                fontSize: "14px"
                            }}>
                                📋 Policy Type
                            </label>
                            <select
                                value={filters.policy_type}
                                onChange={e => setFilters({ ...filters, policy_type: e.target.value })}
                                style={{
                                    width: "100%",
                                    padding: "10px",
                                    borderRadius: "6px",
                                    border: "2px solid #ddd",
                                    fontSize: "14px",
                                    fontWeight: "500",
                                    cursor: "pointer",
                                    transition: "all 0.3s ease",
                                    boxSizing: "border-box"
                                }}
                            >
                                <option value="">All Types</option>
                                <option value="auto">🚗 Auto Insurance</option>
                                <option value="health">🏥 Health Insurance</option>
                                <option value="life">❤️ Life Insurance</option>
                                <option value="home">🏠 Home Insurance</option>
                                <option value="travel">✈️ Travel Insurance</option>
                            </select>
                        </div>

                        <div>
                            <label style={{
                                display: "block",
                                marginBottom: "8px",
                                fontWeight: "600",
                                color: "#333",
                                fontSize: "14px"
                            }}>
                                💰 Min Premium
                            </label>
                            <input
                                type="number"
                                placeholder="Min"
                                value={filters.min_premium}
                                onChange={e => setFilters({ ...filters, min_premium: e.target.value })}
                                style={{
                                    width: "100%",
                                    padding: "10px",
                                    borderRadius: "6px",
                                    border: "2px solid #ddd",
                                    fontSize: "14px",
                                    transition: "all 0.3s ease",
                                    boxSizing: "border-box"
                                }}
                            />
                        </div>

                        <div>
                            <label style={{
                                display: "block",
                                marginBottom: "8px",
                                fontWeight: "600",
                                color: "#333",
                                fontSize: "14px"
                            }}>
                                💰 Max Premium
                            </label>
                            <input
                                type="number"
                                placeholder="Max"
                                value={filters.max_premium}
                                onChange={e => setFilters({ ...filters, max_premium: e.target.value })}
                                style={{
                                    width: "100%",
                                    padding: "10px",
                                    borderRadius: "6px",
                                    border: "2px solid #ddd",
                                    fontSize: "14px",
                                    transition: "all 0.3s ease",
                                    boxSizing: "border-box"
                                }}
                            />
                        </div>
                    </div>
                </div>

                {error && (
                    <div style={{
                        color: "#d32f2f",
                        padding: "15px",
                        backgroundColor: "rgba(255,255,255,0.95)",
                        borderRadius: "8px",
                        marginBottom: "20px",
                        border: "2px solid #d32f2f",
                        fontWeight: "500"
                    }}>
                        ⚠️ {error}
                    </div>
                )}

                {loading ? (
                    <div style={{
                        textAlign: "center",
                        color: "white",
                        fontSize: "18px",
                        padding: "40px",
                        backgroundColor: "rgba(255,255,255,0.1)",
                        borderRadius: "12px",
                        backdropFilter: "blur(10px)"
                    }}>
                        ⏳ Loading policies...
                    </div>
                ) : (
                    <>
                        {/* Selection Info & Compare Button */}
                        <div style={{
                            marginBottom: "30px",
                            backgroundColor: "white",
                            padding: "20px",
                            borderRadius: "12px",
                            boxShadow: "0 4px 12px rgba(0,0,0,0.08)"
                        }}>
                            <div style={{
                                display: "flex",
                                justifyContent: "space-between",
                                alignItems: "center",
                                flexWrap: "wrap",
                                gap: "15px"
                            }}>
                                <p style={{
                                    margin: "0",
                                    fontSize: "16px",
                                    fontWeight: "600",
                                    color: "#333"
                                }}>
                                    ✅ Selected: <span style={{ color: "#667eea", fontSize: "18px", fontWeight: "700" }}>{selectedPolicies.length}</span> policies
                                </p>
                                <button
                                    onClick={handleCompare}
                                    disabled={selectedPolicies.length < 2}
                                    style={{
                                        padding: "12px 24px",
                                        backgroundColor: selectedPolicies.length < 2 ? "#ccc" : "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                                        color: "white",
                                        border: "none",
                                        borderRadius: "8px",
                                        cursor: selectedPolicies.length < 2 ? "not-allowed" : "pointer",
                                        fontWeight: "600",
                                        fontSize: "15px",
                                        transition: "all 0.3s ease",
                                        boxShadow: selectedPolicies.length < 2 ? "none" : "0 4px 12px rgba(102, 126, 234, 0.3)"
                                    }}
                                    onMouseEnter={(e) => {
                                        if (selectedPolicies.length >= 2) {
                                            e.target.style.transform = "translateY(-2px)";
                                            e.target.style.boxShadow = "0 6px 16px rgba(102, 126, 234, 0.4)";
                                        }
                                    }}
                                    onMouseLeave={(e) => {
                                        e.target.style.transform = "translateY(0)";
                                        e.target.style.boxShadow = "0 4px 12px rgba(102, 126, 234, 0.3)";
                                    }}
                                >
                                    📊 Compare Selected ({selectedPolicies.length})
                                </button>
                            </div>
                        </div>

                        {/* Policy Cards Grid */}
                        <div style={{
                            display: "grid",
                            gridTemplateColumns: "repeat(auto-fill, minmax(clamp(280px, 90vw, 320px), 1fr))",
                            gap: "20px",
                            marginTop: "20px"
                        }}>
                            {policies.map(policy => (
                                <div
                                    key={policy.id}
                                    style={{
                                        border: selectedPolicies.includes(policy.id) ? "3px solid #fff" : "none",
                                        borderRadius: "12px",
                                        padding: "20px",
                                        backgroundColor: "white",
                                        cursor: "pointer",
                                        transition: "all 0.3s ease",
                                        boxShadow: selectedPolicies.includes(policy.id)
                                            ? "0 12px 28px rgba(0,0,0,0.25)"
                                            : "0 4px 12px rgba(0,0,0,0.1)",
                                        transform: selectedPolicies.includes(policy.id) ? "translateY(-6px) scale(1.02)" : "translateY(0) scale(1)",
                                        background: selectedPolicies.includes(policy.id)
                                            ? "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
                                            : "white",
                                        color: selectedPolicies.includes(policy.id) ? "white" : "black",
                                        display: "flex",
                                        flexDirection: "column"
                                    }}
                                    onClick={() => handleSelectPolicy(policy.id)}
                                    onMouseEnter={(e) => {
                                        if (!selectedPolicies.includes(policy.id)) {
                                            e.currentTarget.style.boxShadow = "0 8px 20px rgba(0,0,0,0.15)";
                                            e.currentTarget.style.transform = "translateY(-4px)";
                                        }
                                    }}
                                    onMouseLeave={(e) => {
                                        if (!selectedPolicies.includes(policy.id)) {
                                            e.currentTarget.style.boxShadow = "0 4px 12px rgba(0,0,0,0.1)";
                                            e.currentTarget.style.transform = "translateY(0)";
                                        }
                                    }}
                                >
                                    <div style={{ display: "flex", alignItems: "start", justifyContent: "space-between", marginBottom: "12px" }}>
                                        <h3 style={{
                                            margin: "0 0 0 0",
                                            fontSize: "clamp(16px, 4vw, 18px)",
                                            flex: 1,
                                            fontWeight: "700"
                                        }}>
                                            {policyIcons[policy.policy_type]} {policy.title}
                                        </h3>
                                    </div>

                                    <p style={{
                                        color: selectedPolicies.includes(policy.id) ? "rgba(255,255,255,0.9)" : "#666",
                                        margin: "0 0 8px 0",
                                        fontSize: "13px"
                                    }}>
                                        <strong>Provider:</strong> {policy.provider.name}
                                    </p>

                                    <p style={{
                                        color: selectedPolicies.includes(policy.id) ? "rgba(255,255,255,0.9)" : "#666",
                                        margin: "0 0 12px 0",
                                        fontSize: "13px"
                                    }}>
                                        <strong>Type:</strong> <span style={{ textTransform: "capitalize" }}>{policy.policy_type}</span>
                                    </p>

                                    <div style={{
                                        fontSize: "clamp(18px, 5vw, 24px)",
                                        fontWeight: "bold",
                                        color: selectedPolicies.includes(policy.id) ? "#fff" : "#667eea",
                                        marginBottom: "12px",
                                        padding: "10px 0",
                                        borderTop: selectedPolicies.includes(policy.id) ? "1px solid rgba(255,255,255,0.3)" : "1px solid #ddd",
                                        borderBottom: selectedPolicies.includes(policy.id) ? "1px solid rgba(255,255,255,0.3)" : "1px solid #ddd"
                                    }}>
                                        💵 ${policy.premium}/month
                                    </div>

                                    <p style={{
                                        color: selectedPolicies.includes(policy.id) ? "rgba(255,255,255,0.9)" : "#666",
                                        margin: "0 0 8px 0",
                                        fontSize: "13px"
                                    }}>
                                        <strong>📅 Term:</strong> {policy.term_months} months
                                    </p>

                                    <p style={{
                                        color: selectedPolicies.includes(policy.id) ? "rgba(255,255,255,0.9)" : "#666",
                                        margin: "0 0 12px 0",
                                        fontSize: "13px"
                                    }}>
                                        <strong>💳 Deductible:</strong> ${policy.deductible}
                                    </p>

                                    {policy.coverage && (
                                        <div style={{
                                            backgroundColor: selectedPolicies.includes(policy.id) ? "rgba(255,255,255,0.2)" : "#f0f0f0",
                                            padding: "10px",
                                            borderRadius: "6px",
                                            marginBottom: "12px",
                                            color: selectedPolicies.includes(policy.id) ? "rgba(255,255,255,0.95)" : "#333"
                                        }}>
                                            <strong style={{ display: "block", marginBottom: "6px" }}>📋 Coverage:</strong>
                                            <ul style={{ margin: "0", paddingLeft: "20px", fontSize: "12px" }}>
                                                {Object.entries(policy.coverage).slice(0, 3).map(([key, value]) => (
                                                    <li key={key} style={{ marginBottom: "4px" }}>
                                                        {key.replace(/_/g, " ")}: {typeof value === "boolean" ? (value ? "✅" : "❌") : value}
                                                    </li>
                                                ))}
                                            </ul>
                                        </div>
                                    )}

                                    <div style={{ display: "flex", gap: "10px", marginTop: "15px" }}>
                                        <button
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                handleSelectPolicy(policy.id);
                                            }}
                                            style={{
                                                flex: 1,
                                                padding: "10px",
                                                backgroundColor: selectedPolicies.includes(policy.id) ? "rgba(255,255,255,0.3)" : "#667eea",
                                                color: "white",
                                                border: "none",
                                                borderRadius: "6px",
                                                cursor: "pointer",
                                                fontWeight: "600",
                                                fontSize: "13px",
                                                transition: "all 0.3s ease"
                                            }}
                                            onMouseEnter={(e) => {
                                                if (!selectedPolicies.includes(policy.id)) {
                                                    e.target.style.backgroundColor = "#764ba2";
                                                }
                                            }}
                                            onMouseLeave={(e) => {
                                                if (!selectedPolicies.includes(policy.id)) {
                                                    e.target.style.backgroundColor = "#667eea";
                                                }
                                            }}
                                        >
                                            {selectedPolicies.includes(policy.id) ? "✅ Selected" : "☑️ Select"}
                                        </button>
                                        <button
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                navigate(`/policy/${policy.id}`);
                                            }}
                                            style={{
                                                flex: 1,
                                                padding: "10px",
                                                backgroundColor: selectedPolicies.includes(policy.id) ? "rgba(255,255,255,0.3)" : "#4CAF50",
                                                color: "white",
                                                border: "none",
                                                borderRadius: "6px",
                                                cursor: "pointer",
                                                fontWeight: "600",
                                                fontSize: "13px",
                                                transition: "all 0.3s ease"
                                            }}
                                            onMouseEnter={(e) => {
                                                if (!selectedPolicies.includes(policy.id)) {
                                                    e.target.style.backgroundColor = "#388E3C";
                                                }
                                            }}
                                            onMouseLeave={(e) => {
                                                if (!selectedPolicies.includes(policy.id)) {
                                                    e.target.style.backgroundColor = "#4CAF50";
                                                }
                                            }}
                                        >
                                            📄 Details
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>

                        {policies.length === 0 && (
                            <div style={{
                                textAlign: "center",
                                padding: "60px 20px",
                                color: "white",
                                backgroundColor: "rgba(255,255,255,0.1)",
                                borderRadius: "12px",
                                backdropFilter: "blur(10px)"
                            }}>
                                <p style={{ fontSize: "24px", margin: "0 0 10px 0" }}>😔 No policies found</p>
                                <p style={{ margin: "0", opacity: "0.9" }}>Try adjusting your filters to see more policies.</p>
                            </div>
                        )}
                    </>
                )}
            </div>
        </div>
    );
}

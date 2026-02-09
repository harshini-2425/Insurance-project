import { useState, useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";

export default function Recommendations() {
    const [recommendations, setRecommendations] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [regenerating, setRegenerating] = useState(false);
    const navigate = useNavigate();
    const [searchParams] = useSearchParams();
    const token = searchParams.get("token") || localStorage.getItem("token");

    useEffect(() => {
        if (token) {
            fetchRecommendations();
        } else {
            setError("No token provided");
            setLoading(false);
        }
    }, [token]);

    const fetchRecommendations = async () => {
        try {
            setLoading(true);
            const url = `http://localhost:8000/recommendations?token=${token}`;
            const res = await fetch(url);

            if (!res.ok) {
                const errText = await res.text();
                throw new Error(`HTTP ${res.status}: ${errText}`);
            }

            const data = await res.json();
            console.log("Recommendations data:", data);

            // Filter out any items without policy data
            const validRecs = data.filter(rec => rec && rec.policy);
            setRecommendations(validRecs);

            if (validRecs.length === 0 && data.length > 0) {
                setError("Some recommendations couldn't be loaded. Please regenerate.");
            } else if (validRecs.length === 0) {
                setError("No recommendations yet. Click 'Regenerate' to generate personalized recommendations.");
            } else {
                setError("");
            }
        } catch (err) {
            console.error("Error:", err);
            setError("Error loading recommendations: " + err.message);
        } finally {
            setLoading(false);
        }
    };

    const regenerateRecommendations = async () => {
        try {
            setRegenerating(true);
            const url = `http://localhost:8000/recommendations/generate?token=${token}`;
            const res = await fetch(url, { method: "POST" });

            if (!res.ok) {
                const errText = await res.text();
                throw new Error(`HTTP ${res.status}: ${errText}`);
            }

            const data = await res.json();
            setRecommendations(data);
            setError("");
        } catch (err) {
            console.error("Error:", err);
            setError("Error regenerating recommendations: " + err.message);
        } finally {
            setRegenerating(false);
        }
    };

    const deleteRecommendation = async (recId) => {
        try {
            const url = `http://localhost:8000/recommendations/${recId}?token=${token}`;
            const res = await fetch(url, { method: "DELETE" });

            if (!res.ok) throw new Error("Failed to delete");

            setRecommendations(prev => prev.filter(r => r.id !== recId));
        } catch (err) {
            console.error("Error:", err);
            setError("Error deleting recommendation");
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
            <div style={{ color: "white", fontSize: "18px" }}>⏳ Loading recommendations...</div>
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
                <h2 style={{ color: "#d32f2f", margin: "0 0 15px 0" }}>⚠️ No Recommendations</h2>
                <p style={{ color: "#666", marginBottom: "20px" }}>{error}</p>
                <div style={{ display: "flex", gap: "10px" }}>
                    <button
                        onClick={regenerateRecommendations}
                        disabled={regenerating}
                        style={{
                            flex: 1,
                            padding: "10px 20px",
                            backgroundColor: regenerating ? "#999" : "#4CAF50",
                            color: "white",
                            border: "none",
                            borderRadius: "8px",
                            cursor: regenerating ? "not-allowed" : "pointer",
                            fontWeight: "600"
                        }}
                    >
                        {regenerating ? "🔄 Generating..." : "🔄 Generate"}
                    </button>
                    <button
                        onClick={() => navigate("/browse")}
                        style={{
                            flex: 1,
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
        </div>
    );

    return (
        <div style={{
            minHeight: "100vh",
            background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
            padding: "clamp(15px, 3vw, 30px)",
            fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
        }}>
            <div style={{ maxWidth: "1000px", margin: "0 auto" }}>
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
                        margin: "0 0 15px 0"
                    }}>
                        ⭐ Your Personalized Recommendations
                    </h1>
                    <p style={{
                        fontSize: "clamp(14px, 2vw, 18px)",
                        opacity: 0.95,
                        margin: "0",
                        fontWeight: "300"
                    }}>
                        {recommendations.length > 0
                            ? `${recommendations.length} recommended policies based on your preferences`
                            : "No recommendations yet. Set your preferences to get started!"}
                    </p>
                </div>

                {/* Action Buttons */}
                <div style={{
                    display: "flex",
                    gap: "15px",
                    justifyContent: "center",
                    marginBottom: "30px",
                    flexWrap: "wrap"
                }}>
                    <button
                        onClick={() => navigate("/profile")}
                        style={{
                            padding: "12px 24px",
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
                        ⚙️ Update Preferences
                    </button>

                    <button
                        onClick={regenerateRecommendations}
                        disabled={regenerating}
                        style={{
                            padding: "12px 24px",
                            backgroundColor: regenerating ? "#999" : "#4CAF50",
                            color: "white",
                            border: "none",
                            borderRadius: "8px",
                            cursor: regenerating ? "not-allowed" : "pointer",
                            fontSize: "14px",
                            fontWeight: "600",
                            transition: "all 0.3s ease"
                        }}
                        onMouseEnter={(e) => {
                            if (!regenerating) {
                                e.target.style.backgroundColor = "#45a049";
                            }
                        }}
                        onMouseLeave={(e) => {
                            if (!regenerating) {
                                e.target.style.backgroundColor = "#4CAF50";
                            }
                        }}
                    >
                        {regenerating ? "🔄 Regenerating..." : "🔄 Regenerate"}
                    </button>
                </div>

                {/* Recommendations List */}
                {recommendations.length > 0 ? (
                    <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
                        {recommendations.map((rec, idx) => {
                            // Handle missing policy data
                            if (!rec.policy) {
                                return null;
                            }

                            return (
                                <div
                                    key={rec.id}
                                    style={{
                                        backgroundColor: "white",
                                        borderRadius: "12px",
                                        padding: "25px",
                                        boxShadow: "0 8px 25px rgba(0,0,0,0.15)",
                                        border: `4px solid ${getScoreColor(rec.score)}`,
                                        position: "relative"
                                    }}
                                >
                                    {/* Rank Badge */}
                                    <div style={{
                                        position: "absolute",
                                        top: "-15px",
                                        left: "30px",
                                        backgroundColor: getScoreColor(rec.score),
                                        color: "white",
                                        width: "50px",
                                        height: "50px",
                                        borderRadius: "50%",
                                        display: "flex",
                                        alignItems: "center",
                                        justifyContent: "center",
                                        fontWeight: "700",
                                        fontSize: "20px",
                                        boxShadow: "0 4px 12px rgba(0,0,0,0.2)"
                                    }}>
                                        #{idx + 1}
                                    </div>

                                    {/* Score */}
                                    <div style={{
                                        position: "absolute",
                                        top: "20px",
                                        right: "20px",
                                        textAlign: "right"
                                    }}>
                                        <div style={{
                                            fontSize: "32px",
                                            fontWeight: "700",
                                            color: getScoreColor(rec.score)
                                        }}>
                                            {rec.score}%
                                        </div>
                                        <div style={{ fontSize: "12px", color: "#999" }}>Match Score</div>
                                    </div>

                                    {/* Policy Details */}
                                    <h3 style={{
                                        margin: "0 0 10px 0",
                                        color: "#333",
                                        fontSize: "22px",
                                        paddingTop: "20px"
                                    }}>
                                        {rec.policy.title}
                                    </h3>

                                    <div style={{
                                        display: "flex",
                                        gap: "20px",
                                        marginBottom: "15px",
                                        flexWrap: "wrap"
                                    }}>
                                        <div>
                                            <span style={{ color: "#999", fontSize: "12px" }}>PROVIDER</span>
                                            <div style={{ color: "#333", fontWeight: "600" }}>
                                                {rec.policy.provider.name}
                                            </div>
                                        </div>
                                        <div>
                                            <span style={{ color: "#999", fontSize: "12px" }}>MONTHLY PREMIUM</span>
                                            <div style={{ color: "#4CAF50", fontWeight: "700", fontSize: "18px" }}>
                                                ${rec.policy.premium}
                                            </div>
                                        </div>
                                        <div>
                                            <span style={{ color: "#999", fontSize: "12px" }}>TERM</span>
                                            <div style={{ color: "#333", fontWeight: "600" }}>
                                                {rec.policy.term_months} months
                                            </div>
                                        </div>
                                        <div>
                                            <span style={{ color: "#999", fontSize: "12px" }}>DEDUCTIBLE</span>
                                            <div style={{ color: "#333", fontWeight: "600" }}>
                                                ${rec.policy.deductible}
                                            </div>
                                        </div>
                                    </div>

                                    {/* Reason */}
                                    {rec.reason && (
                                        <div style={{
                                            backgroundColor: "#f5f5f5",
                                            padding: "15px",
                                            borderRadius: "8px",
                                            color: "#666",
                                            fontSize: "14px",
                                            marginBottom: "15px",
                                            borderLeft: `4px solid ${getScoreColor(rec.score)}`
                                        }}>
                                            <strong style={{ color: "#333" }}>Why recommended:</strong> {rec.reason}
                                        </div>
                                    )}

                                    {/* Action Buttons */}
                                    <div style={{
                                        display: "flex",
                                        gap: "10px",
                                        marginTop: "15px"
                                    }}>
                                        <button
                                            onClick={() => navigate(`/policy/${rec.policy_id}`)}
                                            style={{
                                                flex: 1,
                                                padding: "12px",
                                                backgroundColor: "#667eea",
                                                color: "white",
                                                border: "none",
                                                borderRadius: "6px",
                                                cursor: "pointer",
                                                fontWeight: "600",
                                                transition: "all 0.3s ease"
                                            }}
                                            onMouseEnter={(e) => {
                                                e.target.style.backgroundColor = "#5568d3";
                                            }}
                                            onMouseLeave={(e) => {
                                                e.target.style.backgroundColor = "#667eea";
                                            }}
                                        >
                                            📋 View Details
                                        </button>

                                        <button
                                            onClick={() => deleteRecommendation(rec.id)}
                                            style={{
                                                padding: "12px 20px",
                                                backgroundColor: "#f5f5f5",
                                                color: "#d32f2f",
                                                border: "1px solid #ddd",
                                                borderRadius: "6px",
                                                cursor: "pointer",
                                                fontWeight: "600",
                                                transition: "all 0.3s ease"
                                            }}
                                            onMouseEnter={(e) => {
                                                e.target.style.backgroundColor = "#ffe0e0";
                                            }}
                                            onMouseLeave={(e) => {
                                                e.target.style.backgroundColor = "#f5f5f5";
                                            }}
                                        >
                                            ✕
                                        </button>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                ) : (
                    <div style={{
                        backgroundColor: "white",
                        padding: "60px 20px",
                        borderRadius: "12px",
                        textAlign: "center",
                        boxShadow: "0 8px 25px rgba(0,0,0,0.15)"
                    }}>
                        <h2 style={{ color: "#667eea", margin: "0 0 15px 0" }}>📭 No Recommendations Yet</h2>
                        <p style={{ color: "#666", marginBottom: "25px", fontSize: "16px" }}>
                            Complete your profile preferences to get personalized policy recommendations.
                        </p>
                        <button
                            onClick={() => navigate("/profile")}
                            style={{
                                padding: "12px 30px",
                                backgroundColor: "#4CAF50",
                                color: "white",
                                border: "none",
                                borderRadius: "8px",
                                cursor: "pointer",
                                fontWeight: "600",
                                fontSize: "16px"
                            }}
                        >
                            ⚙️ Set Preferences
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
}

function getScoreColor(score) {
    if (score >= 80) return "#4CAF50";  // Green
    if (score >= 60) return "#FFC107";  // Amber
    if (score >= 40) return "#FF9800";  // Orange
    return "#d32f2f";                   // Red
}

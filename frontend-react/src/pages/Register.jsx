import { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function Register() {
    const [form, setForm] = useState({ name: "", email: "", password: "", dob: "" });
    const [error, setError] = useState("");
    const navigate = useNavigate();

    const submit = async () => {
        try {
            setError("");

            if (!form.name || !form.email || !form.password || !form.dob) {
                setError("Please fill in all fields");
                return;
            }

            const res = await fetch("http://localhost:8000/auth/register", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(form)
            });

            const json = await res.json();

            if (json.access_token) {
                localStorage.setItem("token", json.access_token);
                localStorage.setItem("userId", json.user_id);
                navigate("/browse");
            } else {
                setError(json.detail || "Registration failed");
            }
        } catch (err) {
            setError("Error registering: " + err.message);
        }
    };

    return (
        <div style={{
            minHeight: "100vh",
            background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            padding: "clamp(15px, 3vw, 30px)",
            fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
        }}>
            <div style={{
                maxWidth: "420px",
                width: "100%",
                padding: "clamp(20px, 5vw, 35px)",
                backgroundColor: "white",
                borderRadius: "12px",
                boxShadow: "0 8px 25px rgba(0,0,0,0.15)"
            }}>
                <h1 style={{
                    textAlign: "center",
                    fontSize: "clamp(28px, 6vw, 32px)",
                    color: "#667eea",
                    margin: "0 0 10px 0",
                    fontWeight: "700"
                }}>
                    📋 Create Account
                </h1>
                <p style={{
                    textAlign: "center",
                    fontSize: "14px",
                    color: "#999",
                    margin: "0 0 25px 0"
                }}>
                    Join InsureCompare today
                </p>

                {error && (
                    <div style={{
                        color: "#d32f2f",
                        marginBottom: "20px",
                        padding: "12px",
                        backgroundColor: "#ffebee",
                        borderRadius: "8px",
                        fontSize: "14px",
                        border: "1px solid #d32f2f"
                    }}>
                        ⚠️ {error}
                    </div>
                )}

                <div style={{ marginBottom: "15px" }}>
                    <label style={{ display: "block", marginBottom: "6px", fontWeight: "600", color: "#333", fontSize: "13px" }}>👤 Full Name</label>
                    <input
                        placeholder="John Doe"
                        value={form.name}
                        onChange={e => setForm({ ...form, name: e.target.value })}
                        style={{
                            width: "100%",
                            padding: "10px",
                            borderRadius: "6px",
                            border: "2px solid #ddd",
                            fontSize: "14px",
                            boxSizing: "border-box"
                        }}
                    />
                </div>

                <div style={{ marginBottom: "15px" }}>
                    <label style={{ display: "block", marginBottom: "6px", fontWeight: "600", color: "#333", fontSize: "13px" }}>📧 Email</label>
                    <input
                        type="email"
                        placeholder="you@example.com"
                        value={form.email}
                        onChange={e => setForm({ ...form, email: e.target.value })}
                        style={{
                            width: "100%",
                            padding: "10px",
                            borderRadius: "6px",
                            border: "2px solid #ddd",
                            fontSize: "14px",
                            boxSizing: "border-box"
                        }}
                    />
                </div>

                <div style={{ marginBottom: "15px" }}>
                    <label style={{ display: "block", marginBottom: "6px", fontWeight: "600", color: "#333", fontSize: "13px" }}>🔐 Password</label>
                    <input
                        type="password"
                        placeholder="••••••••"
                        value={form.password}
                        onChange={e => setForm({ ...form, password: e.target.value })}
                        style={{
                            width: "100%",
                            padding: "10px",
                            borderRadius: "6px",
                            border: "2px solid #ddd",
                            fontSize: "14px",
                            boxSizing: "border-box"
                        }}
                    />
                </div>

                <div style={{ marginBottom: "20px" }}>
                    <label style={{ display: "block", marginBottom: "6px", fontWeight: "600", color: "#333", fontSize: "13px" }}>📅 Date of Birth</label>
                    <input
                        type="date"
                        value={form.dob}
                        onChange={e => setForm({ ...form, dob: e.target.value })}
                        style={{
                            width: "100%",
                            padding: "10px",
                            borderRadius: "6px",
                            border: "2px solid #ddd",
                            fontSize: "14px",
                            boxSizing: "border-box"
                        }}
                    />
                </div>

                <button
                    onClick={submit}
                    style={{
                        width: "100%",
                        padding: "12px",
                        backgroundColor: "#667eea",
                        color: "white",
                        border: "none",
                        borderRadius: "8px",
                        fontSize: "16px",
                        fontWeight: "600",
                        cursor: "pointer",
                        transition: "all 0.3s ease",
                        boxShadow: "0 4px 12px rgba(102, 126, 234, 0.3)",
                        marginBottom: "15px"
                    }}
                    onMouseEnter={(e) => {
                        e.target.style.transform = "translateY(-2px)";
                        e.target.style.boxShadow = "0 6px 16px rgba(102, 126, 234, 0.4)";
                    }}
                    onMouseLeave={(e) => {
                        e.target.style.transform = "translateY(0)";
                        e.target.style.boxShadow = "0 4px 12px rgba(102, 126, 234, 0.3)";
                    }}
                >
                    ✨ Create Account
                </button>

                <p style={{ textAlign: "center", fontSize: "14px", color: "#999", margin: "0" }}>
                    Already have an account? <a href="/login" style={{ color: "#667eea", textDecoration: "none", fontWeight: "600" }}>Sign in</a>
                </p>
            </div>
        </div>
    );
}

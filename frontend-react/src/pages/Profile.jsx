import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"
import { api } from "../services/api"

export default function Profile() {
    const navigate = useNavigate()
    const token = localStorage.getItem("token")

    const [user, setUser] = useState(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        async function loadProfile() {
            try {
                const res = await api.get(`/user/me?token=${token}`)
                setUser(res.data)
            } catch (err) {
                console.error("Profile error:", err)
            } finally {
                setLoading(false)
            }
        }
        loadProfile()
    }, [])

    if (loading) return <p style={{ padding: 20 }}>Loading profile...</p>
    if (!user) return <p style={{ padding: 20 }}>Failed to load profile</p>

    const rp = user.risk_profile || {}

    return (
        <div style={pageStyle}>
            <div style={cardStyle}>
                <h2 style={title}>👤 My Profile</h2>

                <p><b>Age:</b> {rp.age}</p>
                <p><b>Income:</b> ₹{rp.income}</p>
                <p><b>Marital Status:</b> {rp.marital_status}</p>
                <p><b>Has Kids:</b> {rp.has_kids ? "Yes" : "No"}</p>

                <p><b>Height:</b> {rp.height} cm</p>
                <p><b>Weight:</b> {rp.weight} kg</p>
                <p><b>BMI:</b> {rp.bmi}</p>

                <p><b>Diseases:</b> {rp.diseases?.join(", ") || "None"}</p>
                <p><b>Risk Level:</b> {rp.risk_level}</p>

                <p>
                    <b>Preferred Policies:</b>{" "}
                    {rp.preferred_policy_types?.join(", ") || "Not set"}
                </p>

                <p><b>Max Premium:</b> ₹{rp.max_premium}</p>

                <button
                    style={button}
                    onClick={() => navigate("/recommendations")}
                >
                    ⭐ View Recommendations
                </button>

                <button
                    style={{ ...button, background: "#667eea", marginTop: "10px" }}
                    onClick={() => navigate("/preferences")}
                >
                    ✏️ Update Preferences
                </button>

                <button
                    style={{ ...button, background: "#764ba2", marginTop: "10px" }}
                    onClick={() => navigate("/claims")}
                >
                    📋 Insurance Claims
                </button>
            </div>
        </div>
    )
}

/* styles */
const pageStyle = {
    minHeight: "100vh",
    background: "#F4F6F8",
    display: "flex",
    justifyContent: "center",
    alignItems: "center"
}

const cardStyle = {
    width: "520px",
    background: "#fff",
    padding: "30px",
    borderRadius: "14px",
    boxShadow: "0 8px 20px rgba(0,0,0,0.15)",
    color: "#333"
}

const title = {
    color: "#1976D2",
    marginBottom: "15px"
}

const button = {
    marginTop: "20px",
    width: "100%",
    padding: "12px",
    background: "#1976D2",
    color: "#fff",
    border: "none",
    borderRadius: "8px",
    fontSize: "16px",
    cursor: "pointer"
}

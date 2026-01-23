import { useEffect, useState } from "react"
import { api } from "../services/api"

export default function Profile() {
    const token = localStorage.getItem("token")
    const [user, setUser] = useState(null)
    const [error, setError] = useState("")

    useEffect(() => {
        if (!token) return

        api.get(`/user/me?token=${token}`)
            .then(res => {
                setUser(res.data)
            })
            .catch(err => {
                console.error("Profile error:", err)
                setError("Failed to load profile")
            })
    }, [token])

    if (error) return <p style={{ color: "red" }}>{error}</p>
    if (!user) return <p>Loading...</p>

    const riskProfile = user.risk_profile || {}
    const riskLevel = riskProfile.risk_level || "unknown"

    return (
        <div style={{
            minHeight: "100vh",
            background: "#f4f6f8",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            padding: "20px"
        }}>
            <div style={{
                width: "520px",
                background: "#ffffff",
                padding: "30px",
                borderRadius: "14px",
                boxShadow: "0 10px 25px rgba(0,0,0,0.15)",
                color: "#222",
                fontFamily: "Segoe UI, sans-serif"
            }}>
                <h2 style={{ color: "#1976D2", marginBottom: "15px" }}>
                    👤 User Profile
                </h2>

                <p><b>Name:</b> {user.name}</p>
                <p><b>Email:</b> {user.email}</p>
                <p><b>DOB:</b> {user.dob}</p>

                <hr style={{ margin: "20px 0" }} />

                <h3 style={{ color: "#1976D2" }}>🩺 Health & Risk Profile</h3>

                {user.risk_profile ? (
                    <>
                        <p><b>Age:</b> {riskProfile.age ?? "—"}</p>
                        <p><b>Annual Income:</b> ₹{riskProfile.income ?? "—"}</p>
                        <p><b>BMI:</b> {riskProfile.bmi ?? "—"}</p>
                        <p>
                            <b>Diseases:</b>{" "}
                            {riskProfile.diseases?.length
                                ? riskProfile.diseases.join(", ")
                                : "None"}
                        </p>

                        <p style={{
                            fontWeight: "bold",
                            marginTop: "10px",
                            color:
                                riskLevel === "high" ? "red" :
                                    riskLevel === "medium" ? "orange" :
                                        riskLevel === "low" ? "green" :
                                            "#555"
                        }}>
                            Risk Level: {riskLevel.toUpperCase()}
                        </p>
                    </>
                ) : (
                    <p>No preferences saved yet</p>
                )}
            </div>
        </div>
    )
}

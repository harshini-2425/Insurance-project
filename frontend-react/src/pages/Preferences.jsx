import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { api } from "../services/api"

export default function Preferences() {
    const navigate = useNavigate()

    const [form, setForm] = useState({
        age: "",
        marital_status: "",
        has_kids: "no",
        income: "",
        diseases: [],
        bmi: ""
    })

    // 🔢 RISK LEVEL CALCULATION
    const calculateRiskLevel = () => {
        let score = 0

        if (form.diseases.length >= 5) score += 3
        else if (form.diseases.length >= 2) score += 2
        else score += 1

        const bmi = parseFloat(form.bmi)
        if (bmi >= 30) score += 2
        else if (bmi >= 25) score += 1

        if (score >= 5) return "High"
        if (score >= 3) return "Medium"
        return "Low"
    }
    const [preferredTypes, setPreferredTypes] = useState([])
    const [maxPremium, setMaxPremium] = useState("")


    const handleSave = async () => {
        const userId = localStorage.getItem("user_id")
        const token = localStorage.getItem("token")

        const payload = {
            ...form,
            risk_level: calculateRiskLevel()
        }

        try {
            await api.post(
                `/user/preferences?token=${token}`,
                {
                    age,
                    income,
                    marital_status,
                    has_kids,
                    bmi: Number(bmi),
                    diseases,
                    preferred_policy_types: preferredTypes,
                    max_premium: Number(maxPremium)
                }
            )

            navigate("/recommendations")
        } catch (err) {
            console.error("Save preferences failed", err)
            alert("Failed to save preferences")
        }
    }

    return (
        <div style={{
            minHeight: "100vh",
            background: "#f4f6f8",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            fontFamily: "Segoe UI, sans-serif"
        }}>
            <div style={{
                width: "420px",
                background: "#fff",
                padding: "30px",
                borderRadius: "12px",
                boxShadow: "0 8px 20px rgba(0,0,0,0.15)"
            }}>
                <h2 style={{ color: "#1976D2", marginBottom: "20px" }}>
                    User Preferences
                </h2>

                {/* BASIC DETAILS */}
                <input
                    placeholder="Age"
                    type="number"
                    value={form.age}
                    onChange={e => setForm({ ...form, age: e.target.value })}
                    style={inputStyle}
                />

                <select
                    value={form.marital_status}
                    onChange={e => setForm({ ...form, marital_status: e.target.value })}
                    style={inputStyle}
                >
                    <option value="">Marital Status</option>
                    <option value="single">Single</option>
                    <option value="married">Married</option>
                </select>

                <select
                    value={form.has_kids}
                    onChange={e => setForm({ ...form, has_kids: e.target.value })}
                    style={inputStyle}
                >
                    <option value="no">No Kids</option>
                    <option value="yes">Has Kids</option>
                </select>

                <input
                    placeholder="Annual Income"
                    type="number"
                    value={form.income}
                    onChange={e => setForm({ ...form, income: e.target.value })}
                    style={inputStyle}
                />

                {/* HEALTH DETAILS */}
                <h3 style={{ marginTop: "20px", color: "#333" }}>
                    Health Details
                </h3>

                {["Diabetes", "BP", "Asthma", "Heart", "Thyroid"].map(d => (
                    <label key={d} style={checkboxStyle}>
                        <input
                            type="checkbox"
                            checked={form.diseases.includes(d)}
                            onChange={(e) => {
                                setForm({
                                    ...form,
                                    diseases: e.target.checked
                                        ? [...form.diseases, d]
                                        : form.diseases.filter(x => x !== d)
                                })
                            }}
                        />
                        <span>{d}</span>
                    </label>
                ))}

                <input
                    placeholder="BMI (e.g. 23.5)"
                    type="number"
                    value={form.bmi}
                    onChange={e => setForm({ ...form, bmi: e.target.value })}
                    style={{ ...inputStyle, marginTop: "10px" }}
                />

                {/* RISK LEVEL DISPLAY */}
                <p style={{
                    marginTop: "15px",
                    fontWeight: "600",
                    color: "#1976D2"
                }}>
                    Risk Level: {calculateRiskLevel()}
                </p>
                <h3>Policy Preferences</h3>

                <label>Preferred Insurance Types</label>
                <div>
                    {["health", "life", "auto", "home", "travel"].map(type => (
                        <label key={type} style={{ marginRight: "10px", color: "#000" }}>
                            <input
                                type="checkbox"
                                value={type}
                                onChange={(e) => {
                                    if (e.target.checked) {
                                        setPreferredTypes([...preferredTypes, type])
                                    } else {
                                        setPreferredTypes(preferredTypes.filter(t => t !== type))
                                    }
                                }}
                            /> {type.toUpperCase()}
                        </label>
                    ))}
                </div>

                <label>Max Premium (₹)</label>
                <input
                    type="number"
                    value={maxPremium}
                    onChange={e => setMaxPremium(e.target.value)}
                />

                <button
                    onClick={handleSave}
                    style={{
                        width: "100%",
                        marginTop: "20px",
                        padding: "12px",
                        background: "#1976D2",
                        color: "#fff",
                        border: "none",
                        borderRadius: "8px",
                        fontSize: "16px",
                        cursor: "pointer"
                    }}
                >
                    Save Preferences
                </button>
            </div>
        </div>
    )
}

const inputStyle = {
    width: "100%",
    padding: "10px",
    marginBottom: "10px",
    borderRadius: "6px",
    border: "1px solid #ccc",
    fontSize: "14px"
}

const checkboxStyle = {
    display: "flex",
    alignItems: "center",
    gap: "10px",
    marginBottom: "8px",
    color: "#333",
    fontSize: "14px"
}

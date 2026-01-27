import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"
import { api } from "../services/api"

export default function Preferences() {
    const navigate = useNavigate()

    const [form, setForm] = useState({
        age: "",
        marital_status: "",
        has_kids: "no",
        income: "",
        height: "",
        weight: "",
        diseases: []
    })
    useEffect(() => {
        async function loadExistingPreferences() {
            const token = localStorage.getItem("token")
            try {
                const res = await api.get(`/user/me?token=${token}`)
                const rp = res.data.risk_profile
                if (!rp) return

                setForm({
                    age: rp.age || "",
                    income: rp.income || "",
                    marital_status: rp.marital_status || "",
                    has_kids: rp.has_kids ? "yes" : "no",
                    height: rp.height || "",
                    weight: rp.weight || "",
                    diseases: rp.diseases || []
                })

                setPreferredTypes(rp.preferred_policy_types || [])
                setMaxPremium(rp.max_premium || "")
            } catch (err) {
                console.error("Failed to load preferences", err)
            }
        }

        loadExistingPreferences()
    }, [])


    // 🧮 BMI CALCULATION
    const calculateBMI = () => {
        if (!form.height || !form.weight) return null
        const h = Number(form.height) / 100
        const w = Number(form.weight)
        return (w / (h * h)).toFixed(1)
    }

    const bmi = calculateBMI()

    // 🔢 RISK LEVEL
    const calculateRiskLevel = () => {
        let score = 0

        if (form.diseases.length >= 4) score += 3
        else if (form.diseases.length >= 2) score += 2
        else score += 1

        if (bmi >= 30) score += 2
        else if (bmi >= 25) score += 1

        if (score >= 5) return "High"
        if (score >= 3) return "Medium"
        return "Low"
    }

    const [preferredTypes, setPreferredTypes] = useState([])
    const [maxPremium, setMaxPremium] = useState("")


    const handleSave = async () => {
        const token = localStorage.getItem("token")

        const payload = {
            age: Number(form.age),
            income: Number(form.income),
            marital_status: form.marital_status,
            has_kids: form.has_kids === "yes",
            height: Number(form.height),
            weight: Number(form.weight),
            bmi: Number(bmi),
            diseases: form.diseases,
            preferred_policy_types: preferredTypes,
            max_premium: Number(maxPremium),
            risk_level: calculateRiskLevel()
        }

        try {
            const res = await fetch(`http://localhost:8000/user/preferences?token=${token}`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(payload)
            })

            if (!res.ok) {
                const errText = await res.text()
                throw new Error(`HTTP ${res.status}: ${errText}`)
            }

            localStorage.setItem("hasPreferences", "true")
            alert("Preferences saved successfully ✅")

            // Small delay to ensure backend has processed
            setTimeout(() => {
                navigate(`/recommendations?token=${token}`)
            }, 500)

        } catch (err) {
            console.error("Save preferences failed", err)
            alert("Failed to save preferences ❌")
        }
    }


    return (
        <div style={pageStyle}>
            <div style={cardStyle}>
                <h2 style={titleStyle}>👤 User Preferences</h2>

                {/* BASIC DETAILS */}
                <section>
                    <h3 style={sectionTitle}>Basic Details</h3>

                    <input
                        type="number"
                        placeholder="Age"
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
                        type="number"
                        placeholder="Annual Income (₹)"
                        value={form.income}
                        onChange={e => setForm({ ...form, income: e.target.value })}
                        style={inputStyle}
                    />
                </section>

                {/* HEALTH DETAILS */}
                <section>
                    <h3 style={sectionTitle}>❤️ Health Details</h3>

                    <div style={{ display: "flex", gap: "10px" }}>
                        <input
                            type="number"
                            placeholder="Height (cm)"
                            value={form.height}
                            onChange={e => setForm({ ...form, height: e.target.value })}
                            style={inputStyle}
                        />
                        <input
                            type="number"
                            placeholder="Weight (kg)"
                            value={form.weight}
                            onChange={e => setForm({ ...form, weight: e.target.value })}
                            style={inputStyle}
                        />
                    </div>

                    {bmi && (
                        <p style={{ color: "#0D47A1", fontWeight: 600 }}>
                            BMI: {bmi}
                        </p>
                    )}

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
                            {d}
                        </label>
                    ))}

                    <p style={{ fontWeight: 600, color: "#1976D2" }}>
                        Risk Level: {calculateRiskLevel()}
                    </p>
                </section>

                {/* POLICY PREFERENCES */}
                <section>
                    <h3 style={sectionTitle}>🛡️ Policy Preferences</h3>

                    <div style={pillContainer}>
                        {["health", "life", "auto", "home", "travel"].map(type => (
                            <label key={type} style={pill}>
                                <input
                                    type="checkbox"
                                    checked={preferredTypes.includes(type)}
                                    onChange={(e) => {
                                        setPreferredTypes(
                                            e.target.checked
                                                ? [...preferredTypes, type]
                                                : preferredTypes.filter(t => t !== type)
                                        )
                                    }}
                                />
                                {type.toUpperCase()}
                            </label>
                        ))}
                    </div>

                    <label style={{ fontWeight: 600, color: "#333" }}>
                        💰 Maximum Premium (₹)
                    </label>

                    <input
                        type="number"
                        placeholder="e.g. 15000"
                        value={maxPremium}
                        onChange={e => setMaxPremium(e.target.value)}
                        style={{
                            ...inputStyle,
                            color: "#000",
                            background: "#FFFDE7",
                            border: "1px solid #FFD54F"
                        }}
                    />
                </section>

                <button onClick={handleSave} style={buttonStyle}>
                    Save Preferences
                </button>
            </div>
        </div>
    )
}

/* ---------------- STYLES ---------------- */

const pageStyle = {
    minHeight: "100vh",
    background: "linear-gradient(135deg, #E3F2FD, #BBDEFB)",
    display: "flex",
    justifyContent: "center",
    alignItems: "center"
}

const cardStyle = {
    width: "520px",
    background: "#fff",
    padding: "30px",
    borderRadius: "16px",
    boxShadow: "0 10px 25px rgba(0,0,0,0.2)"
}

const titleStyle = {
    textAlign: "center",
    color: "#0D47A1",
    marginBottom: "20px"
}

const sectionTitle = {
    color: "#1565C0",
    borderBottom: "2px solid #E3F2FD",
    paddingBottom: "5px",
    marginTop: "20px"
}

const inputStyle = {
    width: "100%",
    padding: "10px",
    marginBottom: "10px",
    borderRadius: "8px",
    border: "1px solid #ccc",
    fontSize: "14px",
    color: "#000",
    background: "#FAFAFA"
}

const checkboxStyle = {
    display: "flex",
    gap: "8px",
    alignItems: "center",
    marginBottom: "6px",
    color: "#333"
}

const pillContainer = {
    display: "flex",
    flexWrap: "wrap",
    gap: "10px",
    marginBottom: "15px"
}

const pill = {
    background: "#E3F2FD",
    padding: "8px 14px",
    borderRadius: "20px",
    fontSize: "13px",
    color: "#0D47A1",
    display: "flex",
    alignItems: "center",
    gap: "6px",
    cursor: "pointer"
}

const buttonStyle = {
    width: "100%",
    padding: "14px",
    marginTop: "20px",
    background: "#1976D2",
    color: "#fff",
    border: "none",
    borderRadius: "10px",
    fontSize: "16px",
    cursor: "pointer"
}

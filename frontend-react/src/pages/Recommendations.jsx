import { useEffect, useState } from "react"
import { api } from "../services/api"

export default function Recommendations() {
    const token = localStorage.getItem("token")
    const [data, setData] = useState([])

    useEffect(() => {
        async function load() {
            try {
                const res = await api.get(`/recommendations?token=${token}`)
                setData(res.data)
            } catch (err) {
                console.error(err)
            }
        }
        load()
    }, [])

    if (data.length === 0) {
        return <h3>No recommendations yet</h3>
    }

    return (
        <div style={{
            minHeight: "100vh",
            background: "#f4f6f8",
            padding: "30px",
            fontFamily: "Segoe UI, sans-serif"
        }}>
            <h2 style={{
                marginBottom: "20px",
                color: "#333",
                fontSize: "26px"
            }}>
                ⭐ Recommended Policies for You
            </h2>

            {data.map(p => (
                <div
                    key={p.policy_id}
                    style={{
                        background: "white",
                        color: "#333",
                        padding: "20px",
                        marginBottom: "15px",
                        borderRadius: "10px",
                        boxShadow: "0 4px 10px rgba(0,0,0,0.08)",
                        borderLeft: "6px solid #667eea"
                    }}
                >
                    <h3 style={{ margin: "0 0 10px", color: "#667eea" }}>
                        {p.title}
                    </h3>

                    <p><b>Policy Type:</b> {p.policy_type}</p>
                    <p><b>Premium:</b> ₹{p.premium}</p>

                    <p style={{
                        marginTop: "10px",
                        fontStyle: "italic",
                        color: "#555"
                    }}>
                        💡 {p.reason}
                    </p>
                </div>
            ))}
        </div>
    )

}

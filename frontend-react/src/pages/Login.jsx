import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

export default function Login() {
  const [data, setData] = useState({ email: '', password: '' })
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const handleLogin = async () => {
    try {
      const res = await fetch('http://localhost:8000/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      })
      const json = await res.json()

      if (json.access_token) {
        localStorage.setItem("token", json.access_token)
        localStorage.setItem("user_id", json.user_id)

        // 🚀 FIRST TIME FLOW
        navigate("/preferences")
      } else {
        setError('Login failed')
      }

    } catch (err) {
      setError('Error logging in')
    }
  }


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
          🔐 Welcome Back
        </h1>
        <p style={{
          textAlign: "center",
          fontSize: "14px",
          color: "#999",
          margin: "0 0 25px 0"
        }}>
          Sign in to your InsureCompare account
        </p>

        {error && (
          <div style={{
            color: '#d32f2f',
            marginBottom: '20px',
            padding: '12px',
            backgroundColor: '#ffebee',
            borderRadius: '8px',
            fontSize: '14px',
            border: '1px solid #d32f2f'
          }}>
            ⚠️ {error}
          </div>
        )}

        <div style={{ marginBottom: '15px' }}>
          <label style={{ display: 'block', marginBottom: '6px', fontWeight: '600', color: '#333', fontSize: '13px' }}>📧 Email</label>
          <input
            placeholder="you@example.com"
            type="email"
            value={data.email}
            onChange={(e) => setData({ ...data, email: e.target.value })}
            style={{
              width: '100%',
              padding: '10px',
              borderRadius: '6px',
              border: '2px solid #ddd',
              fontSize: '14px',
              boxSizing: 'border-box'
            }}
          />
        </div>

        <div style={{ marginBottom: '20px' }}>
          <label style={{ display: 'block', marginBottom: '6px', fontWeight: '600', color: '#333', fontSize: '13px' }}>🔐 Password</label>
          <input
            type="password"
            placeholder="••••••••"
            value={data.password}
            onChange={(e) => setData({ ...data, password: e.target.value })}
            style={{
              width: '100%',
              padding: '10px',
              borderRadius: '6px',
              border: '2px solid #ddd',
              fontSize: '14px',
              boxSizing: 'border-box'
            }}
          />
        </div>

        <button
          onClick={handleLogin}
          style={{
            width: '100%',
            padding: '12px',
            backgroundColor: '#667eea',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            fontSize: '16px',
            fontWeight: '600',
            cursor: 'pointer',
            transition: 'all 0.3s ease',
            boxShadow: '0 4px 12px rgba(102, 126, 234, 0.3)',
            marginBottom: '15px'
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
          ✨ Sign In
        </button>

        <p style={{ textAlign: 'center', fontSize: '14px', color: '#999', margin: '0' }}>
          Don't have an account? <a href="/register" style={{ color: '#667eea', textDecoration: 'none', fontWeight: '600' }}>Create one</a>
        </p>
      </div>
    </div>
  )
}

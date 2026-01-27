import { useNavigate } from "react-router-dom";
import { useState } from "react";

export default function Header() {
    const navigate = useNavigate();
    const token = localStorage.getItem("token");
    const [showMenu, setShowMenu] = useState(false);

    const handleLogout = () => {
        localStorage.removeItem("token");
        localStorage.removeItem("userId");
        navigate("/login");
    };

    if (!token) return null; // Don't show header on login/register pages

    return (
        <header style={{
            backgroundColor: "#1976D2",
            color: "white",
            padding: "15px 20px",
            boxShadow: "0 2px 4px rgba(0,0,0,0.1)"
        }}>
            <div style={{
                maxWidth: "1200px",
                margin: "0 auto",
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center"
            }}>
                <div onClick={() => navigate("/browse")} style={{ cursor: "pointer", fontSize: "20px", fontWeight: "bold" }}>
                    🛡️ InsureCompare
                </div>

                <nav style={{ display: "flex", gap: "20px", alignItems: "center" }}>
                    <a
                        onClick={() => navigate("/browse")}
                        style={{ color: "white", cursor: "pointer", textDecoration: "none", fontSize: "14px" }}
                    >
                        Browse Policies
                    </a>
                    <a
                        onClick={() => navigate("/profile")}
                        style={{ color: "white", cursor: "pointer", textDecoration: "none", fontSize: "14px" }}
                    >
                        My Profile
                    </a>

                    <div style={{ position: "relative" }}>
                        <button
                            onClick={() => setShowMenu(!showMenu)}
                            style={{
                                backgroundColor: "rgba(255,255,255,0.2)",
                                color: "white",
                                border: "none",
                                padding: "8px 15px",
                                borderRadius: "4px",
                                cursor: "pointer",
                                fontSize: "14px"
                            }}
                        >
                            Menu ▼
                        </button>

                        {showMenu && (
                            <div style={{
                                position: "absolute",
                                right: 0,
                                top: "100%",
                                backgroundColor: "white",
                                color: "black",
                                borderRadius: "4px",
                                boxShadow: "0 4px 8px rgba(0,0,0,0.2)",
                                zIndex: 1000,
                                minWidth: "200px"
                            }}>
                                <a
                                    onClick={() => {
                                        navigate("/browse");
                                        setShowMenu(false);
                                    }}
                                    style={{
                                        display: "block",
                                        padding: "12px 20px",
                                        cursor: "pointer",
                                        borderBottom: "1px solid #eee",
                                        textDecoration: "none",
                                        color: "black"
                                    }}
                                    onMouseEnter={e => e.target.style.backgroundColor = "#f5f5f5"}
                                    onMouseLeave={e => e.target.style.backgroundColor = "white"}
                                >
                                    📋 Browse Policies
                                </a>
                                <a
                                    onClick={() => {
                                        navigate("/profile");
                                        setShowMenu(false);
                                    }}
                                    style={{
                                        display: "block",
                                        padding: "12px 20px",
                                        cursor: "pointer",
                                        borderBottom: "1px solid #eee",
                                        textDecoration: "none",
                                        color: "black"
                                    }}
                                    onMouseEnter={e => e.target.style.backgroundColor = "#f5f5f5"}
                                    onMouseLeave={e => e.target.style.backgroundColor = "white"}
                                >
                                    👤 My Profile
                                </a>
                                <a
                                    onClick={() => {
                                        navigate("/claims");
                                        setShowMenu(false);
                                    }}
                                    style={{
                                        display: "block",
                                        padding: "12px 20px",
                                        cursor: "pointer",
                                        borderBottom: "1px solid #eee",
                                        textDecoration: "none",
                                        color: "black"
                                    }}
                                    onMouseEnter={e => e.target.style.backgroundColor = "#f5f5f5"}
                                    onMouseLeave={e => e.target.style.backgroundColor = "white"}
                                >
                                    📋 Insurance Claims
                                </a>
                                <a
                                    onClick={() => {
                                        handleLogout();
                                        setShowMenu(false);
                                    }}
                                    style={{
                                        display: "block",
                                        padding: "12px 20px",
                                        cursor: "pointer",
                                        color: "#d32f2f",
                                        textDecoration: "none",
                                        fontWeight: "bold"
                                    }}
                                    onMouseEnter={e => e.target.style.backgroundColor = "#ffebee"}
                                    onMouseLeave={e => e.target.style.backgroundColor = "white"}
                                >
                                    🚪 Logout
                                </a>
                            </div>
                        )}
                    </div>
                </nav>
            </div>
        </header>
    );
}

import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import Login from './pages/Login'
import Register from './pages/Register'
import Profile from './pages/Profile'
import BrowsePolicies from './pages/BrowsePolicies'
import ComparePolicies from './pages/ComparePolicies'
import Header from './components/Header'
import './App.css'
import Preferences from "./pages/Preferences";
import Recommendations from "./pages/Recommendations";

function App() {
  return (
    <Router>
      <Header />
      <Routes>
        <Route path="/" element={<Navigate to="/browse" />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/browse" element={<BrowsePolicies />} />
        <Route path="/compare" element={<ComparePolicies />} />
        <Route path="/preferences" element={<Preferences />} />
        <Route path="/recommendations" element={<Recommendations />} />

      </Routes>
    </Router>
  )
}

export default App

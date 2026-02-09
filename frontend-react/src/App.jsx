import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import Login from './pages/Login'
import Register from './pages/Register'
import Profile from './pages/Profile'
import BrowsePolicies from './pages/BrowsePolicies'
import ComparePolicies from './pages/ComparePolicies'
import PolicyDetails from './pages/PolicyDetails'
import ApplyInsurance from './pages/ApplyInsurance'
import ClaimsPage from './pages/Claims'
import FraudMonitoring from './pages/FraudMonitoring'
import Header from './components/Header'
import './App.css'
import Preferences from "./pages/Preferences";
import Recommendations from "./pages/Recommendations";
import ProtectedRecommendations from "./components/ProtectedRecommendations"

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
        <Route path="/policy/:policyId" element={<PolicyDetails />} />
        <Route path="/apply/:policyId" element={<ApplyInsurance />} />
        <Route path="/preferences" element={<Preferences />} />
        <Route path="/recommendations" element={<Recommendations />} />
        <Route
          path="/recommendations"
          element={
            <ProtectedRecommendations>
              <Recommendations />
            </ProtectedRecommendations>
          }
        />
        <Route path="/claims" element={<ClaimsPage />} />
        <Route path="/fraud" element={<FraudMonitoring />} />

      </Routes>
    </Router>
  )
}

export default App

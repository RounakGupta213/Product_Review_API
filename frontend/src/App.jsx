import React, { useState } from "react";
import { BrowserRouter as Router, Routes, Route, Navigate, Link, useNavigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext";
import { ProductList } from "./pages/ProductList";
import { ProductDetail } from "./pages/ProductDetail";
import { LoginPage } from "./pages/LoginPage";
import { RegisterPage } from "./pages/RegisterPage";
import { LogOut, User as UserIcon } from "lucide-react";
import "./App.css";

const AppContent = () => {
  const [selectedProductId, setSelectedProductId] = useState(null);

  const { logout, user, loading } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  if (loading) {
    return <div className="loading-screen">Loading...</div>;
  }

  return (
    <div className="App">
      <header className="app-header">
        <div className="header-container">
          <h1>Product Review System</h1>
          <div className="user-nav">
            {user ? (
              <div className="user-nav-simple">
                <span className="user-name">{user.full_name}</span>
                <button onClick={handleLogout} className="logout-link">Logout</button>
              </div>
            ) : (
              <div className="auth-links">
                <Link to="/login" className="nav-link">Login</Link>
                <div className="nav-divider"></div>
                <Link to="/register" className="nav-link highlight">Register</Link>
              </div>
            )}
          </div>
        </div>
      </header>

      <main>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/" element={
            selectedProductId ? (
              <ProductDetail
                productId={selectedProductId}
                onBack={() => setSelectedProductId(null)}
              />
            ) : (
              <ProductList onSelectProduct={setSelectedProductId} />
            )
          } />
        </Routes>
      </main>
    </div>
  );
};

function App() {
  return (
    <AuthProvider>
      <Router>
        <AppContent />
      </Router>
    </AuthProvider>
  );
}

export default App;
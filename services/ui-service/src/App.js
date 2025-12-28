import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import OverviewDashboard from './pages/OverviewDashboard';
import Devices from './pages/Devices';
import Gateways from './pages/Gateways';
import Alerts from './pages/Alerts';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<OverviewDashboard />} />
          <Route path="/devices" element={<Devices />} />
          <Route path="/gateways" element={<Gateways />} />
          <Route path="/alerts" element={<Alerts />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;

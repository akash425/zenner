import React, { useState, useEffect } from 'react';
import StatCard from '../components/StatCard';
import { getTopDevices, getWeakDevices, getGatewayStats, getHighTemperatureAlerts } from '../services/apiClient';

const OverviewDashboard = () => {
  const [stats, setStats] = useState({
    topDevices: 0,
    weakDevices: 0,
    gateways: 0,
    highTemperatureAlerts: 0,
  });
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setIsLoading(true);
      setError(null);

      const [topDevicesRes, weakDevicesRes, gatewayStatsRes, highTempRes] = await Promise.allSettled([
        getTopDevices(),
        getWeakDevices(),
        getGatewayStats(),
        getHighTemperatureAlerts(),
      ]);

      const topDevices = topDevicesRes.status === 'fulfilled' ? (topDevicesRes.value?.data || []) : [];
      const weakDevices = weakDevicesRes.status === 'fulfilled' ? (weakDevicesRes.value?.data || []) : [];
      const gateways = gatewayStatsRes.status === 'fulfilled' ? (gatewayStatsRes.value?.data || []) : [];
      // High temperature returns an object with result_count, not an array
      const highTempData = highTempRes.status === 'fulfilled' ? (highTempRes.value?.data || {}) : {};
      const highTemperatureCount = typeof highTempData === 'object' && highTempData.result_count !== undefined 
        ? highTempData.result_count 
        : (Array.isArray(highTempData) ? highTempData.length : 0);

      setStats({
        topDevices: topDevices.length,
        weakDevices: weakDevices.length,
        gateways: gateways.length,
        highTemperatureAlerts: highTemperatureCount,
      });
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      setError('Failed to load dashboard data. Please try again later.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Overview Dashboard</h1>

      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm text-red-800">{error}</p>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Top Devices"
          value={isLoading ? '...' : stats.topDevices}
          icon={
            <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          }
        />
        <StatCard
          title="Weak Devices"
          value={isLoading ? '...' : stats.weakDevices}
          icon={
            <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          }
        />
        <StatCard
          title="Gateways"
          value={isLoading ? '...' : stats.gateways}
          icon={
            <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.111 16.404a5.5 5.5 0 017.778 0M12 20h.01m-7.08-7.071c3.904-3.905 10.236-3.905 14.141 0M1.394 9.393c5.857-5.857 15.355-5.857 21.213 0" />
            </svg>
          }
        />
        <StatCard
          title="High Temperature Alerts"
          value={isLoading ? '...' : stats.highTemperatureAlerts}
          icon={
            <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          }
        />
      </div>
    </div>
  );
};

export default OverviewDashboard;

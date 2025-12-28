import React, { useState, useEffect } from 'react';
import DataTable from '../components/DataTable';
import HealthBadge from '../components/HealthBadge';
import { getHighTemperatureAlerts, getWeakDevices, getDuplicateDevices } from '../services/apiClient';

const Alerts = () => {
  const [highTemperatureAlerts, setHighTemperatureAlerts] = useState([]);
  const [weakDevices, setWeakDevices] = useState([]);
  const [duplicateDevices, setDuplicateDevices] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchAlerts();
  }, []);

  const fetchAlerts = async () => {
    try {
      setIsLoading(true);
      setError(null);

      const [highTempRes, weakDevicesRes, duplicateDevicesRes] = await Promise.allSettled([
        getHighTemperatureAlerts(),
        getWeakDevices(),
        getDuplicateDevices(),
      ]);

      // High temperature returns an object with metadata, not an array of records
      // For now, we'll show an empty array since the API doesn't return individual records
      const highTempData = highTempRes.status === 'fulfilled' ? (highTempRes.value?.data || {}) : {};
      setHighTemperatureAlerts(
        Array.isArray(highTempData) ? highTempData : []
      );
      setWeakDevices(
        weakDevicesRes.status === 'fulfilled' ? (weakDevicesRes.value?.data || []) : []
      );
      setDuplicateDevices(
        duplicateDevicesRes.status === 'fulfilled' ? (duplicateDevicesRes.value?.data || []) : []
      );
    } catch (error) {
      console.error('Error fetching alerts:', error);
      setError('Failed to load alert data. Please try again later.');
    } finally {
      setIsLoading(false);
    }
  };

  const highTemperatureColumns = [
    {
      header: 'Device ID',
      key: 'device_id',
      render: (row) => row.device_id || row.device || 'N/A',
    },
    {
      header: 'Temperature',
      key: 'temperature',
      render: (row) => {
        const temp = row.temperature || row.temp || 'N/A';
        return temp !== 'N/A' ? `${temp}°C` : temp;
      },
    },
    {
      header: 'Timestamp',
      key: 'timestamp',
      render: (row) => {
        if (row.timestamp) {
          return new Date(row.timestamp).toLocaleString();
        }
        if (row.last_seen) {
          return new Date(row.last_seen).toLocaleString();
        }
        return 'N/A';
      },
    },
    {
      header: 'Status',
      key: 'status',
      render: () => <HealthBadge status="critical" label="High Temperature" />,
    },
  ];

  const weakDevicesColumns = [
    {
      header: 'Device ID',
      key: 'device_id',
    },
    {
      header: 'RSSI',
      key: 'rssi',
    },
    {
      header: 'SNR',
      key: 'snr',
    },
    {
      header: 'Status',
      key: 'status',
      render: () => <HealthBadge status="warning" label="Weak Signal" />,
    },
  ];

  const duplicateDevicesColumns = [
    {
      header: 'Device ID',
      key: 'device_id',
      render: (row) => row.device_id || row.device || 'N/A',
    },
    {
      header: 'Count',
      key: 'count',
      render: (row) => row.count || row.duplicate_count || 'N/A',
    },
    {
      header: 'Status',
      key: 'status',
      render: () => <HealthBadge status="warning" label="Duplicate" />,
    },
  ];

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Alerts</h1>
        <button
          onClick={fetchAlerts}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition"
        >
          Refresh
        </button>
      </div>

      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm text-red-800">{error}</p>
        </div>
      )}

      <div className="space-y-8">
        <div>
          <h2 className="text-xl font-semibold text-gray-900 mb-4">High Temperature Alerts</h2>
          <DataTable
            columns={highTemperatureColumns}
            data={highTemperatureAlerts}
            isLoading={isLoading}
            emptyMessage="No high temperature alerts found"
          />
        </div>

        <div>
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Weak Signal Devices</h2>
          <DataTable
            columns={weakDevicesColumns}
            data={weakDevices}
            isLoading={isLoading}
            emptyMessage="No weak signal devices found"
          />
        </div>

        <div>
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Duplicate Devices</h2>
          <DataTable
            columns={duplicateDevicesColumns}
            data={duplicateDevices}
            isLoading={isLoading}
            emptyMessage="No duplicate devices found"
          />
        </div>
      </div>
    </div>
  );
};

export default Alerts;

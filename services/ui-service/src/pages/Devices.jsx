import React, { useState, useEffect } from 'react';
import DataTable from '../components/DataTable';
import HealthBadge from '../components/HealthBadge';
import { getTopDevices, getWeakDevices, getDuplicateDevices } from '../services/apiClient';

const Devices = () => {
  const [topDevices, setTopDevices] = useState([]);
  const [weakDevices, setWeakDevices] = useState([]);
  const [duplicateDevices, setDuplicateDevices] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchDevices();
  }, []);

  const fetchDevices = async () => {
    try {
      setIsLoading(true);
      setError(null);

      const [topDevicesRes, weakDevicesRes, duplicateDevicesRes] = await Promise.allSettled([
        getTopDevices(),
        getWeakDevices(),
        getDuplicateDevices(),
      ]);

      setTopDevices(
        topDevicesRes.status === 'fulfilled' ? (topDevicesRes.value?.data || []) : []
      );
      setWeakDevices(
        weakDevicesRes.status === 'fulfilled' ? (weakDevicesRes.value?.data || []) : []
      );
      setDuplicateDevices(
        duplicateDevicesRes.status === 'fulfilled' ? (duplicateDevicesRes.value?.data || []) : []
      );
    } catch (error) {
      console.error('Error fetching devices:', error);
      setError('Failed to load device data. Please try again later.');
    } finally {
      setIsLoading(false);
    }
  };

  const topDevicesColumns = [
    {
      header: 'Device ID',
      key: 'device_id',
    },
    {
      header: 'Total Uplinks',
      key: 'count',
      render: (row) => row.count || row.total_uplinks || 0,
    },
    {
      header: 'Last Seen',
      key: 'last_seen',
      render: (row) => {
        if (row.last_seen) {
          return new Date(row.last_seen).toLocaleString();
        }
        return 'N/A';
      },
    },
    {
      header: 'Status',
      key: 'status',
      render: (row) => {
        const uplinks = row.count || row.total_uplinks || 0;
        const status = uplinks > 0 ? 'healthy' : 'unknown';
        return <HealthBadge status={status} label={status === 'healthy' ? 'Active' : 'Unknown'} />;
      },
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
        <h1 className="text-2xl font-bold text-gray-900">Devices</h1>
        <button
          onClick={fetchDevices}
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
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Top Active Devices</h2>
          <DataTable
            columns={topDevicesColumns}
            data={topDevices}
            isLoading={isLoading}
            emptyMessage="No top active devices found"
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

export default Devices;

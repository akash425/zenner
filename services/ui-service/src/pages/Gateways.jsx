import React, { useState, useEffect } from 'react';
import DataTable from '../components/DataTable';
import { getGatewayStats } from '../services/apiClient';

const Gateways = () => {
  const [gateways, setGateways] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchGateways();
  }, []);

  const fetchGateways = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await getGatewayStats();
      setGateways(response?.data || []);
    } catch (error) {
      console.error('Error fetching gateways:', error);
      setError('Failed to load gateway data. Please try again later.');
      setGateways([]);
    } finally {
      setIsLoading(false);
    }
  };

  const columns = [
    {
      header: 'Gateway ID',
      key: 'gateway_id',
    },
    {
      header: 'Avg Temperature',
      key: 'avg_temperature',
      render: (row) => {
        const temp = row.avg_temperature || row.avg_temp || row.temperature;
        if (temp !== null && temp !== undefined) {
          return `${parseFloat(temp).toFixed(2)}°C`;
        }
        return 'N/A';
      },
    },
    {
      header: 'Avg Humidity',
      key: 'avg_humidity',
      render: (row) => {
        const humidity = row.avg_humidity || row.humidity;
        if (humidity !== null && humidity !== undefined) {
          return `${parseFloat(humidity).toFixed(2)}%`;
        }
        return 'N/A';
      },
    },
  ];

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Gateways</h1>
        <button
          onClick={fetchGateways}
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

      <DataTable
        columns={columns}
        data={gateways}
        isLoading={isLoading}
        emptyMessage="No gateways found"
      />
    </div>
  );
};

export default Gateways;

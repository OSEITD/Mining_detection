import axios from 'axios';

// Update this to your computer's IP address when running locally
// Find your IP with: ipconfig (Windows) or ifconfig (Mac/Linux)
const API_BASE_URL = 'http://192.168.1.172:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface MiningSite {
  id: string;
  name: string;
  latitude: number;
  longitude: number;
  status: string;
  area: number;
  detectionDate: string;
}

export interface MiningStats {
  totalSites: number;
  activeMines: number;
  abandoned: number;
  totalArea: number;
  alerts: number;
}

export interface FieldReport {
  location: string;
  coordinates: {
    latitude: number;
    longitude: number;
  };
  description: string;
  photo: string | null;
  timestamp: string;
}

export const getMiningSites = async (): Promise<MiningSite[]> => {
  try {
    const response = await api.get('/mining-sites');
    return response.data;
  } catch (error) {
    console.error('Error fetching mining sites:', error);
    // Return mock data for development
    return getMockMiningSites();
  }
};

export const getMiningStats = async (): Promise<MiningStats> => {
  try {
    const response = await api.get('/stats');
    return response.data;
  } catch (error) {
    console.error('Error fetching stats:', error);
    // Return mock data for development
    return {
      totalSites: 35,
      activeMines: 15,
      abandoned: 12,
      totalArea: 523.4,
      alerts: 3,
    };
  }
};

export const submitFieldReport = async (
  report: FieldReport,
): Promise<void> => {
  try {
    await api.post('/field-reports', report);
  } catch (error) {
    console.error('Error submitting field report:', error);
    throw error;
  }
};

// Mock data for development/testing
const getMockMiningSites = (): MiningSite[] => {
  return [
    {
      id: '1',
      name: 'Site A - Konkola Mine Area',
      latitude: -12.5328,
      longitude: 27.8639,
      status: 'Active',
      area: 45.2,
      detectionDate: '2025-10-15',
    },
    {
      id: '2',
      name: 'Site B - Nchanga Area',
      latitude: -12.5512,
      longitude: 27.8421,
      status: 'Monitoring',
      area: 23.8,
      detectionDate: '2025-09-22',
    },
    {
      id: '3',
      name: 'Site C - Chingola West',
      latitude: -12.5145,
      longitude: 27.8534,
      status: 'Abandoned',
      area: 18.5,
      detectionDate: '2025-08-10',
    },
    {
      id: '4',
      name: 'Site D - Kasompe Area',
      latitude: -12.5689,
      longitude: 27.8756,
      status: 'Active',
      area: 32.1,
      detectionDate: '2025-11-01',
    },
    {
      id: '5',
      name: 'Site E - Chiwempala',
      latitude: -12.5234,
      longitude: 27.8312,
      status: 'Active',
      area: 28.7,
      detectionDate: '2025-10-28',
    },
    {
      id: '6',
      name: 'Site F - Lulamba',
      latitude: -12.5478,
      longitude: 27.8890,
      status: 'Monitoring',
      area: 15.3,
      detectionDate: '2025-09-15',
    },
    {
      id: '7',
      name: 'Site G - Mutenda',
      latitude: -12.5601,
      longitude: 27.8223,
      status: 'Abandoned',
      area: 21.9,
      detectionDate: '2025-07-20',
    },
    {
      id: '8',
      name: 'Site H - Kapisha',
      latitude: -12.5087,
      longitude: 27.8667,
      status: 'Active',
      area: 41.5,
      detectionDate: '2025-10-30',
    },
  ];
};

export default api;

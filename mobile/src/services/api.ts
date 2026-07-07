import axios, { AxiosInstance } from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

const API_BASE_URL = 'http://localhost:8080';

class ApiService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add auth token interceptor
    this.client.interceptors.request.use(async (config) => {
      const token = await AsyncStorage.getItem('auth_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });
  }

  // Auth
  async login(username: string, password: string) {
    const response = await this.client.post('/api/auth/login', {
      username,
      password,
    });
    return response.data;
  }

  async register(username: string, email: string, password: string) {
    const response = await this.client.post('/api/auth/register', {
      username,
      email,
      password,
    });
    return response.data;
  }

  // Market Data
  async getQuote(symbol: string) {
    const response = await this.client.get(`/api/market/quote/${symbol}`);
    return response.data;
  }

  async getAllQuotes() {
    const response = await this.client.get('/api/market/quotes');
    return response.data;
  }

  async getOrderBook(symbol: string, depth: number = 5) {
    const response = await this.client.get(`/api/market/orderbook/${symbol}`, {
      params: { depth },
    });
    return response.data;
  }

  async getStocks() {
    const response = await this.client.get('/api/market/stocks');
    return response.data;
  }

  async getMarketStatus() {
    const response = await this.client.get('/api/market/market-status');
    return response.data;
  }

  // Trading
  async placeOrder(order: {
    symbol: string;
    side: string;
    quantity: number;
    order_type?: string;
    price?: number;
  }) {
    const response = await this.client.post('/api/trading/order', order);
    return response.data;
  }

  async cancelOrder(orderId: string) {
    const response = await this.client.delete(`/api/trading/order/${orderId}`);
    return response.data;
  }

  async getPortfolio() {
    const response = await this.client.get('/api/trading/portfolio');
    return response.data;
  }

  async getPositions() {
    const response = await this.client.get('/api/trading/positions');
    return response.data;
  }

  async getTrades(symbol?: string, limit: number = 50) {
    const response = await this.client.get('/api/trading/trades', {
      params: { symbol, limit },
    });
    return response.data;
  }

  async getOrders(status?: string, limit: number = 50) {
    const response = await this.client.get('/api/trading/orders', {
      params: { status, limit },
    });
    return response.data;
  }

  // News
  async getNews(limit: number = 20) {
    // Mock for now
    return [
      {
        id: '1',
        title: 'IHSG Melemah Tipis di Tengah Sentimen Global',
        source: 'CNBC Indonesia',
        sentiment: -0.2,
        timestamp: new Date().toISOString(),
      },
    ];
  }

  // Fear & Greed
  async getFearGreed() {
    // Mock for now
    return {
      indonesia: { score: 45, status: 'Neutral' },
      asia: { score: 52, status: 'Neutral' },
      global: { score: 58, status: 'Neutral' },
      overall: { score: 50, status: 'Neutral' },
    };
  }
}

export const apiService = new ApiService();

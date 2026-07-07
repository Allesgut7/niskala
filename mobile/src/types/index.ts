// Niskala Mobile App Types

export interface Stock {
  symbol: string;
  name: string;
  price: number;
  change: number;
  changePct: number;
  volume: number;
}

export interface Quote {
  symbol: string;
  bid: number;
  ask: number;
  last: number;
  volume: number;
  change: number;
  changePct: number;
  timestamp: string;
}

export interface OrderBook {
  symbol: string;
  bids: [number, number][];
  asks: [number, number][];
  timestamp: string;
}

export interface Order {
  id: string;
  symbol: string;
  side: 'buy' | 'sell';
  quantity: number;
  order_type: 'market' | 'limit';
  price?: number;
  status: 'pending' | 'filled' | 'cancelled' | 'rejected';
  filled_quantity: number;
  fill_price: number;
  commission: number;
  created_at: string;
}

export interface Position {
  symbol: string;
  quantity: number;
  avg_price: number;
  current_price: number;
  market_value: number;
  unrealized_pnl: number;
  unrealized_pnl_pct: number;
}

export interface Portfolio {
  cash: number;
  equity: number;
  positions_value: number;
  total_realized_pnl: number;
  total_unrealized_pnl: number;
  total_pnl: number;
  return_pct: number;
  positions: Position[];
}

export interface NewsItem {
  id: string;
  title: string;
  source: string;
  sentiment: number;
  timestamp: string;
  url?: string;
}

export interface FearGreedData {
  indonesia: { score: number; status: string };
  asia: { score: number; status: string };
  global: { score: number; status: string };
  overall: { score: number; status: string };
}

export interface Alert {
  id: string;
  symbol: string;
  targetPrice: number;
  condition: 'above' | 'below';
  isActive: boolean;
}

export interface User {
  user_id: string;
  username: string;
  email: string;
}

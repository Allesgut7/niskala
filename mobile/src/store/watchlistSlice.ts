import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { apiService } from '../services/api';

interface WatchlistItem {
  symbol: string;
  name: string;
  price: number;
  change: number;
  changePct: number;
}

interface WatchlistState {
  items: WatchlistItem[];
  loading: boolean;
  error: string | null;
}

const initialState: WatchlistState = {
  items: [
    { symbol: 'BBCA', name: 'Bank Central Asia', price: 9500, change: 150, changePct: 1.6 },
    { symbol: 'BBRI', name: 'Bank Rakyat Indonesia', price: 4800, change: -50, changePct: -1.03 },
    { symbol: 'BMRI', name: 'Bank Mandiri', price: 6200, change: 100, changePct: 1.64 },
    { symbol: 'TLKM', name: 'Telkom Indonesia', price: 3800, change: 25, changePct: 0.66 },
    { symbol: 'GOTO', name: 'Gojek Tokopedia', price: 75, change: -2, changePct: -2.6 },
  ],
  loading: false,
  error: null,
};

export const fetchWatchlist = createAsyncThunk(
  'watchlist/fetchWatchlist',
  async () => {
    // Mock API call
    return initialState.items;
  }
);

const watchlistSlice = createSlice({
  name: 'watchlist',
  initialState,
  reducers: {
    addToWatchlist: (state, action) => {
      const exists = state.items.find(item => item.symbol === action.payload.symbol);
      if (!exists) {
        state.items.push(action.payload);
      }
    },
    removeFromWatchlist: (state, action) => {
      state.items = state.items.filter(item => item.symbol !== action.payload);
    },
    updatePrice: (state, action) => {
      const item = state.items.find(i => i.symbol === action.payload.symbol);
      if (item) {
        item.price = action.payload.price;
        item.change = action.payload.change;
        item.changePct = action.payload.changePct;
      }
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchWatchlist.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchWatchlist.fulfilled, (state, action) => {
        state.loading = false;
        state.items = action.payload;
      })
      .addCase(fetchWatchlist.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch watchlist';
      });
  },
});

export const { addToWatchlist, removeFromWatchlist, updatePrice } = watchlistSlice.actions;
export default watchlistSlice.reducer;

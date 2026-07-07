import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  FlatList,
  TouchableOpacity,
  StyleSheet,
  RefreshControl,
} from 'react-native';
import { useSelector, useDispatch } from 'react-redux';
import { Ionicons } from '@expo/vector-icons';

import { RootState } from '../store';
import { fetchWatchlist, removeFromWatchlist } from '../store/watchlistSlice';
import { StockCard } from '../components/StockCard';

export default function WatchlistScreen() {
  const dispatch = useDispatch();
  const { items, loading } = useSelector((state: RootState) => state.watchlist);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    dispatch(fetchWatchlist());
  }, [dispatch]);

  const onRefresh = async () => {
    setRefreshing(true);
    await dispatch(fetchWatchlist());
    setRefreshing(false);
  };

  const handleRemove = (symbol: string) => {
    dispatch(removeFromWatchlist(symbol));
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>My Watchlist</Text>
        <Text style={styles.headerSubtitle}>{items.length} stocks</Text>
      </View>

      <FlatList
        data={items}
        keyExtractor={(item) => item.symbol}
        renderItem={({ item }) => (
          <StockCard
            symbol={item.symbol}
            name={item.name}
            price={item.price}
            change={item.change}
            changePct={item.changePct}
            onRemove={() => handleRemove(item.symbol)}
          />
        )}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Ionicons name="star-outline" size={64} color="#6b7280" />
            <Text style={styles.emptyText}>No stocks in watchlist</Text>
            <Text style={styles.emptySubtext}>Add stocks to track them here</Text>
          </View>
        }
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#111827',
  },
  header: {
    padding: 16,
    backgroundColor: '#1f2937',
    borderBottomWidth: 1,
    borderBottomColor: '#374151',
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
  },
  headerSubtitle: {
    fontSize: 14,
    color: '#9ca3af',
    marginTop: 4,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 60,
  },
  emptyText: {
    fontSize: 18,
    color: '#9ca3af',
    marginTop: 16,
  },
  emptySubtext: {
    fontSize: 14,
    color: '#6b7280',
    marginTop: 8,
  },
});

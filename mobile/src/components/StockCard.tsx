import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

interface StockCardProps {
  symbol: string;
  name: string;
  price: number;
  change: number;
  changePct: number;
  onRemove?: () => void;
}

export const StockCard: React.FC<StockCardProps> = ({
  symbol,
  name,
  price,
  change,
  changePct,
  onRemove,
}) => {
  const isPositive = change >= 0;

  return (
    <View style={styles.card}>
      <View style={styles.info}>
        <Text style={styles.symbol}>{symbol}</Text>
        <Text style={styles.name}>{name}</Text>
      </View>
      
      <View style={styles.priceContainer}>
        <Text style={styles.price}>Rp {price.toLocaleString()}</Text>
        <View style={[styles.changeBadge, { backgroundColor: isPositive ? '#22c55e20' : '#ef444420' }]}>
          <Ionicons 
            name={isPositive ? 'trending-up' : 'trending-down'} 
            size={14} 
            color={isPositive ? '#22c55e' : '#ef4444'} 
          />
          <Text style={[styles.change, { color: isPositive ? '#22c55e' : '#ef4444' }]}>
            {isPositive ? '+' : ''}{changePct.toFixed(2)}%
          </Text>
        </View>
      </View>

      {onRemove && (
        <TouchableOpacity onPress={onRemove} style={styles.removeButton}>
          <Ionicons name="close-circle" size={24} color="#6b7280" />
        </TouchableOpacity>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  card: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    backgroundColor: '#1f2937',
    marginHorizontal: 16,
    marginBottom: 8,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#374151',
  },
  info: {
    flex: 1,
  },
  symbol: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#fff',
  },
  name: {
    fontSize: 12,
    color: '#9ca3af',
    marginTop: 2,
  },
  priceContainer: {
    alignItems: 'flex-end',
  },
  price: {
    fontSize: 16,
    fontWeight: '600',
    color: '#fff',
  },
  changeBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
    marginTop: 4,
  },
  change: {
    fontSize: 12,
    fontWeight: '600',
  },
  removeButton: {
    marginLeft: 12,
  },
});

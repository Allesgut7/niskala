import React, { useState } from 'react';
import {
  View,
  Text,
  FlatList,
  TouchableOpacity,
  StyleSheet,
  TextInput,
  Alert,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';

interface Alert {
  id: string;
  symbol: string;
  targetPrice: number;
  condition: 'above' | 'below';
  isActive: boolean;
}

export default function PriceAlertsScreen() {
  const [alerts, setAlerts] = useState<Alert[]>([
    { id: '1', symbol: 'BBCA', targetPrice: 10000, condition: 'above', isActive: true },
    { id: '2', symbol: 'BBRI', targetPrice: 4500, condition: 'below', isActive: true },
  ]);
  const [symbol, setSymbol] = useState('');
  const [price, setPrice] = useState('');

  const addAlert = () => {
    if (!symbol || !price) {
      Alert.alert('Error', 'Please enter symbol and price');
      return;
    }

    const newAlert: Alert = {
      id: Date.now().toString(),
      symbol: symbol.toUpperCase(),
      targetPrice: parseFloat(price),
      condition: 'above',
      isActive: true,
    };

    setAlerts([...alerts, newAlert]);
    setSymbol('');
    setPrice('');
  };

  const toggleAlert = (id: string) => {
    setAlerts(alerts.map(a => 
      a.id === id ? { ...a, isActive: !a.isActive } : a
    ));
  };

  const deleteAlert = (id: string) => {
    setAlerts(alerts.filter(a => a.id !== id));
  };

  return (
    <View style={styles.container}>
      <View style={styles.inputContainer}>
        <TextInput
          style={styles.input}
          placeholder="Symbol (e.g., BBCA)"
          placeholderTextColor="#6b7280"
          value={symbol}
          onChangeText={setSymbol}
          autoCapitalize="characters"
        />
        <TextInput
          style={styles.input}
          placeholder="Target Price"
          placeholderTextColor="#6b7280"
          value={price}
          onChangeText={setPrice}
          keyboardType="numeric"
        />
        <TouchableOpacity style={styles.addButton} onPress={addAlert}>
          <Ionicons name="add" size={24} color="#fff" />
        </TouchableOpacity>
      </View>

      <FlatList
        data={alerts}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => (
          <View style={styles.alertItem}>
            <View style={styles.alertInfo}>
              <Text style={styles.alertSymbol}>{item.symbol}</Text>
              <Text style={styles.alertPrice}>
                {item.condition === 'above' ? '↗' : '↙'} Rp {item.targetPrice.toLocaleString()}
              </Text>
            </View>
            <View style={styles.alertActions}>
              <TouchableOpacity onPress={() => toggleAlert(item.id)}>
                <Ionicons 
                  name={item.eye === true ? 'notifications' : 'notifications-off'} 
                  size={24} 
                  color={item.isActive ? '#2563eb' : '#6b7280'} 
                />
              </TouchableOpacity>
              <TouchableOpacity onPress={() => deleteAlert(item.id)}>
                <Ionicons name="trash" size={24} color="#ef4444" />
              </TouchableOpacity>
            </View>
          </View>
        )}
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Ionicons name="notifications-off-outline" size={64} color="#6b7280" />
            <Text style={styles.emptyText}>No price alerts</Text>
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
  inputContainer: {
    flexDirection: 'row',
    padding: 16,
    gap: 8,
  },
  input: {
    flex: 1,
    backgroundColor: '#1f2937',
    borderRadius: 8,
    padding: 12,
    color: '#fff',
    borderWidth: 1,
    borderColor: '#374151',
  },
  addButton: {
    backgroundColor: '#2563eb',
    borderRadius: 8,
    padding: 12,
    justifyContent: 'center',
    alignItems: 'center',
  },
  alertItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    backgroundColor: '#1f2937',
    marginHorizontal: 16,
    marginBottom: 8,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#374151',
  },
  alertInfo: {
    flex: 1,
  },
  alertSymbol: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#fff',
  },
  alertPrice: {
    fontSize: 14,
    color: '#9ca3af',
    marginTop: 4,
  },
  alertActions: {
    flexDirection: 'row',
    gap: 16,
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
});

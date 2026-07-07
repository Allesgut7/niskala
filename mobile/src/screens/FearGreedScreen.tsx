import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  RefreshControl,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';

interface FearGreedData {
  indonesia: { score: number; status: string };
  asia: { score: number; status: string };
  global: { score: number; status: string };
  overall: { score: number; status: string };
}

export default function FearGreedScreen() {
  const [data, setData] = useState<FearGreedData>({
    indonesia: { score: 45, status: 'Neutral' },
    asia: { score: 52, status: 'Neutral' },
    global: { score: 58, status: 'Neutral' },
    overall: { score: 50, status: 'Neutral' },
  });
  const [refreshing, setRefreshing] = useState(false);

  const getScoreColor = (score: number) => {
    if (score >= 75) return '#22c55e';
    if (score >= 55) return '#84cc16';
    if (score >= 45) return '#eab308';
    if (score >= 25) return '#f97316';
    return '#ef4444';
  };

  const getStatusEmoji = (score: number) => {
    if (score >= 75) return '🤑';
    if (score >= 55) return '😊';
    if (score >= 45) return '😐';
    if (score >= 25) return '😨';
    return '😱';
  };

  const renderGauge = (label: string, score: number, status: string) => (
    <View style={styles.gaugeContainer}>
      <Text style={styles.gaugeLabel}>{label}</Text>
      <View style={styles.gauge}>
        <View style={[styles.gaugeBar, { width: `${score}%`, backgroundColor: getScoreColor(score) }]} />
      </View>
      <View style={styles.gaugeInfo}>
        <Text style={[styles.gaugeScore, { color: getScoreColor(score) }]}>{score}</Text>
        <Text style={styles.gaugeStatus}>{getStatusEmoji(score)} {status}</Text>
      </View>
    </View>
  );

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Ionicons name="trending-up" size={32} color="#2563eb" />
        <Text style={styles.headerTitle}>Fear & Greed Index</Text>
        <Text style={styles.headerSubtitle}>Market sentiment indicators</Text>
      </View>

      {renderGauge('🇮🇩 Indonesia', data.indonesia.score, data.indonesia.status)}
      {renderGauge('🌏 Asia', data.asia.score, data.asia.status)}
      {renderGauge('🌍 Global', data.global.score, data.global.status)}
      
      <View style={styles.overallContainer}>
        <Text style={styles.overallLabel}>Overall Market Sentiment</Text>
        <Text style={[styles.overallScore, { color: getScoreColor(data.overall.score) }]}>
          {data.overall.score}
        </Text>
        <Text style={styles.overallStatus}>
          {getStatusEmoji(data.overall.score)} {data.overall.status}
        </Text>
      </View>

      <View style={styles.legendContainer}>
        <Text style={styles.legendTitle}>Legend</Text>
        <View style={styles.legendItem}>
          <View style={[styles.legendDot, { backgroundColor: '#ef4444' }]} />
          <Text style={styles.legendText}>Extreme Fear (0-25)</Text>
        </View>
        <View style={styles.legendItem}>
          <View style={[styles.legendDot, { backgroundColor: '#f97316' }]} />
          <Text style={styles.legendText}>Fear (25-45)</Text>
        </View>
        <View style={styles.legendItem}>
          <View style={[styles.legendDot, { backgroundColor: '#eab308' }]} />
          <Text style={styles.legendText}>Neutral (45-55)</Text>
        </View>
        <View style={styles.legendItem}>
          <View style={[styles.legendDot, { backgroundColor: '#84cc16' }]} />
          <Text style={styles.legendText}>Greed (55-75)</Text>
        </View>
        <View style={styles.legendItem}>
          <View style={[styles.legendDot, { backgroundColor: '#22c55e' }]} />
          <Text style={styles.legendText}>Extreme Greed (75-100)</Text>
        </View>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#111827',
  },
  header: {
    alignItems: 'center',
    padding: 24,
    backgroundColor: '#1f2937',
    borderBottomWidth: 1,
    borderBottomColor: '#374151',
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
    marginTop: 8,
  },
  headerSubtitle: {
    fontSize: 14,
    color: '#9ca3af',
    marginTop: 4,
  },
  gaugeContainer: {
    padding: 16,
    marginHorizontal: 16,
    marginTop: 16,
    backgroundColor: '#1f2937',
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#374151',
  },
  gaugeLabel: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 8,
  },
  gauge: {
    height: 8,
    backgroundColor: '#374151',
    borderRadius: 4,
    overflow: 'hidden',
  },
  gaugeBar: {
    height: '100%',
    borderRadius: 4,
  },
  gaugeInfo: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: 8,
  },
  gaugeScore: {
    fontSize: 24,
    fontWeight: 'bold',
  },
  gaugeStatus: {
    fontSize: 14,
    color: '#9ca3af',
  },
  overallContainer: {
    alignItems: 'center',
    padding: 24,
    margin: 16,
    backgroundColor: '#1f2937',
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#374151',
  },
  overallLabel: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 16,
  },
  overallScore: {
    fontSize: 64,
    fontWeight: 'bold',
  },
  overallStatus: {
    fontSize: 18,
    color: '#9ca3af',
    marginTop: 8,
  },
  legendContainer: {
    padding: 16,
    margin: 16,
    backgroundColor: '#1f2937',
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#374151',
  },
  legendTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 12,
  },
  legendItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  legendDot: {
    width: 12,
    height: 12,
    borderRadius: 6,
    marginRight: 8,
  },
  legendText: {
    fontSize: 14,
    color: '#9ca3af',
  },
});

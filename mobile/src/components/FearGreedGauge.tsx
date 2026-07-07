import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

interface FearGreedGaugeProps {
  score: number;
  label: string;
}

export const FearGreedGauge: React.FC<FearGreedGaugeProps> = ({ score, label }) => {
  const getColor = (s: number) => {
    if (s >= 75) return '#22c55e';
    if (s >= 55) return '#84cc16';
    if (s >= 45) return '#eab308';
    if (s >= 25) return '#f97316';
    return '#ef4444';
  };

  const getStatus = (s: number) => {
    if (s >= 75) return 'Extreme Greed';
    if (s >= 55) return 'Greed';
    if (s >= 45) return 'Neutral';
    if (s >= 25) return 'Fear';
    return 'Extreme Fear';
  };

  return (
    <View style={styles.container}>
      <Text style={styles.label}>{label}</Text>
      <View style={styles.gaugeContainer}>
        <View style={styles.gauge}>
          <View 
            style={[
              styles.gaugeFill, 
              { width: `${score}%`, backgroundColor: getColor(score) }
            ]} 
          />
        </View>
      </View>
      <View style={styles.info}>
        <Text style={[styles.score, { color: getColor(score) }]}>{score}</Text>
        <Text style={styles.status}>{getStatus(score)}</Text>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    padding: 16,
  },
  label: {
    fontSize: 14,
    fontWeight: '600',
    color: '#fff',
    marginBottom: 8,
  },
  gaugeContainer: {
    marginBottom: 8,
  },
  gauge: {
    height: 8,
    backgroundColor: '#374151',
    borderRadius: 4,
    overflow: 'hidden',
  },
  gaugeFill: {
    height: '100%',
    borderRadius: 4,
  },
  info: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  score: {
    fontSize: 20,
    fontWeight: 'bold',
  },
  status: {
    fontSize: 12,
    color: '#9ca3af',
  },
});

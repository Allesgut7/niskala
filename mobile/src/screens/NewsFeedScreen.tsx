import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  FlatList,
  StyleSheet,
  TouchableOpacity,
  Linking,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';

interface NewsItem {
  id: string;
  title: string;
  source: string;
  sentiment: number;
  timestamp: string;
  url: string;
}

export default function NewsFeedScreen() {
  const [news, setNews] = useState<NewsItem[]>([
    {
      id: '1',
      title: 'IHSG Melemah Tipis di Tengah Sentimen Global',
      source: 'CNBC Indonesia',
      sentiment: -0.2,
      timestamp: '2 jam lalu',
      url: 'https://cnbcindonesia.com',
    },
    {
      id: '2',
      title: 'Bank Indonesia Pertahankan Suku Bunga Acuan',
      source: 'Kontan',
      sentiment: 0.1,
      timestamp: '4 jam lalu',
      url: 'https://kontan.co.id',
    },
    {
      id: '3',
      title: 'Saham Teknologi Global Menguat',
      source: 'Reuters',
      sentiment: 0.5,
      timestamp: '6 jam lalu',
      url: 'https://reuters.com',
    },
  ]);

  const getSentimentColor = (sentiment: number) => {
    if (sentiment > 0.2) return '#22c55e';
    if (sentiment < -0.2) return '#ef4444';
    return '#eab308';
  };

  const getSentimentLabel = (sentiment: number) => {
    if (sentiment > 0.2) return 'Positive';
    if (sentiment < -0.2) return 'Negative';
    return 'Neutral';
  };

  return (
    <View style={styles.container}>
      <FlatList
        data={news}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => (
          <TouchableOpacity 
            style={styles.newsItem}
            onPress={() => Linking.openURL(item.url)}
          >
            <View style={styles.newsHeader}>
              <View style={[styles.sentimentBadge, { backgroundColor: getSentimentColor(item.sentiment) }]}>
                <Text style={styles.sentimentText}>{getSentimentLabel(item.sentiment)}</Text>
              </View>
              <Text style={styles.source}>{item.source}</Text>
            </View>
            <Text style={styles.title}>{item.title}</Text>
            <Text style={styles.timestamp}>{item.timestamp}</Text>
          </TouchableOpacity>
        )}
        ListHeaderComponent={
          <View style={styles.header}>
            <Ionicons name="newspaper" size={24} color="#2563eb" />
            <Text style={styles.headerTitle}>Latest News</Text>
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
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    gap: 8,
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#fff',
  },
  newsItem: {
    padding: 16,
    backgroundColor: '#1f2937',
    marginHorizontal: 16,
    marginBottom: 8,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#374151',
  },
  newsHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  sentimentBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
  },
  sentimentText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: 'bold',
  },
  source: {
    fontSize: 12,
    color: '#6b7280',
  },
  title: {
    fontSize: 16,
    color: '#fff',
    lineHeight: 24,
  },
  timestamp: {
    fontSize: 12,
    color: '#6b7280',
    marginTop: 8,
  },
});

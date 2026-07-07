import React from 'react';
import { StatusBar } from 'expo-status-bar';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Provider } from 'react-redux';
import { Ionicons } from '@expo/vector-icons';

import { store } from './src/store';
import WatchlistScreen from './src/screens/WatchlistScreen';
import PriceAlertsScreen from './src/screens/PriceAlertsScreen';
import NewsFeedScreen from './src/screens/NewsFeedScreen';
import FearGreedScreen from './src/screens/FearGreedScreen';
import SettingsScreen from './src/screens/SettingsScreen';

const Tab = createBottomTabNavigator();

export default function App() {
  return (
    <Provider store={store}>
      <NavigationContainer>
        <Tab.Navigator
          screenOptions={({ route }) => ({
            tabBarIcon: ({ focused, color, size }) => {
              let iconName: keyof typeof Ionicons.glyphMap;

              switch (route.name) {
                case 'Watchlist':
                  iconName = focused ? 'star' : 'star-outline';
                  break;
                case 'Alerts':
                  iconName = focused ? 'notifications' : 'notifications-outline';
                  break;
                case 'News':
                  iconName = focused ? 'newspaper' : 'newspaper-outline';
                  break;
                case 'Fear & Greed':
                  iconName = focused ? 'trending-up' : 'trending-up-outline';
                  break;
                case 'Settings':
                  iconName = focused ? 'settings' : 'settings-outline';
                  break;
                default:
                  iconName = 'ellipse';
              }

              return <Ionicons name={iconName} size={size} color={color} />;
            },
            tabBarActiveTintColor: '#2563eb',
            tabBarInactiveTintColor: '#6b7280',
            headerStyle: {
              backgroundColor: '#1f2937',
            },
            headerTintColor: '#fff',
            headerTitleStyle: {
              fontWeight: 'bold',
            },
          })}
        >
          <Tab.Screen 
            name="Watchlist" 
            component={WatchlistScreen}
            options={{ title: 'Watchlist' }}
          />
          <Tab.Screen 
            name="Alerts" 
            component={PriceAlertsScreen}
            options={{ title: 'Price Alerts' }}
          />
          <Tab.Screen 
            name="News" 
            component={NewsFeedScreen}
            options={{ title: 'News Feed' }}
          />
          <Tab.Screen 
            name="Fear & Greed" 
            component={FearGreedScreen}
            options={{ title: 'Fear & Greed' }}
          />
          <Tab.Screen 
            name="Settings" 
            component={SettingsScreen}
            options={{ title: 'Settings' }}
          />
        </Tab.Navigator>
        <StatusBar style="light" />
      </NavigationContainer>
    </Provider>
  );
}

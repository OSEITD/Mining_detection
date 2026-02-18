/**
 * Chingola Mining Monitor - React Native App
 * AI-Powered Illegal Mining Detection System
 * @author Owen Mupeta
 */

import React from 'react';
import {NavigationContainer} from '@react-navigation/native';
import {createBottomTabNavigator} from '@react-navigation/bottom-tabs';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import {StatusBar, StyleSheet} from 'react-native';

// Screens
import DashboardScreen from './src/screens/DashboardScreen';
import MapScreen from './src/screens/MapScreen';
import AIDetectionScreen from './src/screens/AIDetectionScreen';
import AnalyticsScreen from './src/screens/AnalyticsScreen';
import ReportScreen from './src/screens/ReportScreen';

const Tab = createBottomTabNavigator();

const App = () => {
  return (
    <>
      <StatusBar barStyle="light-content" backgroundColor="#667eea" />
      <NavigationContainer>
        <Tab.Navigator
          screenOptions={({route}) => ({
            tabBarIcon: ({focused, color, size}) => {
              let iconName: string;

              switch (route.name) {
                case 'Dashboard':
                  iconName = focused ? 'view-dashboard' : 'view-dashboard-outline';
                  break;
                case 'Map':
                  iconName = focused ? 'map' : 'map-outline';
                  break;
                case 'AI Detection':
                  iconName = focused ? 'brain' : 'brain';
                  break;
                case 'Analytics':
                  iconName = focused ? 'chart-line' : 'chart-line';
                  break;
                case 'Report':
                  iconName = focused ? 'alert-circle' : 'alert-circle-outline';
                  break;
                default:
                  iconName = 'help-circle';
              }

              return <Icon name={iconName} size={size} color={color} />;
            },
            tabBarActiveTintColor: '#667eea',
            tabBarInactiveTintColor: 'gray',
            tabBarStyle: styles.tabBar,
            headerStyle: {
              backgroundColor: '#667eea',
            },
            headerTintColor: '#fff',
            headerTitleStyle: {
              fontWeight: 'bold',
            },
          })}>
          <Tab.Screen 
            name="Dashboard" 
            component={DashboardScreen}
            options={{title: '⛏️ Mining Monitor'}}
          />
          <Tab.Screen 
            name="Map" 
            component={MapScreen}
            options={{title: 'Interactive Map'}}
          />                                     
          <Tab.Screen 
            name="AI Detection" 
            component={AIDetectionScreen}
            options={{title: 'AI Detection'}}     

          />
          <Tab.Screen 
            name="Analytics" 
            component={AnalyticsScreen}
            options={{title: 'Analytics'}}
          />
          <Tab.Screen 
            name="Report" 
            component={ReportScreen}
            options={{title: 'Field Report'}}
          />
        </Tab.Navigator>
      </NavigationContainer>
    </>
  );
};

const styles = StyleSheet.create({
  tabBar: {
    paddingBottom: 5,
    paddingTop: 5,
    height: 60,
  },
});

export default App;

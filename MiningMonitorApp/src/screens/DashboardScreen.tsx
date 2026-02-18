import React, {useEffect, useState} from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Dimensions,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import {getMiningStats} from '../services/api';

const {width} = Dimensions.get('window');

const DashboardScreen = () => {
  const [stats, setStats] = useState({
    totalSites: 0,
    activeMines: 0,
    abandoned: 0,
    totalArea: 0,
    alerts: 0,
  });

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const data = await getMiningStats();
      setStats(data);
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
  };

  const StatCard = ({
    icon,
    title,
    value,
    unit,
    color,
  }: {
    icon: string;
    title: string;
    value: number;
    unit?: string;
    color: string;
  }) => (
    <View style={[styles.statCard, {borderLeftColor: color}]}>
      <Icon name={icon} size={32} color={color} />
      <View style={styles.statContent}>
        <Text style={styles.statValue}>
          {value}
          {unit && <Text style={styles.statUnit}> {unit}</Text>}
        </Text>
        <Text style={styles.statTitle}>{title}</Text>
      </View>
    </View>
  );

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Chingola Mining Monitor</Text>
        <Text style={styles.subtitle}>
          AI-Powered Illegal Mining Detection System
        </Text>
        <Text style={styles.location}>📍 Chingola District, Zambia</Text>
      </View>

      <View style={styles.statsContainer}>
        <StatCard
          icon="map-marker-multiple"
          title="Total Mining Sites"
          value={stats.totalSites}
          color="#667eea"
        />
        <StatCard
          icon="alert-circle"
          title="Active Mines"
          value={stats.activeMines}
          color="#e74c3c"
        />
        <StatCard
          icon="close-circle"
          title="Abandoned Sites"
          value={stats.abandoned}
          color="#95a5a6"
        />
        <StatCard
          icon="chart-box"
          title="Total Area"
          value={stats.totalArea}
          unit="ha"
          color="#2ecc71"
        />
      </View>

      {stats.alerts > 0 && (
        <View style={styles.alertBox}>
          <Icon name="alert" size={24} color="#e74c3c" />
          <View style={styles.alertContent}>
            <Text style={styles.alertTitle}>
              {stats.alerts} New Activity Detected
            </Text>
            <Text style={styles.alertText}>
              Potential illegal mining detected. Review AI analysis for details.
            </Text>
          </View>
        </View>
      )}

      <View style={styles.quickActions}>
        <Text style={styles.sectionTitle}>Quick Actions</Text>
        <TouchableOpacity style={styles.actionButton}>
          <Icon name="map-search" size={24} color="#fff" />
          <Text style={styles.actionText}>View Map</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.actionButton}>
          <Icon name="file-chart" size={24} color="#fff" />
          <Text style={styles.actionText}>Generate Report</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.actionButton}>
          <Icon name="camera" size={24} color="#fff" />
          <Text style={styles.actionText}>Field Report</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f7fa',
  },
  header: {
    padding: 20,
    backgroundColor: '#fff',
    marginBottom: 15,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#2c3e50',
    marginBottom: 5,
  },
  subtitle: {
    fontSize: 14,
    color: '#7f8c8d',
    marginBottom: 8,
  },
  location: {
    fontSize: 14,
    color: '#667eea',
    fontWeight: '600',
  },
  statsContainer: {
    paddingHorizontal: 15,
  },
  statCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 20,
    marginBottom: 15,
    flexDirection: 'row',
    alignItems: 'center',
    borderLeftWidth: 4,
    shadowColor: '#000',
    shadowOffset: {width: 0, height: 2},
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  statContent: {
    marginLeft: 15,
    flex: 1,
  },
  statValue: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#2c3e50',
  },
  statUnit: {
    fontSize: 16,
    color: '#7f8c8d',
  },
  statTitle: {
    fontSize: 14,
    color: '#7f8c8d',
    marginTop: 4,
  },
  alertBox: {
    backgroundColor: '#fee',
    borderLeftWidth: 4,
    borderLeftColor: '#e74c3c',
    borderRadius: 8,
    padding: 15,
    marginHorizontal: 15,
    marginBottom: 20,
    flexDirection: 'row',
  },
  alertContent: {
    marginLeft: 12,
    flex: 1,
  },
  alertTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#c0392b',
    marginBottom: 4,
  },
  alertText: {
    fontSize: 14,
    color: '#7f8c8d',
  },
  quickActions: {
    paddingHorizontal: 15,
    paddingBottom: 20,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#2c3e50',
    marginBottom: 15,
  },
  actionButton: {
    backgroundColor: '#667eea',
    borderRadius: 12,
    padding: 16,
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: {width: 0, height: 2},
    shadowOpacity: 0.2,
    shadowRadius: 4,
    elevation: 3,
  },
  actionText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
    marginLeft: 12,
  },
});

export default DashboardScreen;

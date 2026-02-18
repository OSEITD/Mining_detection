import React from 'react';
import {View, Text, StyleSheet, ScrollView} from 'react-native';
import {BarChart, PieChart} from 'react-native-chart-kit';
import {Dimensions} from 'react-native';

const screenWidth = Dimensions.get('window').width;

const AnalyticsScreen = () => {
  const statusData = [
    {
      name: 'Active',
      count: 15,
      color: '#e74c3c',
      legendFontColor: '#7f8c8d',
      legendFontSize: 12,
    },
    {
      name: 'Monitoring',
      count: 8,
      color: '#f39c12',
      legendFontColor: '#7f8c8d',
      legendFontSize: 12,
    },
    {
      name: 'Abandoned',
      count: 12,
      color: '#95a5a6',
      legendFontColor: '#7f8c8d',
      legendFontSize: 12,
    },
  ];

  const monthlyDetections = {
    labels: ['Jul', 'Aug', 'Sep', 'Oct', 'Nov'],
    datasets: [
      {
        data: [3, 7, 5, 9, 11],
      },
    ],
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>📊 Mining Analytics</Text>
        <Text style={styles.subtitle}>Chingola District Overview</Text>
      </View>

      <View style={styles.chartContainer}>
        <Text style={styles.chartTitle}>Mining Site Status Distribution</Text>
        <PieChart
          data={statusData}
          width={screenWidth - 40}
          height={220}
          chartConfig={{
            color: (opacity = 1) => `rgba(102, 126, 234, ${opacity})`,
          }}
          accessor="count"
          backgroundColor="transparent"
          paddingLeft="15"
          absolute
        />
      </View>

      <View style={styles.chartContainer}>
        <Text style={styles.chartTitle}>Monthly Detections (2025)</Text>
        <BarChart
          data={monthlyDetections}
          width={screenWidth - 40}
          height={220}
          yAxisLabel=""
          yAxisSuffix=""
          chartConfig={{
            backgroundColor: '#fff',
            backgroundGradientFrom: '#fff',
            backgroundGradientTo: '#fff',
            decimalPlaces: 0,
            color: (opacity = 1) => `rgba(102, 126, 234, ${opacity})`,
            labelColor: (opacity = 1) => `rgba(0, 0, 0, ${opacity})`,
            style: {
              borderRadius: 16,
            },
            propsForBackgroundLines: {
              strokeDasharray: '',
            },
          }}
          style={styles.chart}
        />
      </View>

      <View style={styles.statsGrid}>
        <View style={styles.statBox}>
          <Text style={styles.statNumber}>35</Text>
          <Text style={styles.statLabel}>Total Sites</Text>
        </View>
        <View style={styles.statBox}>
          <Text style={styles.statNumber}>523 ha</Text>
          <Text style={styles.statLabel}>Total Area</Text>
        </View>
        <View style={styles.statBox}>
          <Text style={styles.statNumber}>43%</Text>
          <Text style={styles.statLabel}>Active Rate</Text>
        </View>
        <View style={styles.statBox}>
          <Text style={styles.statNumber}>35</Text>
          <Text style={styles.statLabel}>YTD Detections</Text>
        </View>
      </View>

      <View style={styles.insightsContainer}>
        <Text style={styles.sectionTitle}>Key Insights</Text>
        <View style={styles.insightBox}>
          <Text style={styles.insightIcon}>📈</Text>
          <Text style={styles.insightText}>
            Mining activity increased 22% in the last quarter
          </Text>
        </View>
        <View style={styles.insightBox}>
          <Text style={styles.insightIcon}>⚠️</Text>
          <Text style={styles.insightText}>
            15 sites classified as high-priority for monitoring
          </Text>
        </View>
        <View style={styles.insightBox}>
          <Text style={styles.insightIcon}>🌍</Text>
          <Text style={styles.insightText}>
            Average site size: 14.9 hectares
          </Text>
        </View>
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
    fontSize: 22,
    fontWeight: 'bold',
    color: '#2c3e50',
    marginBottom: 5,
  },
  subtitle: {
    fontSize: 14,
    color: '#7f8c8d',
  },
  chartContainer: {
    backgroundColor: '#fff',
    marginHorizontal: 15,
    marginBottom: 15,
    borderRadius: 12,
    padding: 15,
    shadowColor: '#000',
    shadowOffset: {width: 0, height: 2},
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  chartTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#2c3e50',
    marginBottom: 15,
  },
  chart: {
    marginVertical: 8,
    borderRadius: 16,
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    paddingHorizontal: 10,
    marginBottom: 15,
  },
  statBox: {
    width: '47%',
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 20,
    margin: '1.5%',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: {width: 0, height: 2},
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  statNumber: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#667eea',
    marginBottom: 5,
  },
  statLabel: {
    fontSize: 12,
    color: '#7f8c8d',
    textAlign: 'center',
  },
  insightsContainer: {
    backgroundColor: '#fff',
    marginHorizontal: 15,
    marginBottom: 20,
    borderRadius: 12,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: {width: 0, height: 2},
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#2c3e50',
    marginBottom: 15,
  },
  insightBox: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#ecf0f1',
  },
  insightIcon: {
    fontSize: 24,
    marginRight: 12,
  },
  insightText: {
    flex: 1,
    fontSize: 14,
    color: '#2c3e50',
  },
});

export default AnalyticsScreen;

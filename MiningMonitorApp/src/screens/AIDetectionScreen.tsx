import React from 'react';
import {View, Text, StyleSheet, ScrollView, Image} from 'react-native';
import {LineChart} from 'react-native-chart-kit';
import {Dimensions} from 'react-native';

const screenWidth = Dimensions.get('window').width;

const AIDetectionScreen = () => {
  const modelMetrics = {
    accuracy: 94.2,
    precision: 91.8,
    recall: 96.5,
    f1Score: 94.1,
  };

  const trainingData = {
    labels: ['Ep1', 'Ep5', 'Ep10', 'Ep15', 'Ep20', 'Ep25'],
    datasets: [
      {
        data: [0.65, 0.78, 0.85, 0.91, 0.94, 0.94],
        color: (opacity = 1) => `rgba(102, 126, 234, ${opacity})`,
        strokeWidth: 2,
      },
    ],
  };

  const MetricCard = ({
    title,
    value,
    icon,
  }: {
    title: string;
    value: number;
    icon: string;
  }) => (
    <View style={styles.metricCard}>
      <Text style={styles.metricIcon}>{icon}</Text>
      <Text style={styles.metricValue}>{value.toFixed(1)}%</Text>
      <Text style={styles.metricTitle}>{title}</Text>
    </View>
  );

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>🤖 U-Net Model Performance</Text>
        <Text style={styles.subtitle}>
          Deep Learning for Mining Detection
        </Text>
      </View>

      <View style={styles.metricsGrid}>
        <MetricCard
          title="Accuracy"
          value={modelMetrics.accuracy}
          icon="🎯"
        />
        <MetricCard
          title="Precision"
          value={modelMetrics.precision}
          icon="📊"
        />
        <MetricCard title="Recall" value={modelMetrics.recall} icon="🔍" />
        <MetricCard title="F1-Score" value={modelMetrics.f1Score} icon="⚡" />
      </View>

      <View style={styles.chartContainer}>
        <Text style={styles.chartTitle}>Training Progress</Text>
        <LineChart
          data={trainingData}
          width={screenWidth - 40}
          height={220}
          chartConfig={{
            backgroundColor: '#fff',
            backgroundGradientFrom: '#fff',
            backgroundGradientTo: '#fff',
            decimalPlaces: 2,
            color: (opacity = 1) => `rgba(102, 126, 234, ${opacity})`,
            labelColor: (opacity = 1) => `rgba(0, 0, 0, ${opacity})`,
            style: {
              borderRadius: 16,
            },
            propsForDots: {
              r: '6',
              strokeWidth: '2',
              stroke: '#667eea',
            },
          }}
          bezier
          style={styles.chart}
        />
      </View>

      <View style={styles.modelInfo}>
        <Text style={styles.sectionTitle}>Model Architecture</Text>
        <View style={styles.infoRow}>
          <Text style={styles.infoLabel}>Model Type:</Text>
          <Text style={styles.infoValue}>U-Net CNN</Text>
        </View>
        <View style={styles.infoRow}>
          <Text style={styles.infoLabel}>Parameters:</Text>
          <Text style={styles.infoValue}>13.4M</Text>
        </View>
        <View style={styles.infoRow}>
          <Text style={styles.infoLabel}>Input Size:</Text>
          <Text style={styles.infoValue}>256x256x3</Text>
        </View>
        <View style={styles.infoRow}>
          <Text style={styles.infoLabel}>Training Data:</Text>
          <Text style={styles.infoValue}>1,250 images</Text>
        </View>
        <View style={styles.infoRow}>
          <Text style={styles.infoLabel}>Last Updated:</Text>
          <Text style={styles.infoValue}>November 2025</Text>
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
  metricsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    paddingHorizontal: 10,
    marginBottom: 15,
  },
  metricCard: {
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
  metricIcon: {
    fontSize: 32,
    marginBottom: 8,
  },
  metricValue: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#667eea',
    marginBottom: 4,
  },
  metricTitle: {
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
  modelInfo: {
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
  infoRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#ecf0f1',
  },
  infoLabel: {
    fontSize: 14,
    color: '#7f8c8d',
  },
  infoValue: {
    fontSize: 14,
    fontWeight: '600',
    color: '#2c3e50',
  },
});

export default AIDetectionScreen;

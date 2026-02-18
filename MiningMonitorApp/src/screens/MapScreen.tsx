import React, {useEffect, useState} from 'react';
import {View, StyleSheet, ActivityIndicator, Text} from 'react-native';
import MapView, {Marker, PROVIDER_GOOGLE, Callout} from 'react-native-maps';
import {getMiningSites} from '../services/api';

interface MiningSite {
  id: string;
  name: string;
  latitude: number;
  longitude: number;
  status: string;
  area: number;
  detectionDate: string;
}

const MapScreen = () => {
  const [sites, setSites] = useState<MiningSite[]>([]);
  const [loading, setLoading] = useState(true);

  // Chingola District coordinates
  const INITIAL_REGION = {
    latitude: -12.5328,
    longitude: 27.8639,
    latitudeDelta: 0.3,
    longitudeDelta: 0.3,
  };

  useEffect(() => {
    loadMiningSites();
  }, []);

  const loadMiningSites = async () => {
    try {
      const data = await getMiningSites();
      setSites(data);
    } catch (error) {
      console.error('Failed to load sites:', error);
    } finally {
      setLoading(false);
    }
  };

  const getMarkerColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'active':
        return '#e74c3c'; // Red
      case 'abandoned':
        return '#95a5a6'; // Gray
      case 'monitoring':
        return '#f39c12'; // Orange
      default:
        return '#667eea'; // Blue
    }
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#667eea" />
        <Text style={styles.loadingText}>Loading mining sites...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <MapView
        provider={PROVIDER_GOOGLE}
        style={styles.map}
        initialRegion={INITIAL_REGION}
        showsUserLocation
        showsMyLocationButton
        showsCompass
        showsScale
        toolbarEnabled>
        {sites.map(site => (
          <Marker
            key={site.id}
            coordinate={{
              latitude: site.latitude,
              longitude: site.longitude,
            }}
            pinColor={getMarkerColor(site.status)}
            title={site.name}>
            <Callout>
              <View style={styles.callout}>
                <Text style={styles.calloutTitle}>{site.name}</Text>
                <Text style={styles.calloutText}>Status: {site.status}</Text>
                <Text style={styles.calloutText}>Area: {site.area} ha</Text>
                <Text style={styles.calloutText}>
                  Detected: {new Date(site.detectionDate).toLocaleDateString()}
                </Text>
              </View>
            </Callout>
          </Marker>
        ))}
      </MapView>

      <View style={styles.legend}>
        <Text style={styles.legendTitle}>Legend</Text>
        <View style={styles.legendItem}>
          <View style={[styles.legendDot, {backgroundColor: '#e74c3c'}]} />
          <Text style={styles.legendText}>Active Mining</Text>
        </View>
        <View style={styles.legendItem}>
          <View style={[styles.legendDot, {backgroundColor: '#f39c12'}]} />
          <Text style={styles.legendText}>Monitoring</Text>
        </View>
        <View style={styles.legendItem}>
          <View style={[styles.legendDot, {backgroundColor: '#95a5a6'}]} />
          <Text style={styles.legendText}>Abandoned</Text>
        </View>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  map: {
    flex: 1,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f5f7fa',
  },
  loadingText: {
    marginTop: 12,
    fontSize: 16,
    color: '#7f8c8d',
  },
  callout: {
    padding: 10,
    minWidth: 200,
  },
  calloutTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#2c3e50',
    marginBottom: 6,
  },
  calloutText: {
    fontSize: 14,
    color: '#7f8c8d',
    marginBottom: 3,
  },
  legend: {
    position: 'absolute',
    bottom: 20,
    right: 20,
    backgroundColor: '#fff',
    padding: 15,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: {width: 0, height: 2},
    shadowOpacity: 0.2,
    shadowRadius: 4,
    elevation: 5,
  },
  legendTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#2c3e50',
    marginBottom: 10,
  },
  legendItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 6,
  },
  legendDot: {
    width: 12,
    height: 12,
    borderRadius: 6,
    marginRight: 8,
  },
  legendText: {
    fontSize: 12,
    color: '#7f8c8d',
  },
});

export default MapScreen;

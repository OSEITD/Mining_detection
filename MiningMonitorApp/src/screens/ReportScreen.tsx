import React, {useState} from 'react';
import {
  View,
  Text,
  StyleSheet,
  TextInput,
  TouchableOpacity,
  ScrollView,
  Alert,
  Image,
} from 'react-native';
import {launchCamera, launchImageLibrary} from 'react-native-image-picker';
import Geolocation from '@react-native-community/geolocation';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import {submitFieldReport} from '../services/api';

const ReportScreen = () => {
  const [location, setLocation] = useState<string>('');
  const [coordinates, setCoordinates] = useState<{
    latitude: number;
    longitude: number;
  } | null>(null);
  const [description, setDescription] = useState<string>('');
  const [photo, setPhoto] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const getCurrentLocation = () => {
    Geolocation.getCurrentPosition(
      position => {
        const {latitude, longitude} = position.coords;
        setCoordinates({latitude, longitude});
        setLocation(`${latitude.toFixed(6)}, ${longitude.toFixed(6)}`);
        Alert.alert('Success', 'GPS location captured!');
      },
      error => {
        Alert.alert('Error', 'Failed to get GPS location: ' + error.message);
      },
      {enableHighAccuracy: true, timeout: 15000, maximumAge: 10000},
    );
  };

  const takePhoto = () => {
    launchCamera(
      {
        mediaType: 'photo',
        quality: 0.8,
        saveToPhotos: true,
      },
      response => {
        if (response.didCancel) {
          return;
        }
        if (response.errorCode) {
          Alert.alert('Error', 'Failed to capture photo: ' + response.errorMessage);
          return;
        }
        if (response.assets && response.assets[0]) {
          setPhoto(response.assets[0].uri!);
        }
      },
    );
  };

  const pickPhoto = () => {
    launchImageLibrary(
      {
        mediaType: 'photo',
        quality: 0.8,
      },
      response => {
        if (response.didCancel) {
          return;
        }
        if (response.errorCode) {
          Alert.alert('Error', 'Failed to pick photo: ' + response.errorMessage);
          return;
        }
        if (response.assets && response.assets[0]) {
          setPhoto(response.assets[0].uri!);
        }
      },
    );
  };

  const handleSubmit = async () => {
    if (!location || !description) {
      Alert.alert('Error', 'Please fill in all required fields');
      return;
    }

    if (!coordinates) {
      Alert.alert('Error', 'Please capture GPS coordinates');
      return;
    }

    setLoading(true);
    try {
      await submitFieldReport({
        location,
        coordinates,
        description,
        photo,
        timestamp: new Date().toISOString(),
      });

      Alert.alert('Success', 'Field report submitted successfully!');
      
      // Reset form
      setLocation('');
      setCoordinates(null);
      setDescription('');
      setPhoto(null);
    } catch (error) {
      Alert.alert('Error', 'Failed to submit report. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>📝 Field Report</Text>
        <Text style={styles.subtitle}>
          Report new mining activity or suspicious sites
        </Text>
      </View>

      <View style={styles.form}>
        <Text style={styles.label}>GPS Location *</Text>
        <View style={styles.locationRow}>
          <TextInput
            style={[styles.input, styles.locationInput]}
            placeholder="Tap button to capture GPS"
            value={location}
            editable={false}
          />
          <TouchableOpacity
            style={styles.gpsButton}
            onPress={getCurrentLocation}>
            <Icon name="crosshairs-gps" size={24} color="#fff" />
          </TouchableOpacity>
        </View>

        <Text style={styles.label}>Description *</Text>
        <TextInput
          style={[styles.input, styles.textArea]}
          placeholder="Describe the mining activity, approximate size, equipment observed, etc."
          value={description}
          onChangeText={setDescription}
          multiline
          numberOfLines={6}
          textAlignVertical="top"
        />

        <Text style={styles.label}>Photo Evidence</Text>
        <View style={styles.photoContainer}>
          {photo ? (
            <View>
              <Image source={{uri: photo}} style={styles.photoPreview} />
              <TouchableOpacity
                style={styles.removePhotoButton}
                onPress={() => setPhoto(null)}>
                <Icon name="close-circle" size={24} color="#e74c3c" />
              </TouchableOpacity>
            </View>
          ) : (
            <View style={styles.photoButtons}>
              <TouchableOpacity style={styles.photoButton} onPress={takePhoto}>
                <Icon name="camera" size={32} color="#667eea" />
                <Text style={styles.photoButtonText}>Take Photo</Text>
              </TouchableOpacity>
              <TouchableOpacity style={styles.photoButton} onPress={pickPhoto}>
                <Icon name="image" size={32} color="#667eea" />
                <Text style={styles.photoButtonText}>Choose Photo</Text>
              </TouchableOpacity>
            </View>
          )}
        </View>

        <TouchableOpacity
          style={[styles.submitButton, loading && styles.submitButtonDisabled]}
          onPress={handleSubmit}
          disabled={loading}>
          <Icon name="send" size={20} color="#fff" />
          <Text style={styles.submitText}>
            {loading ? 'Submitting...' : 'Submit Report'}
          </Text>
        </TouchableOpacity>

        <View style={styles.infoBox}>
          <Icon name="information" size={20} color="#667eea" />
          <Text style={styles.infoText}>
            Reports are sent to the mining authority for investigation. GPS
            coordinates and photos help with verification.
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
  form: {
    padding: 20,
  },
  label: {
    fontSize: 14,
    fontWeight: '600',
    color: '#2c3e50',
    marginBottom: 8,
    marginTop: 15,
  },
  input: {
    backgroundColor: '#fff',
    borderRadius: 8,
    padding: 12,
    fontSize: 14,
    borderWidth: 1,
    borderColor: '#e1e8ed',
  },
  locationRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  locationInput: {
    flex: 1,
    marginRight: 10,
  },
  gpsButton: {
    backgroundColor: '#667eea',
    borderRadius: 8,
    padding: 12,
    justifyContent: 'center',
    alignItems: 'center',
  },
  textArea: {
    height: 120,
    textAlignVertical: 'top',
  },
  photoContainer: {
    marginTop: 10,
    marginBottom: 20,
  },
  photoButtons: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  photoButton: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 20,
    alignItems: 'center',
    width: '45%',
    borderWidth: 2,
    borderColor: '#667eea',
    borderStyle: 'dashed',
  },
  photoButtonText: {
    marginTop: 8,
    fontSize: 12,
    color: '#667eea',
    fontWeight: '600',
  },
  photoPreview: {
    width: '100%',
    height: 200,
    borderRadius: 12,
    resizeMode: 'cover',
  },
  removePhotoButton: {
    position: 'absolute',
    top: 10,
    right: 10,
    backgroundColor: '#fff',
    borderRadius: 12,
  },
  submitButton: {
    backgroundColor: '#667eea',
    borderRadius: 12,
    padding: 16,
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 20,
    shadowColor: '#000',
    shadowOffset: {width: 0, height: 2},
    shadowOpacity: 0.2,
    shadowRadius: 4,
    elevation: 3,
  },
  submitButtonDisabled: {
    backgroundColor: '#95a5a6',
  },
  submitText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
    marginLeft: 8,
  },
  infoBox: {
    flexDirection: 'row',
    backgroundColor: '#ebf5fb',
    borderRadius: 8,
    padding: 15,
    marginTop: 20,
  },
  infoText: {
    flex: 1,
    marginLeft: 10,
    fontSize: 13,
    color: '#667eea',
    lineHeight: 18,
  },
});

export default ReportScreen;

"""
Send notifications via Supabase Realtime
When alert is inserted, all subscribed clients receive it instantly
"""

from supabase import create_client
from datetime import datetime

SUPABASE_URL = "https://ntkzaobvbsppxbljamvb.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im50a3phb2J2YnNwcHhibGphbXZiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjIzNzM2MDAsImV4cCI6MjA3Nzk0OTYwMH0.Tq3N_1Kta0eGZOQiFolcyS5L3NjTAlgHBqUlq5-cqxw"

class NotificationService:
    def __init__(self):
        self.supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    def create_mining_alert(self, 
                           title: str,
                           message: str,
                           area_change_ha: float,
                           change_percent: float,
                           severity: str = None,
                           image_date: str = None):
        """
        Create a mining alert - subscribers will receive it instantly via Supabase Realtime
        
        Args:
            title: Alert title (e.g., "New Mining Activity Detected")
            message: Detailed message
            area_change_ha: Area change in hectares
            change_percent: Percentage change
            severity: 'low', 'medium', 'high', 'critical' (auto-calculated if None)
            image_date: Date of satellite image (YYYY-MM-DD)
        
        Returns:
            Alert ID if successful, None otherwise
        """
        
        # Auto-determine severity based on change
        if severity is None:
            if area_change_ha > 10:
                severity = 'critical'
            elif area_change_ha > 5:
                severity = 'high'
            elif area_change_ha > 1:
                severity = 'medium'
            else:
                severity = 'low'
        
        alert_data = {
            'alert_type': 'mining_detected',
            'severity': severity,
            'title': title,
            'message': message,
            'location': 'Chingola, Zambia',
            'latitude': -12.5,
            'longitude': 27.85,
            'area_change_ha': float(area_change_ha),
            'change_percent': float(change_percent),
            'image_date': image_date or datetime.now().strftime('%Y-%m-%d'),
            'status': 'unread',
            'requires_action': severity in ['high', 'critical']
        }
        
        try:
            response = self.supabase.table('mining_alerts').insert(alert_data).execute()
            
            if response.data and len(response.data) > 0:
                alert_id = response.data[0]['id']
                print(f" Alert created: ID {alert_id}")
                print(f" Realtime notification sent to all subscribers")
                print(f"   Severity: {severity.upper()}")
                print(f"   Change: +{area_change_ha} ha ({change_percent:+.1f}%)")
                return alert_id
            else:
                print(" Failed to create alert")
                return None
                
        except Exception as e:
            print(f" Error creating alert: {e}")
            return None
    
    def mark_alert_as_read(self, alert_id: int):
        """Mark alert as read"""
        try:
            self.supabase.table('mining_alerts') \
                .update({'status': 'read', 'read_at': datetime.now().isoformat()}) \
                .eq('id', alert_id) \
                .execute()
            print(f" Alert {alert_id} marked as read")
        except Exception as e:
            print(f" Error marking alert as read: {e}")
    
    def resolve_alert(self, alert_id: int):
        """Mark alert as resolved"""
        try:
            self.supabase.table('mining_alerts') \
                .update({'status': 'resolved', 'resolved_at': datetime.now().isoformat()}) \
                .eq('id', alert_id) \
                .execute()
            print(f" Alert {alert_id} resolved")
        except Exception as e:
            print(f" Error resolving alert: {e}")
    
    def get_unread_alerts(self):
        """Get all unread alerts"""
        try:
            response = self.supabase.table('mining_alerts') \
                .select('*') \
                .eq('status', 'unread') \
                .order('created_at', desc=True) \
                .execute()
            
            return response.data if response.data else []
        except Exception as e:
            print(f" Error fetching alerts: {e}")
            return []
    
    def get_all_alerts(self, limit=50):
        """Get all alerts (for dashboard)"""
        try:
            response = self.supabase.table('mining_alerts') \
                .select('*') \
                .order('created_at', desc=True) \
                .limit(limit) \
                .execute()
            
            return response.data if response.data else []
        except Exception as e:
            print(f" Error fetching alerts: {e}")
            return []


# Example usage and testing
if __name__ == "__main__":
    print("=" * 60)
    print(" SUPABASE REALTIME NOTIFICATION TEST")
    print("=" * 60)
    
    service = NotificationService()
    
    # Test 1: Low severity
    print("\n Test 1: Low severity alert")
    service.create_mining_alert(
        title="Minor Activity Detected",
        message="Small change detected in Chingola sector 3. Area: 0.5 hectares. Monitor for continued activity.",
        area_change_ha=0.5,
        change_percent=2.3,
        image_date="2025-11-08"
    )
    
    # Test 2: Medium severity
    print("\n Test 2: Medium severity alert")
    service.create_mining_alert(
        title="New Mining Activity",
        message="Moderate expansion detected in Chingola sector 7. Area: 2.8 hectares. Field inspection recommended.",
        area_change_ha=2.8,
        change_percent=8.5,
        image_date="2025-11-08"
    )
    
    # Test 3: High severity
    print("\n Test 3: High severity alert")
    service.create_mining_alert(
        title=" Significant Mining Expansion",
        message="Large mining expansion detected in Chingola district. Area: 6.5 hectares. Immediate inspection required!",
        area_change_ha=6.5,
        change_percent=18.3,
        image_date="2025-11-08"
    )
    
    # Test 4: Critical severity
    print("\n Test 4: CRITICAL severity alert")
    service.create_mining_alert(
        title=" URGENT: Major Illegal Mining Detected",
        message="CRITICAL: Massive mining operation detected in protected area. Area: 12.3 hectares. IMMEDIATE action required! Contact authorities NOW!",
        area_change_ha=12.3,
        change_percent=45.7,
        image_date="2025-11-08"
    )
    
    print("\n" + "=" * 60)
    print(" Test notifications sent!")
    print("=" * 60)
    print("\n Check your dashboard and mobile app")
    print("   Notifications should appear INSTANTLY via Supabase Realtime")
    print("\n Open your Streamlit dashboard to see them in real-time!")

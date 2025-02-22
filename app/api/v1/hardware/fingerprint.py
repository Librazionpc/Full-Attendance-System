import hashlib

def recognize_fingerprint(fingerprint_data):
    """Process the fingerprint and return a hash."""
    try:
        # Assuming fingerprint_data is a string or byte data from the sensor
        fingerprint_hash = hashlib.sha256(fingerprint_data.encode('utf-8')).hexdigest()
        return fingerprint_hash
    except Exception as e:
        print(f"Error recognizing fingerprint: {e}")
        return None

import cv2
import numpy as np
# from deepface import DeepFace
import hashlib

# async def recognize_face(image_path):
#     """Process the image and return a hash of the recognized face."""
#     try:
#         # Perform face recognition using DeepFace (or another method)
#         result = DeepFace.find(image_path=image_path, db_path="path_to_face_database")

#         if result:
#             # Assuming the result contains a list of matches, we hash the result for consistency
#             face_data = result[0]['identity']
#             face_hash = hashlib.sha256(face_data.encode('utf-8')).hexdigest()
#             return face_hash
#         else:
#             raise Exception("No face detected")
    
#     except Exception as e:
#         print(f"Error recognizing face: {e}")
#         return None

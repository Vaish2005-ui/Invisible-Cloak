import tensorflow as tf
import tensorflow_hub as hub

print("⏳ Downloading model...")

# Corrected model URL
model = hub.load("https://tfhub.dev/google/deeplabv3-mobilenetv2/1")

print("✅ Model downloaded and loaded successfully!")

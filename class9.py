import mlcroissant as mlc
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import kagglehub
import os
from PIL import Image
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout, BatchNormalization
from keras.optimizers import Adam
from keras.losses import SparseCategoricalCrossentropy
from keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from keras.utils import image_dataset_from_directory
from sklearn.metrics import f1_score, classification_report, confusion_matrix
import seaborn as sns

# Download latest version
path = kagglehub.dataset_download("fernando2rad/x-ray-lung-diseases-images-9-classes")
print("Path to dataset files:", path)

# Find image files
image_files = []
for root, _, files in os.walk(path):
    for file in files:
        if file.lower().endswith(('.jpeg', '.jpg', '.png')):
            image_files.append(os.path.join(root, file))

print(f"Found {len(image_files)} image files.")

# Step 1: Determine class labels and create mapping
class_names = [os.path.basename(os.path.dirname(img_path)) for img_path in image_files]
unique_class_names = sorted(list(set(class_names)))
label_encoder = LabelEncoder()
encoded_labels = label_encoder.fit_transform(class_names)
class_mapping = dict(zip(unique_class_names, label_encoder.transform(unique_class_names)))

print("Class mapping:", class_mapping)

# Steps 2 & 3: Load, resize, convert to NumPy array, and extract labels
image_size = (128, 128)
images = []
labels = []

print(f"Loading and processing {len(image_files)} images...")
for i, image_file in enumerate(image_files):
    if i % 100 == 0:
        print(f"Processing image {i+1}/{len(image_files)} ({((i+1)/len(image_files)*100):.1f}%)")
    
    try:
        img = Image.open(image_file).convert('RGB')
        img = img.resize(image_size)
        img_array = np.array(img)
        images.append(img_array)

        dir_name = os.path.basename(os.path.dirname(image_file))
        labels.append(class_mapping[dir_name])

    except Exception as e:
        print(f"Error loading image {image_file}: {e}")

print("Image processing completed!")

# Step 4: Convert lists to NumPy arrays
images = np.array(images)
labels = np.array(labels)

print("Shape of images array:", images.shape)
print("Shape of labels array:", labels.shape)

# Step 5: Normalize the image data
images = images.astype('float32') / 255.0

# Step 6: Split data into training and validation sets
X_train, X_val, y_train, y_val = train_test_split(
    images, labels, test_size=0.2, random_state=42, stratify=labels
)

print("Shape of X_train:", X_train.shape)
print("Shape of X_val:", X_val.shape)
print("Shape of y_train:", y_train.shape)
print("Shape of y_val:", y_val.shape)

# IMPROVED MODEL ARCHITECTURE
num_classes = len(unique_class_names)

model = Sequential([
    # Input layer
    Conv2D(32, (3, 3), activation='relu', input_shape=(image_size[0], image_size[1], 3)),
    BatchNormalization(),
    Conv2D(32, (3, 3), activation='relu'),
    BatchNormalization(),
    MaxPooling2D((2, 2)),
    Dropout(0.25),
    
    # Second conv block
    Conv2D(64, (3, 3), activation='relu'),
    BatchNormalization(),
    Conv2D(64, (3, 3), activation='relu'),
    BatchNormalization(),
    MaxPooling2D((2, 2)),
    Dropout(0.25),
    
    # Third conv block
    Conv2D(128, (3, 3), activation='relu'),
    BatchNormalization(),
    Conv2D(128, (3, 3), activation='relu'),
    BatchNormalization(),
    MaxPooling2D((2, 2)),
    Dropout(0.25),
    
    # Flatten and dense layers
    Flatten(),
    Dense(512, activation='relu'),
    BatchNormalization(),
    Dropout(0.5),
    Dense(256, activation='relu'),
    BatchNormalization(),
    Dropout(0.5),
    Dense(num_classes, activation='softmax')
])

# Display the model summary
model.summary()

# Compile with improved settings
model.compile(
    optimizer=Adam(learning_rate=0.001),
    loss=SparseCategoricalCrossentropy(),
    metrics=['accuracy']
)

print("Model compiled successfully.")

# CALLBACKS FOR BETTER TRAINING
callbacks = [
    EarlyStopping(
        monitor='val_loss',
        patience=5,
        restore_best_weights=True,
        verbose=1
    ),
    ModelCheckpoint(
        'best_lung_disease_model.h5',
        monitor='val_accuracy',
        save_best_only=True,
        verbose=1
    ),
    ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.5,
        patience=3,
        min_lr=1e-7,
        verbose=1
    )
]

# Train with callbacks (data augmentation handled differently in newer Keras)
epochs = 18
print(f"Starting improved model training for {epochs} epochs...")
print("Training with improved architecture and callbacks...")

history = model.fit(
    X_train, y_train,
    batch_size=32,
    epochs=epochs,
    validation_data=(X_val, y_val),
    callbacks=callbacks,
    verbose=1
)

print("Model training finished.")

# EVALUATION AND VISUALIZATION
loss, accuracy = model.evaluate(X_val, y_val, verbose=0)
print(f"Validation Loss: {loss:.4f}")
print(f"Validation Accuracy: {accuracy:.4f}")

# Get predictions
y_pred_proba = model.predict(X_val)
y_pred = np.argmax(y_pred_proba, axis=1)

# Calculate F1 score
f1 = f1_score(y_val, y_pred, average='weighted')
print(f"Validation F1 Score: {f1:.4f}")

# Classification report
print("\nClassification Report:")
print(classification_report(y_val, y_pred, target_names=unique_class_names))

# Plot training history
plt.figure(figsize=(12, 4))

plt.subplot(1, 2, 1)
plt.plot(history.history['accuracy'], label='Training Accuracy')
plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
plt.title('Model Accuracy')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.legend()

plt.subplot(1, 2, 2)
plt.plot(history.history['loss'], label='Training Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.title('Model Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()

plt.tight_layout()
plt.savefig('training_history.png', dpi=300, bbox_inches='tight')
plt.show()

# Confusion Matrix
plt.figure(figsize=(10, 8))
cm = confusion_matrix(y_val, y_pred)
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
            xticklabels=unique_class_names, 
            yticklabels=unique_class_names)
plt.title('Confusion Matrix')
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.xticks(rotation=45, ha='right')
plt.yticks(rotation=0)
plt.tight_layout()
plt.savefig('confusion_matrix.png', dpi=300, bbox_inches='tight')
plt.show()

print("Model saved as 'best_lung_disease_model.h5'")
print("Training plots saved as 'training_history.png' and 'confusion_matrix.png'") 
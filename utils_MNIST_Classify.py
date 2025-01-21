from PIL import Image
import numpy as np

def predict_user_image(image_path, model):
    # Load the image
    img = Image.open(image_path).convert('L')  # Convert to grayscale
    img = img.resize((28, 28))  # Resize to 28x28 pixels
    img_array = np.array(img)
    img_array = img_array / 255.0  # Normalize pixel values
    img_array = img_array.reshape(1, 28, 28, 1)  # Reshape to match model input (1, 784)

    # Predict the label
    prediction = model.predict(img_array)
    predicted_label = np.argmax(prediction)

    return predicted_label

def predict_user_image_with_empty_check(image_path, model, threshold=0.6):
    """
    Predict the label for a user-provided image. 
    If the highest probability is below the threshold, classify it as empty (label 0).
    
    Parameters:
    - image_path: Path to the image file.
    - model: Trained Keras model.
    - threshold: Probability threshold for empty box classification.
    
    Returns:
    - Predicted label (int).
    """
    # Load and preprocess the image
    img = Image.open(image_path).convert('L')  # Convert to grayscale
    img = img.resize((28, 28))  # Resize to 28x28 pixels
    img_array = np.array(img) / 255.0  # Normalize pixel values to [0, 1]
    img_array = img_array.reshape(1, 28, 28, 1)  # Reshape for the model input

    # Get the predicted probabilities
    probabilities = model.predict(img_array)

    # Find the highest probability and its corresponding label
    max_prob = np.max(probabilities)
    predicted_label = np.argmax(probabilities)

    # Check if the highest probability is below the threshold
    if max_prob < threshold:
        return 0  # Label as empty
    else:
        return predicted_label
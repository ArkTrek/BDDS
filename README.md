# Brain Disease Detection System (BDDS)
BDDS is an AI-based system designed to detect six different brain diseases from MRI images. This system uses Convolutional Neural Networks (CNNs) to analyze and classify MRI images into distinct disease categories. It aims to assist in early diagnosis and improve the treatment process for neurological conditions.

## Features
1. Supports Detection of Six Brain Diseases:
- Brain Tumor
- Acute Ischemic Stroke
- Alzheimer’s Disease
- Traumatic Brain Injury (TBI)
- Multiple Sclerosis
- Epilepsy

---
  
2. Deep Learning Model Architecture:
- Utilizes CNN layers to extract features from MRI images.
- Regularization through dropout layers to prevent overfitting.
- Softmax activation function for multi-class classification.

---

3. Data Augmentation:
- Random rotations, zooming, shifts, and flips to improve model generalization.
 
---

3. Early Stopping & Model Checkpoints:
- Automatically halts training when validation loss stops improving.
- Saves the best model based on validation performance.

--- 

## Dataset
The dataset used in this project contains MRI images, categorized into six classes. There are:

- 58,145 training images
- 14,534 validation images
Ensure that the dataset is structured into separate folders for each class (i.e., 'Brain Tumor', 'Alzheimer's', etc.).

## Installation
To set up and run the BDDS project, follow these instructions:

1. Clone the Repository:
  Bash
``` 
git clone https://github.com/arktrek/BDDS.git
```

2. Install the Required Dependencies:
Install the necessary Python packages using pip:
```
pip install -r requirements.txt
```

3. Prepare Your Dataset:
Ensure the dataset is properly structured into subdirectories for each class, and place the dataset in the correct folder.

4. Resize the Images (Optional):
Resize all images in the dataset to the required input size (224x224) using the resize_images.py script. The script will convert all images to PNG format and save them:
Python
```
python resizer.py

```

## Model Architecture
The BDDS system uses a deep Convolutional Neural Network (CNN) for brain disease classification. The architecture includes:

- Convolutional Layers: Extract features from the input MRI images.
- MaxPooling Layers: Downsample the feature maps.
- Flatten Layer: Flatten the data for the fully connected layers.
- Dense Layers: Fully connected layers for classification.
- Dropout Layer: Prevent overfitting during training.
- Softmax Output: Multi-class classification for six diseases.

Summary of Model Layers:
- Conv2D: Multiple layers with ReLU activation for feature extraction.
- MaxPooling2D: Reduces the dimensionality.
- Dense (Fully Connected): Connects all neurons to the output classes.
- Dropout: Adds regularization to prevent overfitting.
- Softmax: Outputs probabilities for each class.


## Contributing:
Feel free to submit issues or pull requests if you'd like to contribute to this project.

## Contact: 
For any questions or collaboration opportunities, please contact me via my GitHub profile: [Arpit Ramesan](mailto:arpitramesan777@gmail.com)

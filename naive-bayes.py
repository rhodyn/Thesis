# Import required libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.feature_extraction.text import CountVectorizer
import joblib
import os

# Read file input
data = pd.read_csv('combined-test.csv')
X = data['text']
y = data['label']

# Splits data into testing / training sets (30% test split)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Forms the bag of words
vectorizer = CountVectorizer()
X_train_vectorized = vectorizer.fit_transform(X_train)
X_test_vectorized = vectorizer.transform(X_test)

# Check for generated bag of words
# print("Vocabulary:", vectorizer.get_feature_names_out())

# Model training
model = MultinomialNB(alpha=1)
model.fit(X_train_vectorized, y_train)

# Checking of model accuracy on test data
# accuracy = accuracy_score(y_test, y_pred)
# conf_matrix = confusion_matrix(y_test, y_pred)

# print(f'Accuracy: {accuracy *100}%')

# class_labels = np.unique(y_test)

# plt.figure(figsize=(8, 6))
# sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues', xticklabels=class_labels, yticklabels=class_labels)
# plt.title('Confusion Matrix Heatmap')
# plt.xlabel('Predicted Label')
# plt.ylabel('True Label')
# plt.show()

# Exports the trained model to pkl file
os.makedirs('models', exist_ok=True)
joblib.dump(vectorizer, 'models/vectorizer.pkl')
joblib.dump(model, 'models/naive_bayes-model.pkl')
print("Naive Bayes model saved to models/naive_bayes-model.pkl")

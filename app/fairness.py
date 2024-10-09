import tensorflow as tf
from tensorflow.keras import layers, models
import numpy as np

# Generate some synthetic data (for example purposes)
# X: Input features (e.g., customer data), y: target variable (e.g., loan approval)
# sensitive_attr: sensitive attribute (e.g., gender: 0 or 1)
num_samples = 1000
input_dim = 10

X = np.random.rand(num_samples, input_dim)
y = (X[:, 0] + X[:, 1] > 1).astype(int)  # Binary classification target
sensitive_attr = (X[:, 2] > 0.5).astype(int)  # Sensitive attribute (e.g., gender)

# Split into train and test sets
train_size = int(0.8 * num_samples)
X_train, X_test = X[:train_size], X[train_size:]
y_train, y_test = y[:train_size], y[train_size:]
sensitive_train, sensitive_test = sensitive_attr[:train_size], sensitive_attr[train_size:]

# Build the Predictor model
def build_predictor(input_dim):
    model = models.Sequential([
        layers.InputLayer(input_shape=(input_dim,)),
        layers.Dense(32, activation='relu'),
        layers.Dense(16, activation='relu'),
        layers.Dense(1, activation='sigmoid')  # Binary classification output
    ])
    return model

# Build the Adversary model (takes predictor's output as input)
def build_adversary():
    model = models.Sequential([
        layers.InputLayer(input_shape=(1,)),  # Takes the output of the predictor
        layers.Dense(16, activation='relu'),
        layers.Dense(8, activation='relu'),
        layers.Dense(1, activation='sigmoid')  # Output: sensitive attribute (0 or 1)
    ])
    return model

# Initialize the models
predictor = build_predictor(input_dim)
adversary = build_adversary()

# Optimizers for both models
predictor_optimizer = tf.keras.optimizers.Adam(learning_rate=0.001)
adversary_optimizer = tf.keras.optimizers.Adam(learning_rate=0.001)

# Losses for both models
bce_loss = tf.keras.losses.BinaryCrossentropy()

# Training the models in an adversarial manner
epochs = 50
batch_size = 64
lambda_adv = 0.1  # Strength of the adversarial loss

for epoch in range(epochs):
    # Shuffle training data
    indices = np.arange(train_size)
    np.random.shuffle(indices)
    X_train, y_train, sensitive_train = X_train[indices], y_train[indices], sensitive_train[indices]
    
    # Mini-batch training
    for i in range(0, train_size, batch_size):
        print (X_train.shape)
        X_batch = X_train[i:i + batch_size]
        y_batch = y_train[i:i + batch_size]
        sensitive_batch = sensitive_train[i:i + batch_size]

        with tf.GradientTape(persistent=True) as tape:
            # Predictor forward pass
            predictions = predictor(X_batch, training=True)
            predictor_loss = bce_loss(y_batch, predictions)

            # Adversary forward pass (uses the predictions from predictor as input)
            sensitive_pred = adversary(predictions, training=True)
            adversary_loss = bce_loss(sensitive_batch, sensitive_pred)
            
            # Combined loss: predictor loss minus lambda * adversary loss (adversarial regularization)
            total_loss = predictor_loss - lambda_adv * adversary_loss

        # Gradients for both models
        predictor_grads = tape.gradient(total_loss, predictor.trainable_variables)
        adversary_grads = tape.gradient(adversary_loss, adversary.trainable_variables)

        # Apply gradients
        predictor_optimizer.apply_gradients(zip(predictor_grads, predictor.trainable_variables))
        adversary_optimizer.apply_gradients(zip(adversary_grads, adversary.trainable_variables))

    # Log losses
    print(f'Epoch {epoch + 1}/{epochs} - Predictor Loss: {predictor_loss:.4f}, Adversary Loss: {adversary_loss:.4f}')

# Evaluate the Predictor on the test set (ensure fairness)
y_pred_test = predictor.predict(X_test)
test_accuracy = np.mean((y_pred_test > 0.5).astype(int) == y_test)

sensitive_pred_test = adversary.predict(y_pred_test)
bias_score = np.mean((sensitive_pred_test > 0.5).astype(int) == sensitive_test)

print(f"Test Accuracy: {test_accuracy:.4f}")
print(f"Bias Detection Score (Adversary Accuracy): {bias_score:.4f}")


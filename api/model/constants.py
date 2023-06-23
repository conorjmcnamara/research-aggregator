import tensorflow as tf

class Constants:
    NUM_PREPROCESSING_THREADS = 20
    SPLIT_TEST_SIZE = 0.25
    SPLIT_SEED = 25
    AUTO = tf.data.AUTOTUNE
    VECTORIZER_SEQUENCE_LENGTH = 300
    BATCH_SIZE = 300

    EMBEDDING_VECTOR_LENGTH = 600
    EPOCHS = 10
    EARLY_STOP_PATIENCE = 2
    MODEL_FILE = "classifier_model"
    CLASSES_FILE = "classes.pkl"
    PREDICTION_THRESHOLD = 0.5
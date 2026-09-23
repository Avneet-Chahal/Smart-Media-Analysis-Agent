"""
Curated sample educational data for RAG pipeline testing and demonstrations.
"""

SAMPLE_LECTURE_PDF = {
    "filename": "Lecture_05_Deep_Learning_Architectures.pdf",
    "content_type": "pdf",
    "pages": [
        {
            "page_number": 1,
            "text": """Chapter 1: Convolutional Neural Networks (CNNs).
Convolutional Neural Networks are deep neural network architectures specifically designed for grid-structured data like images.
A convolution operation applies a set of learnable kernels or filters across the input tensor.
Feature maps capture spatial hierarchies: early layers capture edges and textures, whereas deeper layers detect high-level semantic objects."""
        },
        {
            "page_number": 2,
            "text": """Chapter 2: Optimization and Gradient Descent.
Stochastic Gradient Descent (SGD) computes parameter updates on mini-batches of size B rather than the entire training set.
The learning rate alpha determines the step magnitude along the negative gradient vector.
Momentum methods accelerate SGD in directions of consistent gradients while dampening oscillations in orthogonal directions."""
        },
        {
            "page_number": 3,
            "text": """Chapter 3: Regularization and Overfitting Prevention.
Overfitting occurs when a model memorizes training noise rather than learning generalized underlying patterns.
Dropout regularization randomly deactivates a subset of neurons with probability p during each training iteration.
Weight decay (L2 Regularization) adds a penalty proportional to the squared magnitude of weights to the objective loss function."""
        }
    ]
}

SAMPLE_VIDEO_TRANSCRIPT = {
    "filename": "Lecture_06_Transformers_and_Attention.mp4",
    "content_type": "video",
    "segments": [
        {
            "timestamp_start": 0.0,
            "timestamp_end": 120.0,
            "text": "Welcome to Lecture 6. Today we discuss the Transformer architecture and the self-attention mechanism that revolutionized Natural Language Processing."
        },
        {
            "timestamp_start": 120.0,
            "timestamp_end": 350.0,
            "text": "In Self-Attention, each token computes Query, Key, and Value vectors via linear projections. The attention weights are computed using the Softmax of the scaled dot-product between Queries and Keys."
        },
        {
            "timestamp_start": 350.0,
            "timestamp_end": 600.0,
            "text": "Multi-Head Attention allows the model to jointly attend to information from different representation subspaces at different positions, preventing information bottlenecks."
        }
    ]
}

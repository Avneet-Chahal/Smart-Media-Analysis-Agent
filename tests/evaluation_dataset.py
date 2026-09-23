"""
Evaluation Dataset for Smart Media Analysis Agent RAG Retrieval & Grounding Evaluation.
Contains balanced in-domain questions (with expected source sections and page numbers)
and out-of-domain / adversarial questions to test hallucination prevention.
"""

EVALUATION_DOCUMENT_CONTENT = [
    {
        "page": 1,
        "section": "Convolutional Neural Networks & Feature Maps",
        "text": (
            "Chapter 1: Convolutional Neural Networks (CNNs).\n"
            "Convolutional Neural Networks utilize learnable kernels to extract spatial feature maps from input images.\n"
            "Convolution operations apply discrete cross-correlations across receptive fields.\n"
            "Pooling layers (such as max pooling and average pooling) reduce spatial dimensionality while preserving dominant feature activations."
        )
    },
    {
        "page": 2,
        "section": "Optimization & Stochastic Gradient Descent",
        "text": (
            "Chapter 2: Optimization and Gradient Descent.\n"
            "Stochastic Gradient Descent (SGD) computes parameter updates on mini-batches rather than the entire dataset.\n"
            "The learning rate alpha controls the step size taken along the negative gradient vector.\n"
            "Momentum accelerates gradient updates in directions of persistent gradient vectors and dampens oscillations."
        )
    },
    {
        "page": 3,
        "section": "Regularization & Dropout",
        "text": (
            "Chapter 3: Regularization and Overfitting Prevention.\n"
            "Overfitting occurs when a neural network memorizes training set noise rather than generalizing to unseen distributions.\n"
            "Dropout regularization randomly deactivates a fraction p of hidden units during forward passes.\n"
            "Weight decay (L2 Regularization) penalizes large weight coefficients by adding a quadratic penalty term to the objective loss function."
        )
    },
    {
        "page": 4,
        "section": "Transformer Multi-Head Self-Attention",
        "text": (
            "Chapter 4: Transformer Architecture & Attention.\n"
            "The scaled dot-product attention mechanism computes attention weights as Softmax(Q * K^T / sqrt(d_k)) * V.\n"
            "Multi-Head Attention projects Queries, Keys, and Values into multiple lower-dimensional representation subspaces.\n"
            "This enables the neural network to jointly attend to contextual information from different positions simultaneously."
        )
    },
    {
        "page": 5,
        "section": "Positional Encodings & Layer Normalization",
        "text": (
            "Chapter 5: Positional Encodings and Residual Connections.\n"
            "Because transformer architectures contain no inherent recurrence or convolution, positional encodings are injected into input embeddings.\n"
            "Sinusoidal functions PE(pos, 2i) = sin(pos / 10000^(2i/d_model)) represent absolute and relative token positions.\n"
            "Each sub-layer employs a residual skip connection followed by Layer Normalization LayerNorm(x + Sublayer(x)) to stabilize gradient backpropagation."
        )
    }
]

EVALUATION_QUERIES = [
    # In-Domain Queries with Ground Truth Source Targets
    {
        "id": "eval_01",
        "query": "How do Convolutional Neural Networks extract spatial feature maps?",
        "expected_page": 1,
        "expected_section": "Convolutional Neural Networks & Feature Maps",
        "expected_keywords": ["learnable kernels", "spatial feature maps", "receptive fields"],
        "is_in_domain": True
    },
    {
        "id": "eval_02",
        "query": "What is the purpose of pooling layers in CNNs?",
        "expected_page": 1,
        "expected_section": "Convolutional Neural Networks & Feature Maps",
        "expected_keywords": ["reduce spatial dimensionality", "dominant feature activations", "pooling"],
        "is_in_domain": True
    },
    {
        "id": "eval_03",
        "query": "How does Stochastic Gradient Descent compute parameter updates?",
        "expected_page": 2,
        "expected_section": "Optimization & Stochastic Gradient Descent",
        "expected_keywords": ["mini-batches", "learning rate alpha", "negative gradient"],
        "is_in_domain": True
    },
    {
        "id": "eval_04",
        "query": "What role does momentum play in Gradient Descent optimization?",
        "expected_page": 2,
        "expected_section": "Optimization & Stochastic Gradient Descent",
        "expected_keywords": ["accelerates gradient updates", "persistent gradient", "dampens oscillations"],
        "is_in_domain": True
    },
    {
        "id": "eval_05",
        "query": "How does Dropout regularization prevent neural network overfitting?",
        "expected_page": 3,
        "expected_section": "Regularization & Dropout",
        "expected_keywords": ["randomly deactivates", "fraction p", "hidden units"],
        "is_in_domain": True
    },
    {
        "id": "eval_06",
        "query": "Explain weight decay and L2 regularization in deep learning.",
        "expected_page": 3,
        "expected_section": "Regularization & Dropout",
        "expected_keywords": ["penalizes large weight coefficients", "quadratic penalty", "loss function"],
        "is_in_domain": True
    },
    {
        "id": "eval_07",
        "query": "What is the formula for scaled dot-product attention in transformers?",
        "expected_page": 4,
        "expected_section": "Transformer Multi-Head Self-Attention",
        "expected_keywords": ["Softmax", "sqrt(d_k)", "Queries, Keys, and Values"],
        "is_in_domain": True
    },
    {
        "id": "eval_08",
        "query": "Why are sinusoidal positional encodings needed in transformer architectures?",
        "expected_page": 5,
        "expected_section": "Positional Encodings & Layer Normalization",
        "expected_keywords": ["no inherent recurrence", "sinusoidal functions", "token positions"],
        "is_in_domain": True
    },
    {
        "id": "eval_09",
        "query": "How does Layer Normalization and residual skip connections stabilize training?",
        "expected_page": 5,
        "expected_section": "Positional Encodings & Layer Normalization",
        "expected_keywords": ["residual skip connection", "LayerNorm", "gradient backpropagation"],
        "is_in_domain": True
    },

    # Out-of-Domain & Adversarial Queries (Must produce is_grounded = False, no hallucination)
    {
        "id": "eval_ood_01",
        "query": "What is the treaty of Versailles and when was it signed?",
        "expected_page": None,
        "expected_section": None,
        "expected_keywords": [],
        "is_in_domain": False
    },
    {
        "id": "eval_ood_02",
        "query": "How does photosynthesis convert sunlight into glucose in plant chloroplasts?",
        "expected_page": None,
        "expected_section": None,
        "expected_keywords": [],
        "is_in_domain": False
    },
    {
        "id": "eval_ood_03",
        "query": "What are the rules of cricket and how many players are in a team?",
        "expected_page": None,
        "expected_section": None,
        "expected_keywords": [],
        "is_in_domain": False
    }
]

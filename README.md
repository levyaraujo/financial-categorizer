# Categorizer

A machine learning project for classifying financial messages into categories using BERTimbau (BERT for Portuguese).

## Project Structure

- `main.py`: Simple hello-world entry point.
- `src/`
  - `main.py`: Trains a BERT-based classifier on financial messages.
  - `inference.py`: Loads a trained model and predicts the category of new messages.
  - `dataset.py`: Generates a synthetic dataset of financial messages.
- `financial_messages.csv`: The dataset used for training.
- `label_encoder.joblib`: Label encoder for mapping categories.
- `pyproject.toml`: Project dependencies.

## Setup

1. **Clone the repository** and navigate to the project directory.

2. **Install Python 3.12+** if you don't have it.

3. **Create a virtual environment** (recommended):

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

4. **Install dependencies**:

   ```bash
   pip install -U pip
   pip install -r requirements.txt
   # OR, if using PEP 621/pyproject.toml:
   pip install .
   ```

   If you use `uv` or another modern installer, you can also run:

   ```bash
   uv pip install -r requirements.txt
   ```

## Usage

### 1. Generate the Dataset (Optional)

If you want to regenerate the dataset:

```bash
python src/dataset.py
```

This will create or overwrite `financial_messages.csv`.

### 2. Train the Model

```bash
python src/main.py
```

This will:
- Load and preprocess the dataset.
- Train a BERT-based classifier.
- Save the label encoder to `label_encoder.joblib`.
- Save model checkpoints to the `results/` directory.

### 3. Run Inference

After training, you can classify new messages interactively:

```bash
python src/inference.py
```

You'll be prompted to enter a message, and the script will output the predicted category.

## Notes

- The model uses the `neuralmind/bert-base-portuguese-cased` checkpoint from HuggingFace.
- Training and inference require a GPU for reasonable speed, but will work on CPU (slowly).
- Adjust paths in the scripts if you move files or run from a different directory.

## Dependencies

All dependencies are listed in `pyproject.toml`. Key packages:
- `transformers[torch]`
- `pandas`
- `scikit-learn`
- `joblib`
- `datasets`
- `accelerate`

## License

MIT (or specify your license here).

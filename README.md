# Bust the Ghost - Probabilistic AI Game
##  Overview
**Bust the Ghost** is an interactive **grid-based AI game** where players use **probabilistic inference** to locate and capture a hidden ghost. The game employs **Bayesian reasoning** to refine the ghost's possible location based on sensor feedback.

##  Game Mechanics
- The game board consists of a **9x12 grid (108 cells)**.
- The **ghost is randomly positioned** within the grid.
- Players use **sensor readings (color feedback)** to infer the ghost’s location.
- The goal is to **strategically "bust" the ghost** before running out of attempts.

###  Sensor Feedback (Color Codes)
- 🟥 **Red** → The ghost is in the selected cell (**Win**).
- 🟧 **Orange** → The ghost is **1 or 2 cells away**.
- 🟨 **Yellow** → The ghost is **3 or 4 cells away**.
- 🟩 **Green** → The ghost is **5+ cells away**.

### 🔹 Game Features
- **"Bust" Button** → Players attempt to capture the ghost.
- **"Peep" Button** → Reveals probability-based ghost locations.
- **Remaining Attempts & Score** → Tracks player progress.
- **Probabilistic Model** → The game updates ghost probabilities dynamically using **Bayesian inference**.


## AI & Bayesian Inference
- The game starts with a **uniform probability distribution** for the ghost’s location.
- Each sensor reading updates the **posterior probability** using **Bayes’ Theorem**.
- Players refine their guesses **iteratively** to increase accuracy.

### Bayesian Formula Used:
\[
P(G|S) = \frac{P(S|G) \cdot P(G)}{P(S)}
\]
Where:
- \( P(G) \) → Prior probability of ghost location.
- \( P(S|G) \) → Likelihood of observing a sensor reading given the ghost's position.
- \( P(G|S) \) → Posterior probability of ghost being at a location after new evidence.

---

##  Installation & Setup
### 🔹 Prerequisites
- **Python 3.x**
- **Pygame Library**
- **NumPy** (for probability calculations)

### 🔹 Installation
Run the following command to install dependencies:
```bash
pip install pygame numpy

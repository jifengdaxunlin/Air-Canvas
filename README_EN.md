Markdown
# 🎨 Air Canvas - Gesture-Controlled Drawing with OpenCV & MediaPipe

**Python Version:** 3.10.10  
English Version | [中文文档](./README_CH.md)



---

## ✨ Key Features

* **✋ Smart Gesture Recognition**
  * **Select Mode (Index + Middle Finger Up):** Hover over the top UI menu items to make selections (brush size, color, function buttons).
  * **Draw Mode (Index Finger Only Up):** Draw smoothly or erase within the designated painting area.
* **🎨 Two-Tier Interactive UI Menu**
  * **Top Tier (Brush Size & Save):** Offers four stroke sizes (4px, 8px, 15px, 25px) and a `SAVE` button.
  * **Bottom Tier (Color Palette & Tools):** Supports rapid switching between Red, Orange, Yellow, Green, Cyan, Blue, and Purple, along with an Eraser (`ERASER`) and Clear Screen (`CLEAR`).
* **💧 Dynamic Interactive Feedback**
  * Displays a circular selection countdown progress ring when hovering with a fingertip.
  * Triggers a visual ripple animation upon button selection.
* **🖼️ Template Tracing & Real-Time Scoring Algorithm**
  * Supports loading custom background images and blending them seamlessly with the drawing canvas.
  * Built-in scoring algorithm that evaluates real-time similarity based on Precision, Skeleton Coverage (Recall), and an Over-ink Penalty Factor.
* **💾 Transparent Background Canvas Export**
  * Automatically isolates non-white user strokes and saves them as transparent PNG images with a single click (excluding the selected background image).

---

## 🛠️ Prerequisites & Installation

Ensure you have Python 3.8+ installed, then run the following command to install the required dependencies:

```bash
pip install -r requirements.txt
```

---

## 🚀 Quick Start
Place the project code and required Chinese font file (e.g., simhei.ttf or STCAIYUN.TTF) in the same root directory.

Run the main GUI application script:

```Bash
python ui_run_app.py
```
Hand gesture interactions:

Raise Index + Middle fingers and hover over top menu items for ~0.3 seconds to select.

Raise Index finger only to draw or erase freely inside the designated canvas region.

---

## 📂 Project Structure
Plaintext
```
Air Canvas/ 
├── __pycache__/           # Python bytecode cache directory
├── facedata/              # Face data / samples storage directory
├── haar/                  # OpenCV Haar Cascade classifier models
├── model/                 # Trained model files storage directory
├── Pic_example/           # Sample images / tracing background templates
├── Pic_save/              # Directory for saved drawings and artwork
├── draw_ui_source.py      # UI layout and canvas logic source code
├── draw.py                # Core drawing and gesture processing logic
├── icon.png               # Application icon
├── mediapipe_draw.ui      # Qt Designer UI design file
├── README_CH.md           # Chinese project documentation
├── README_EN.md           # English project documentation
├── requirements.txt       # Project dependencies list
├── STCAIYUN.TTF           # Chinese font file (STCaiyun / 华文彩云)
└── ui_run_app.py          # Main application entry point (Launches GUI)
```
---

## 📝 License
This project is open-sourced under the MIT License.
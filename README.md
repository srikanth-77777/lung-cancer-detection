---
title: Lung Cancer AI Diagnostic
emoji: 🫁
colorFrom: blue
colorTo: indigo
sdk: gradio
sdk_version: 4.44.0
app_file: app_gradio.py
pinned: false
license: mit
short_description: ResNet-50 CT Scan Classifier with Grad-CAM and Medical AI Chat
---

# 🫁 AI Lung Cancer Diagnostic & Classification Suite

A clinical decision support prototype leveraging Deep Learning (PyTorch ResNet-50) and Explainable AI (Grad-CAM) to analyze chest CT scans for lung cancer classification and subtyping.

## ✨ Features
1. **4-Class Subtype Classification**: Adenocarcinoma, Large Cell Carcinoma, Squamous Cell Carcinoma, and Normal tissue.
2. **Binary Detection**: Benign vs. Malignant nodule assessment.
3. **Grad-CAM Visual Heatmaps**: Interpretability overlays pinpointing region-of-interest focus areas.
4. **Medical AI Assistant**: Answers clinical staging, heatmap explanations, lung cancer biology, and treatment questions.

## 🚀 Running Locally
```bash
pip install -r requirements.txt
python app_gradio.py
```

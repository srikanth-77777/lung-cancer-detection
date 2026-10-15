"""
================================================================
Hugging Face Spaces — Gradio Interface
Lung Cancer AI Diagnostic System (ResNet-50 + Grad-CAM + AI Chat)
================================================================
"""

import os
import sys
import requests
import numpy as np
import cv2
from PIL import Image
import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import models, transforms
import gradio as gr

# ────────────────────────────────────────────────────────────────
# MODEL DOWNLOAD CONFIG
# ────────────────────────────────────────────────────────────────
MODEL_URL_1 = os.environ.get(
    "MODEL_URL_1",
    "https://huggingface.co/Srikanth77777/best_ResNet50_v5.pth/resolve/main/best_ResNet50_v5.pth"
)
MODEL_URL_2 = os.environ.get(
    "MODEL_URL_2",
    "https://huggingface.co/Srikanth77777/best_ResNet50_v5.pth/resolve/main/resnet50_chest_ct_95acc.pth"
)

EFF_WEIGHTS = "best_ResNet50_v5.pth"
DENSE_WEIGHTS = "resnet50_chest_ct_95acc.pth"

def download_file(url, target_path):
    if os.path.exists(target_path) and os.path.getsize(target_path) > 10_000_000:
        print(f"[OK] {target_path} already exists ({os.path.getsize(target_path)/(1024*1024):.1f} MB).")
        return
    print(f"Downloading {target_path} from {url}...")
    resp = requests.get(url, stream=True)
    resp.raise_for_status()
    with open(target_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=1024 * 1024):
            if chunk:
                f.write(chunk)
    print(f"[SUCCESS] Downloaded {target_path}")

download_file(MODEL_URL_1, EFF_WEIGHTS)
download_file(MODEL_URL_2, DENSE_WEIGHTS)

# ────────────────────────────────────────────────────────────────
# MODEL DEFINITIONS & LOADING
# ────────────────────────────────────────────────────────────────
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

BINARY_CLASSES = ["Benign", "Malignant"]
FOUR_CLASSES   = ["Adenocarcinoma", "Large Cell Carcinoma", "Normal", "Squamous Cell Carcinoma"]

def build_resnet50():
    m = models.resnet50(weights=None)
    in_feat = m.fc.in_features
    m.fc = nn.Sequential(
        nn.Linear(in_feat, 256),
        nn.ReLU(),
        nn.Dropout(0.3),
        nn.Linear(256, 2)
    )
    return m

def build_resnet50_subtype(num_classes=4):
    m = models.resnet50(weights=None)
    in_feat = m.fc.in_features
    m.fc = nn.Sequential(
        nn.Linear(in_feat, 512),
        nn.ReLU(),
        nn.Dropout(0.4),
        nn.Linear(512, num_classes)
    )
    return m

print("Loading models into memory...")
eff_model = build_resnet50().to(device)
eff_model.load_state_dict(torch.load(EFF_WEIGHTS, map_location=device))
eff_model.eval()

dense_model = build_resnet50_subtype(num_classes=4).to(device)
dense_model.load_state_dict(torch.load(DENSE_WEIGHTS, map_location=device))
dense_model.eval()
print("[SUCCESS] Both ResNet-50 models loaded.")

# ────────────────────────────────────────────────────────────────
# GRAD-CAM IMPLEMENTATION
# ────────────────────────────────────────────────────────────────
class GradCAM:
    def __init__(self, model):
        self.model = model
        self.gradients = None
        self.activations = None
        target_layer = self.model.layer4
        target_layer.register_forward_hook(self._forward_hook)
        target_layer.register_full_backward_hook(self._backward_hook)

    def _forward_hook(self, module, inp, out):
        self.activations = out.detach()

    def _backward_hook(self, module, gin, gout):
        self.gradients = gout[0].detach()

    def generate(self, input_tensor, class_idx=None):
        self.model.eval()
        input_tensor = input_tensor.to(device).requires_grad_(True)
        out = self.model(input_tensor)
        if class_idx is None:
            class_idx = out.argmax(dim=1).item()
        self.model.zero_grad()
        out[0][class_idx].backward()

        weights = torch.mean(self.gradients[0], dim=(1, 2), keepdim=True)
        cam = torch.sum(weights * self.activations[0], dim=0).squeeze().cpu().numpy()
        cam = np.maximum(cam, 0)
        if cam.max() > 0:
            cam = cam / cam.max()
        return cam

eff_gradcam = GradCAM(eff_model)
dense_gradcam = GradCAM(dense_model)

# ────────────────────────────────────────────────────────────────
# PREPROCESSING & OVERLAY
# ────────────────────────────────────────────────────────────────
IMG_SIZE = 224

eval_transform = transforms.Compose([
    transforms.ToPILImage(),
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225])
])

def preprocess_image(pil_img):
    img = np.array(pil_img.convert("RGB"))
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    resized_enhanced = cv2.resize(enhanced, (IMG_SIZE, IMG_SIZE))
    rgb_enhanced = cv2.cvtColor(resized_enhanced, cv2.COLOR_GRAY2RGB)
    tensor = eval_transform(rgb_enhanced).unsqueeze(0).to(device)
    return tensor, rgb_enhanced

def make_heatmap_overlay(rgb_img, cam, alpha=0.5):
    h, w, _ = rgb_img.shape
    cam_resized = cv2.resize(cam, (w, h))
    heatmap = (cam_resized * 255).astype(np.uint8)
    heatmap_colored = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)
    heatmap_colored = cv2.cvtColor(heatmap_colored, cv2.COLOR_BGR2RGB)
    overlay = cv2.addWeighted(rgb_img, 1 - alpha, heatmap_colored, alpha, 0)
    return overlay

# Global state to share latest diagnostic with the chatbot
current_session_context = {
    "prediction": "None",
    "confidence": 0.0,
    "stage": "Unknown",
    "subtype": "None",
    "location": "Central Lung Field",
    "model": "None"
}

# ────────────────────────────────────────────────────────────────
# INFERENCE FUNCTIONS
# ────────────────────────────────────────────────────────────────
def predict_subtype(pil_img):
    if pil_img is None:
        return None, {}, "Please upload a CT scan image."
    
    tensor, rgb_img = preprocess_image(pil_img)
    with torch.no_grad():
        logits = dense_model(tensor)
        probs = F.softmax(logits, dim=1)[0].cpu().numpy()
    
    pred_idx = int(np.argmax(probs))
    pred_class = FOUR_CLASSES[pred_idx]
    confidence = float(probs[pred_idx] * 100)

    # Grad-CAM
    cam = dense_gradcam.generate(tensor, pred_idx)
    overlay = make_heatmap_overlay(rgb_img, cam)

    prob_dict = {FOUR_CLASSES[i]: float(probs[i]) for i in range(len(FOUR_CLASSES))}

    # Clinical Note estimation
    if pred_class == "Normal":
        stage = "N/A (Healthy Scan)"
        risk = "Minimal / Normal"
    elif pred_class == "Adenocarcinoma":
        stage = "Stage I / II (Peripheral)"
        risk = "High"
    elif pred_class == "Squamous Cell Carcinoma":
        stage = "Stage II / III (Bronchial/Central)"
        risk = "High"
    else:
        stage = "Stage III (Large / Aggressive)"
        risk = "Critical"

    current_session_context["prediction"] = pred_class
    current_session_context["confidence"] = round(confidence, 1)
    current_session_context["stage"] = stage
    current_session_context["subtype"] = pred_class
    current_session_context["model"] = "4-Class Subtype ResNet-50"

    report = f"""### 📋 AI Diagnostic Report
- **Predicted Class:** `{pred_class}`
- **Model Confidence:** `{confidence:.2f}%`
- **Clinical Staging Estimate:** `{stage}`
- **Risk Level:** `{risk}`
- **Heatmap Finding:** Red/warm highlighted regions indicate dominant features influencing the model's focus.
"""
    return overlay, prob_dict, report

def predict_binary(pil_img):
    if pil_img is None:
        return None, {}, "Please upload a CT scan image."
    
    tensor, rgb_img = preprocess_image(pil_img)
    with torch.no_grad():
        logits = eff_model(tensor)
        probs = F.softmax(logits, dim=1)[0].cpu().numpy()
    
    pred_idx = int(np.argmax(probs))
    pred_class = BINARY_CLASSES[pred_idx]
    confidence = float(probs[pred_idx] * 100)

    # Grad-CAM
    cam = eff_gradcam.generate(tensor, pred_idx)
    overlay = make_heatmap_overlay(rgb_img, cam)

    prob_dict = {BINARY_CLASSES[i]: float(probs[i]) for i in range(len(BINARY_CLASSES))}

    risk = "Low Risk (Non-cancerous nodule)" if pred_class == "Benign" else "High Risk (Malignant lesion detected)"
    
    current_session_context["prediction"] = pred_class
    current_session_context["confidence"] = round(confidence, 1)
    current_session_context["stage"] = "Requires biopsy confirmation" if pred_class == "Malignant" else "Benign"
    current_session_context["subtype"] = pred_class
    current_session_context["model"] = "Binary ResNet-50"

    report = f"""### 📋 Binary Detection Report
- **Diagnosis:** `{pred_class}`
- **Confidence:** `{confidence:.2f}%`
- **Assessment:** `{risk}`
- **Grad-CAM Focus:** Warm colored areas represent areas of suspicion analyzed by the network.
"""
    return overlay, prob_dict, report

# ────────────────────────────────────────────────────────────────
# CHATBOT ENGINE
# ────────────────────────────────────────────────────────────────
def answer_medical_chat(user_msg, chat_history):
    msg = user_msg.lower().strip()
    has_image = (current_session_context["prediction"] != "None")
    pred = current_session_context["prediction"]
    conf = current_session_context["confidence"]
    stage = current_session_context["stage"]

    # 1. Greetings
    if any(k in msg for k in ['hello', 'hi', 'hey', 'good morning', 'good evening', 'greetings']):
        bot_response = "Hello! 👋 I'm your AI Medical Assistant. I can help explain your CT scan results, cancer stages, confidence scores, and heatmaps. Ask me anything!"

    # 2. Results / Prediction
    elif any(k in msg for k in ['predicted', 'prediction', 'result', 'what did you find', 'diagnosis', 'what cancer']):
        if has_image:
            bot_response = f"According to the analysis, the predicted classification is **{pred}** with a confidence score of **{conf}%**."
        else:
            bot_response = "Kindly upload your CT scan image first and run an analysis, and I will summarize the results for you!"

    # 3. Stages
    elif any(k in msg for k in ['stage', 'which stage', 'what stage', 'stage ii', 'stage 2']):
        if has_image:
            bot_response = f"The estimated clinical category is **{stage}**. Note: Definitive cancer staging requires biopsy, TNM assessment, and clinical oncologist consultation."
        else:
            bot_response = "Cancer stages range from Stage 0/I (localized) to Stage IV (distant metastasis). Upload a scan to check the stage estimate!"

    # 4. Confidence Explanation
    elif any(k in msg for k in ['confidence', 'score', 'percent', '41.3', 'reliable', 'accuracy']):
        bot_response = f"Confidence indicates how strongly the model matched visual features to its training data. Current prediction confidence: **{conf}%**. High confidence means stronger pattern resemblance, but clinical review is always necessary."

    # 5. Heatmap & Visualizations
    elif any(k in msg for k in ['heatmap', 'gradcam', 'red area', 'blue area', 'color', 'warm']):
        bot_response = "The Grad-CAM heatmap uses thermal coloring: **Red/warm colors** highlight regions that most strongly influenced the neural network's diagnosis. **Blue/cold colors** had minimal influence."

    # 6. Types of Cancer
    elif any(k in msg for k in ['type', 'types', 'subtype', 'classes', 'detect']):
        bot_response = "Our models detect: **Adenocarcinoma**, **Large Cell Carcinoma**, **Squamous Cell Carcinoma**, and **Normal lung tissue**, as well as **Benign** vs **Malignant** classification."

    # 7. Differences (Adeno vs Squamous)
    elif any(k in msg for k in ['adeno', 'squamous', 'difference']):
        bot_response = "• **Adenocarcinoma**: Often occurs in mucus-secreting glands in outer lung regions; common among non-smokers.\n• **Squamous Cell Carcinoma**: Typically arises in bronchial airways near the chest center, often linked to smoking history."

    # 8. Causes / Smoking
    elif any(k in msg for k in ['smoking', 'cause', 'why lung cancer', 'risk factors']):
        bot_response = "Smoking is the leading risk factor (~85% of cases), but non-smokers can also develop lung cancer due to radon gas, secondhand smoke, air pollution, and genetic predispositions."

    # 9. Treatments & Cure
    elif any(k in msg for k in ['treatment', 'cure', 'surgery', 'chemo', 'radiation']):
        bot_response = "Treatment options include surgery (resection/lobectomy), targeted therapy, immunotherapy, radiation therapy, and chemotherapy, tailored by an oncology multidisciplinary team."

    # 10. Normal vs Abnormal
    elif any(k in msg for k in ['normal', 'abnormal', 'benign', 'malignant']):
        bot_response = "• **Benign / Normal**: Non-cancerous, healthy tissue or stable granulomas.\n• **Malignant**: Active abnormal cellular proliferation that requires immediate clinical intervention."

    # 11. Polite / Thank you
    elif any(k in msg for k in ['thank', 'thanks', 'bye', 'goodbye']):
        bot_response = "You're very welcome! Feel free to ask if you have more questions about CT scans or lung oncology. Take care! 💙"

    # Fallback
    else:
        bot_response = "I can explain CT classifications, subtypes (Adenocarcinoma, Squamous, Large Cell), predicted stage, confidence, heatmaps, and treatment options. Could you clarify your question?"

    chat_history.append((user_msg, bot_response))
    return "", chat_history

# ────────────────────────────────────────────────────────────────
# DEMO IMAGES
# ────────────────────────────────────────────────────────────────
demo_dir = "static/demo_images"
demo_images = []
if os.path.exists(demo_dir):
    for f in sorted(os.listdir(demo_dir)):
        if f.lower().endswith(('.png', '.jpg', '.jpeg')):
            demo_images.append(os.path.join(demo_dir, f))

# ────────────────────────────────────────────────────────────────
# GRADIO BLOCKS UI
# ────────────────────────────────────────────────────────────────
custom_theme = gr.themes.Soft(
    primary_hue="blue",
    secondary_hue="slate"
)

with gr.Blocks(theme=custom_theme, title="AI Lung Cancer Classification & Diagnostics") as demo:
    gr.Markdown("""
    # 🫁 AI Lung Cancer Diagnostic & Classification Suite
    ### Deep Learning-Assisted CT Scan Analysis with Explainable AI (Grad-CAM)
    """)

    with gr.Tabs():
        # TAB 1: 4-CLASS SUBTYPE
        with gr.Tab("🔬 4-Class Subtype Classification"):
            with gr.Row():
                with gr.Column(scale=1):
                    s2_img = gr.Image(type="pil", label="Upload Chest CT Scan")
                    s2_btn = gr.Button("🔍 Analyze Subtype", variant="primary")
                    if demo_images:
                        gr.Examples(examples=demo_images, inputs=s2_img, label="Quick Demo CT Scans")
                with gr.Column(scale=1):
                    s2_cam = gr.Image(label="Grad-CAM Interpretability Overlay")
                    s2_probs = gr.Label(num_top_classes=4, label="Class Probabilities")
                    s2_report = gr.Markdown()
            s2_btn.click(predict_subtype, inputs=s2_img, outputs=[s2_cam, s2_probs, s2_report])

        # TAB 2: BINARY DETECTION
        with gr.Tab("🛡️ Binary Detection (Benign vs Malignant)"):
            with gr.Row():
                with gr.Column(scale=1):
                    s1_img = gr.Image(type="pil", label="Upload CT Slice")
                    s1_btn = gr.Button("🔬 Run Binary Detection", variant="primary")
                    if demo_images:
                        gr.Examples(examples=demo_images, inputs=s1_img, label="Quick Demo CT Scans")
                with gr.Column(scale=1):
                    s1_cam = gr.Image(label="Grad-CAM Heatmap")
                    s1_probs = gr.Label(num_top_classes=2, label="Classification Probabilities")
                    s1_report = gr.Markdown()
            s1_btn.click(predict_binary, inputs=s1_img, outputs=[s1_cam, s1_probs, s1_report])

        # TAB 3: CHATBOT
        with gr.Tab("💬 Medical AI Assistant"):
            gr.Markdown("Ask questions regarding your current scan result, staging, Grad-CAM heatmap, confidence score, or cancer biology!")
            chatbot = gr.Chatbot(height=450)
            with gr.Row():
                chat_in = gr.Textbox(placeholder="E.g., What is the predicted cancer subtype? What does the heatmap mean?", show_label=False, scale=8)
                chat_btn = gr.Button("Send", variant="primary", scale=1)
            
            chat_btn.click(answer_medical_chat, inputs=[chat_in, chatbot], outputs=[chat_in, chatbot])
            chat_in.submit(answer_medical_chat, inputs=[chat_in, chatbot], outputs=[chat_in, chatbot])

            gr.Examples(
                examples=[
                    "What types of lung cancer can your model detect?",
                    "What is the predicted cancer subtype?",
                    "What does the heatmap mean?",
                    "What stage is the cancer?",
                    "What is the difference between adenocarcinoma and squamous cell carcinoma?",
                    "Can lung cancer be cured?"
                ],
                inputs=chat_in
            )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)

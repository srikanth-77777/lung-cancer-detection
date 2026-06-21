"""
================================================================
Grad-CAM — Gradient-weighted Class Activation Mapping
Works for both EfficientNet and ResNet architectures.
================================================================
"""

import cv2
import numpy as np
import torch
import torch.nn.functional as F


class GradCAM:
    def __init__(self, model, model_type="efficientnet"):
        self.model = model
        self.model_type = model_type
        self.gradients = None
        self.activations = None
        self._register_hooks()

    def _register_hooks(self):
        def forward_hook(module, input, output):
            self.activations = output.detach()

        def backward_hook(module, grad_input, grad_output):
            self.gradients = grad_output[0].detach()

        if self.model_type == "efficientnet":
            target_layer = self.model.features[-1]
        elif self.model_type == "resnet":
            target_layer = self.model.layer4
        else:
            target_layer = self.model.features.denseblock4

        target_layer.register_forward_hook(forward_hook)
        target_layer.register_full_backward_hook(backward_hook)

    def generate(self, input_tensor, class_idx=None):
        self.model.eval()

        # Move input to same device as model
        input_tensor = input_tensor.to(
            next(self.model.parameters()).device)
        input_tensor = input_tensor.requires_grad_(True)

        # Forward pass
        output = self.model(input_tensor)

        if class_idx is None:
            class_idx = output.argmax(dim=1).item()

        # Backward pass for target class
        self.model.zero_grad()
        target = output[0][class_idx]
        target.backward()

        # Compute Grad-CAM
        gradients = self.gradients[0]
        activations = self.activations[0]

        # Global average pool gradients
        weights = gradients.mean(dim=(1, 2))

        # Weighted combination — keep on same device
        cam = torch.zeros(
            activations.shape[1:],
            dtype=torch.float32
        ).to(gradients.device)

        for i, w in enumerate(weights):
            cam += w * activations[i]

        # ReLU and move to CPU
        cam = F.relu(cam)
        cam = cam.cpu().numpy()

        if cam.max() > 0:
            cam = cam / cam.max()

        # Resize to 224x224
        cam = cv2.resize(cam, (224, 224))
        return cam, class_idx

    def generate_dual_cam(self, input_tensor, pred_idx, num_classes):
        """
        Generate Grad-CAM for both the predicted class and the
        strongest counter-class (the next highest probability).
        Returns: (pred_cam, counter_cam, counter_idx)
        """
        # Forward pass to get probabilities
        self.model.eval()
        input_tensor = input_tensor.to(
            next(self.model.parameters()).device)

        with torch.no_grad():
            logits = self.model(input_tensor)
            probs = torch.softmax(logits, dim=1)[0]

        # Find counter class — highest prob class that isn't pred
        probs_np = probs.cpu().numpy()
        sorted_idx = np.argsort(probs_np)[::-1]
        counter_idx = int(
            sorted_idx[0] if sorted_idx[0] != pred_idx
            else sorted_idx[1]
        )

        # Generate CAM for predicted class
        pred_cam, _ = self.generate(input_tensor.clone(), pred_idx)

        # Generate CAM for counter class
        counter_cam, _ = self.generate(
            input_tensor.clone(), counter_idx)

        return pred_cam, counter_cam, counter_idx


def generate_explanation_narrative(
    prediction, confidence, cam_analysis,
    class_names, probs_list, is_binary=True
):
    """
    Generate a natural-language AI explanation from
    cam_analysis data and prediction results.
    """
    a = cam_analysis
    pred = prediction
    conf = round(confidence, 1)

    # Confidence quality
    if confidence >= 90:
        conf_q = "high confidence"
        conf_note = "The model shows strong certainty"
    elif confidence >= 70:
        conf_q = "moderate confidence"
        conf_note = (
            "The model shows reasonable certainty, "
            "but clinical correlation is recommended"
        )
    else:
        conf_q = "low confidence"
        conf_note = (
            "The model is uncertain — "
            "manual expert review is strongly advised"
        )

    # Probability gap
    sorted_probs = sorted(probs_list, reverse=True)
    gap = round(sorted_probs[0] - sorted_probs[1], 1) \
        if len(sorted_probs) > 1 else 0
    if gap > 40:
        gap_note = (
            f"with a decisive {gap}% margin over "
            f"the next likely class"
        )
    elif gap > 15:
        gap_note = (
            f"with a moderate {gap}% margin over "
            f"the next alternative"
        )
    else:
        gap_note = (
            f"with only a {gap}% margin — "
            f"the alternative diagnosis was close"
        )

    # Location description
    loc = a.get('location', 'unspecified region')
    shape = a.get('shape', 'nodular')
    size = a.get('size_label', 'Unknown')
    pct = a.get('activation_pct', 0)
    intensity = a.get('intensity_label', 'Unknown')
    mean_int = a.get('mean_intensity', 0)
    spots = a.get('num_spots', 0)
    spread = a.get('spread', 'Localized')

    # Build narrative
    narrative = (
        f"The AI model classified this scan as "
        f"**{pred}** with {conf_q} ({conf}%), "
        f"{gap_note}. "
    )

    narrative += (
        f"The primary region of interest is in the "
        f"**{loc}**, where a **{shape.lower()} mass** "
        f"was identified covering **{pct}%** of the "
        f"scan area ({size} size). "
    )

    narrative += (
        f"The activation intensity is "
        f"**{intensity.lower()}** (mean: {mean_int}), "
    )

    if spots <= 1:
        narrative += (
            "concentrated in a **single focus**, "
            "suggesting localized pathology. "
        )
    elif spots == 2:
        narrative += (
            f"distributed across **{spots} foci**, "
            "suggesting possible bilateral involvement. "
        )
    else:
        narrative += (
            f"distributed across **{spots} foci**, "
            "indicating **diffuse spread** that "
            "warrants urgent attention. "
        )

    narrative += f"{conf_note}."

    # Counter-class insight
    second_idx = int(np.argsort(probs_list)[::-1][1]) \
        if len(probs_list) > 1 else None
    if second_idx is not None:
        second_name = class_names[second_idx]
        second_pct = round(probs_list[second_idx], 1)
        narrative += (
            f" The next most likely classification was "
            f"**{second_name}** at {second_pct}%."
        )

    return narrative


def generate_heatmap_overlay(original_img, cam, alpha=0.4):
    """
    Overlay Grad-CAM heatmap on original image.
    original_img : grayscale numpy array (224x224)
    cam          : grad-cam output (224x224) values 0-1
    Returns      : RGB overlay image
    """
    if len(original_img.shape) == 2:
        img_rgb = cv2.cvtColor(
            original_img.astype(np.uint8),
            cv2.COLOR_GRAY2RGB
        )
    else:
        img_rgb = original_img.astype(np.uint8)

    heatmap = np.uint8(255 * cam)
    heatmap = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)
    heatmap = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)

    overlay = cv2.addWeighted(img_rgb, 1 - alpha, heatmap, alpha, 0)
    return overlay, heatmap


def analyze_heatmap(cam, threshold=0.5):
    """
    Analyze Grad-CAM to determine location, size,
    intensity and number of spots.
    Returns dict with analysis results.
    """
    h, w = cam.shape

    # Threshold to get activated region
    binary = (cam > threshold).astype(np.uint8)

    # Size analysis
    activated_pixels = np.sum(binary)
    total_pixels = h * w
    activation_pct = (activated_pixels / total_pixels) * 100

    if activation_pct < 10:
        size_label = "Small"
        stage_hint = "Early stage suspected"
    elif activation_pct < 30:
        size_label = "Medium"
        stage_hint = "Intermediate stage suspected"
    else:
        size_label = "Large"
        stage_hint = "Advanced stage suspected"

    # Intensity analysis
    if activated_pixels > 0:
        mean_intensity = float(cam[cam > threshold].mean())
    else:
        mean_intensity = 0.0

    if mean_intensity > 0.75:
        intensity_label = "High"
    elif mean_intensity > 0.5:
        intensity_label = "Moderate"
    else:
        intensity_label = "Low"

    # Location analysis
    top_half = cam[:h//2, :]
    bottom_half = cam[h//2:, :]
    left_half = cam[:, :w//2]
    right_half = cam[:, w//2:]
    center = cam[h//4:3*h//4, w//4:3*w//4]

    zone_scores = {
        "upper":   float(top_half.mean()),
        "lower":   float(bottom_half.mean()),
        "left":    float(left_half.mean()),
        "right":   float(right_half.mean()),
        "central": float(center.mean())
    }

    if zone_scores["upper"] > zone_scores["lower"]:
        vertical = "Upper"
    else:
        vertical = "Lower"

    if zone_scores["left"] > zone_scores["right"]:
        horizontal = "Left"
    else:
        horizontal = "Right"

    max_vert = max(zone_scores["upper"], zone_scores["lower"])
    is_central = zone_scores["central"] > max_vert * 0.8

    if is_central:
        location = "Central (near airways/bronchi)"
        location_short = "Central"
    else:
        location = vertical + " " + horizontal + " Lobe"
        location_short = vertical + " " + horizontal

    # Number of spots
    num_labels, _ = cv2.connectedComponents(binary)
    num_spots = num_labels - 1

    if num_spots <= 1:
        spread = "Localized (single region)"
    elif num_spots == 2:
        spread = "Bilateral involvement possible"
    else:
        spread = "Diffuse spread detected"

    # Shape analysis
    contours, _ = cv2.findContours(
        binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        largest = max(contours, key=cv2.contourArea)
        area_c = cv2.contourArea(largest)
        perimeter = cv2.arcLength(largest, True)
        if perimeter > 0:
            circularity = 4 * np.pi * area_c / (perimeter ** 2)
        else:
            circularity = 0
        if circularity > 0.7:
            shape = "Rounded nodular"
        elif circularity > 0.4:
            shape = "Oval / elongated"
        else:
            shape = "Irregular"
    else:
        shape = "Not detected"

    # 8-zone location analysis
    h3, w3 = h // 3, w // 3
    zones_8 = {
        "Top Left":     cam[:h3, :w3],
        "Top":          cam[:h3, w3:2*w3],
        "Top Right":    cam[:h3, 2*w3:],
        "Left":         cam[h3:2*h3, :w3],
        "Right":        cam[h3:2*h3, 2*w3:],
        "Bottom Left":  cam[2*h3:, :w3],
        "Bottom":       cam[2*h3:, w3:2*w3],
        "Bottom Right": cam[2*h3:, 2*w3:]
    }
    zone_means = {k: float(v.mean()) for k, v in zones_8.items()}
    location_8zone = max(zone_means, key=zone_means.get)

    return {
        "location":        location,
        "location_short":  location_short,
        "size_label":      size_label,
        "activation_pct":  round(activation_pct, 1),
        "intensity_label": intensity_label,
        "mean_intensity":  round(mean_intensity, 3),
        "stage_hint":      stage_hint,
        "num_spots":       num_spots,
        "spread":          spread,
        "is_central":      is_central,
        "shape":           shape,
        "location_8zone":  location_8zone
    }

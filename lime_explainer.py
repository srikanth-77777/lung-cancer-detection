"""
================================================================
LIME Explainer — Local Interpretable Model-agnostic Explanations
Generates superpixel-based explanations for CT scan predictions
================================================================
"""

import cv2
import base64
import numpy as np
from PIL import Image
from lime import lime_image
from skimage.segmentation import mark_boundaries


class LimeExplainer:
    def __init__(self, model, transform, device, class_names):
        self.model = model
        self.transform = transform
        self.device = device
        self.class_names = class_names
        self.explainer = lime_image.LimeImageExplainer()

    def _batch_predict(self, images):
        """
        LIME passes numpy arrays (N, H, W, 3) in 0-255 range.
        Convert to tensor and run inference.
        """
        import torch

        batch = []
        for img in images:
            pil = Image.fromarray(img.astype(np.uint8))
            tensor = self.transform(pil)
            batch.append(tensor)

        batch_tensor = torch.stack(batch).to(self.device)

        self.model.eval()
        with torch.no_grad():
            outputs = self.model(batch_tensor)
            probs = torch.softmax(outputs, dim=1)

        return probs.cpu().numpy()

    def explain(self, img_rgb_224, pred_idx,
                num_samples=100, num_features=8):
        """
        Generate LIME explanation for an image.
        img_rgb_224: numpy array (224, 224, 3) uint8
        pred_idx: predicted class index
        Returns: (positive_overlay, mask_overlay, narrative)
        """
        # Run LIME
        try:
            explanation = self.explainer.explain_instance(
                img_rgb_224,
                self._batch_predict,
                top_labels=len(self.class_names),
                hide_color=0,
                num_samples=num_samples,
                batch_size=10
            )
        except Exception as e:
            # Fallback if LIME fails
            return None, None, f"LIME Error: {str(e)}"

        # Get the explanation for the predicted class
        temp_pos, mask_pos = explanation.get_image_and_mask(
            pred_idx,
            positive_only=True,
            num_features=num_features,
            hide_rest=False
        )

        temp_full, mask_full = explanation.get_image_and_mask(
            pred_idx,
            positive_only=False,
            num_features=num_features,
            hide_rest=False
        )

        # Create overlay images
        pos_overlay = mark_boundaries(
            temp_pos / 255.0, mask_pos,
            color=(0.4, 1.0, 0.4), mode='thick'
        )
        pos_overlay = (pos_overlay * 255).astype(np.uint8)

        full_overlay = mark_boundaries(
            temp_full / 255.0, mask_full,
            color=(0.3, 0.6, 1.0), mode='thick'
        )
        full_overlay = (full_overlay * 255).astype(np.uint8)

        # Analyze the mask for narrative
        pos_pixels = np.sum(mask_pos > 0)
        total_pixels = mask_pos.shape[0] * mask_pos.shape[1]
        pos_pct = round((pos_pixels / total_pixels) * 100, 1)

        neg_mask = (mask_full > 0) & (mask_pos == 0)
        neg_pixels = np.sum(neg_mask)
        neg_pct = round((neg_pixels / total_pixels) * 100, 1)

        # Find location of positive superpixels
        if pos_pixels > 0:
            ys, xs = np.where(mask_pos > 0)
            if len(ys) > 0 and len(xs) > 0:
                cy, cx = int(np.mean(ys)), int(np.mean(xs))
                h, w = mask_pos.shape
                v = "upper" if cy < h // 2 else "lower"
                hz = "left" if cx < w // 2 else "right"
                loc_str = f"{v} {hz} region"
            else:
                loc_str = "unspecified region"
        else:
            loc_str = "no clearly dominant region"

        pred_name = self.class_names[pred_idx]
        narrative = (
            f"LIME identified **{pos_pct}%** of the image as "
            f"positively contributing to the **{pred_name}** "
            f"prediction, concentrated in the **{loc_str}**. "
        )

        if neg_pct > 0:
            narrative += (
                f"Additionally, **{neg_pct}%** of superpixels "
                f"showed negative influence (evidence against "
                f"the prediction). "
            )

        if pos_pct > 20:
            narrative += (
                "The large positive region suggests the model "
                "found widespread supporting evidence across "
                "the scan. "
            )
        elif pos_pct > 5:
            narrative += (
                "The focused positive region indicates specific "
                "localized features driving the classification. "
            )
        else:
            narrative += (
                "The small positive area suggests the model "
                "relies on very specific, subtle features. "
            )

        narrative += (
            "LIME provides a complementary view to Grad-CAM "
            "by testing what happens when regions are removed, "
            "rather than where gradients flow."
        )

        return pos_overlay, full_overlay, narrative


def img_to_base64_rgb(img_array):
    """Convert RGB numpy array to base64 string"""
    img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
    _, buffer = cv2.imencode('.png', img_bgr)
    return base64.b64encode(buffer).decode('utf-8')

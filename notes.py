"""
================================================================
Clinical Notes System — 24-Variation Location-Specific Data
Generates dynamic diagnostic notes based on:
- Predicted cancer subtype (3 types + Normal)
- 8-zone heatmap location from Grad-CAM
- Confidence level
================================================================
"""


# ── Subtype clinical data with 8-zone location variants ──────
SUBTYPE_DATA = {

    # ══════════════════════════════════════════════════════════
    # ADENOCARCINOMA — Stage I — ABNORMAL
    # ══════════════════════════════════════════════════════════
    "Adenocarcinoma": {
        "stage": "Stage I",
        "risk": "ABNORMAL",
        "risk_color": "#FF8C00",
        "description": (
            "Adenocarcinoma is the most common type of lung cancer "
            "(~40%), typically found in the outer edges of the lung. "
            "Early-stage detection indicates favorable prognosis "
            "with appropriate intervention."
        ),
        "locations": {
            "Top Left": {
                "location_analysis": (
                    "Tumor identified in the left upper lobe apical "
                    "segment near the subclavian vessels. This "
                    "peripheral location may involve the brachial "
                    "plexus if the superior sulcus is affected. "
                    "Early-stage adenocarcinoma here has favorable "
                    "surgical prognosis with lobectomy."
                ),
                "symptoms": [
                    "Left shoulder and upper arm pain radiating downward",
                    "Persistent dry cough worsening over weeks",
                    "Mild chest discomfort localized to upper left area",
                    "Unexplained fatigue and general weakness",
                    "Occasional shortness of breath during exertion",
                    "Tingling or numbness in the left arm (nerve involvement)",
                    "Mild hoarseness or voice changes",
                    "Night sweats and low-grade intermittent fever"
                ],
                "next_steps": [
                    "CT-guided biopsy of left upper lobe lesion",
                    "PET scan to rule out mediastinal lymph node involvement",
                    "Pulmonary function tests to assess surgical candidacy",
                    "MRI of brachial plexus if shoulder pain present",
                    "Oncology consultation for surgical planning"
                ],
                "treatments": [
                    "Left upper lobectomy via VATS (minimally invasive)",
                    "Targeted therapy — EGFR/ALK inhibitors if mutation positive",
                    "Stereotactic body radiation (SBRT) if surgery not feasible",
                    "Adjuvant chemotherapy if lymph nodes involved post-surgery",
                    "Immunotherapy assessment with PD-L1 expression testing"
                ]
            },
            "Top": {
                "location_analysis": (
                    "Tumor detected in the superior mediastinal region "
                    "near the trachea and great vessels. This central-"
                    "upper location requires careful evaluation for "
                    "potential airway compromise and vascular involvement."
                ),
                "symptoms": [
                    "Persistent cough with occasional blood-tinged sputum",
                    "Difficulty swallowing or sensation of chest pressure",
                    "Facial or neck swelling (possible SVC compression)",
                    "Hoarseness or voice changes due to nerve proximity",
                    "Shortness of breath worsening when lying flat",
                    "Recurrent upper respiratory tract infections",
                    "Dull ache behind the breastbone",
                    "Visible swelling in the neck or upper chest veins"
                ],
                "next_steps": [
                    "Urgent bronchoscopy to assess airway involvement",
                    "CT angiography to evaluate vascular proximity",
                    "Mediastinoscopy for lymph node staging",
                    "Pulmonary function tests before intervention",
                    "Multidisciplinary tumor board review"
                ],
                "treatments": [
                    "Surgical resection with mediastinal lymph node dissection",
                    "Neoadjuvant chemotherapy to shrink tumor before surgery",
                    "Concurrent chemoradiation if surgery not feasible",
                    "Targeted therapy based on molecular profiling results",
                    "Immunotherapy — pembrolizumab if PD-L1 ≥ 50%"
                ]
            },
            "Top Right": {
                "location_analysis": (
                    "Tumor located in the right upper lobe apical "
                    "segment. This is the most common site for lung "
                    "cancer. The right upper lobe offers good surgical "
                    "access and early-stage tumors here respond well "
                    "to lobectomy."
                ),
                "symptoms": [
                    "Persistent cough not responding to standard treatment",
                    "Right-sided chest pain or tightness in upper area",
                    "Unexplained weight loss over recent weeks",
                    "Recurrent upper respiratory infections",
                    "Mild hemoptysis (blood-streaked sputum)",
                    "Shoulder blade pain on the right side",
                    "General malaise and reduced exercise tolerance",
                    "Swollen lymph nodes in the neck area"
                ],
                "next_steps": [
                    "CT-guided percutaneous biopsy of right upper lobe",
                    "PET-CT scan for complete staging workup",
                    "Pulmonary function tests for surgical assessment",
                    "Blood work including tumor markers (CEA, CYFRA 21-1)",
                    "Referral to thoracic surgeon for evaluation"
                ],
                "treatments": [
                    "Right upper lobectomy (standard approach for Stage I)",
                    "VATS (video-assisted thoracoscopic surgery)",
                    "Stereotactic ablative radiotherapy if medically inoperable",
                    "Adjuvant targeted therapy based on mutation analysis",
                    "Post-surgical monitoring with 3-month CT follow-up"
                ]
            },
            "Left": {
                "location_analysis": (
                    "Tumor detected in the left hilar region near the "
                    "left main bronchus and pulmonary artery. This "
                    "central location may cause bronchial obstruction "
                    "and requires assessment of vascular involvement."
                ),
                "symptoms": [
                    "Persistent wheezing localized to the left lung",
                    "Progressive shortness of breath on exertion",
                    "Left-sided chest pain with deep breathing",
                    "Recurrent left lung pneumonia or atelectasis",
                    "Productive cough with mucoid sputum",
                    "Audible stridor during inspiration",
                    "Left arm swelling if vascular compression occurs",
                    "Fatigue with decreased physical stamina"
                ],
                "next_steps": [
                    "Bronchoscopy with endobronchial biopsy",
                    "CT pulmonary angiography to assess vessel involvement",
                    "Endobronchial ultrasound (EBUS) for nodal staging",
                    "Cardiac evaluation if pericardial involvement suspected",
                    "Pulmonary function tests including split lung function"
                ],
                "treatments": [
                    "Left pneumonectomy if central bronchial involvement",
                    "Sleeve lobectomy to preserve lung tissue where possible",
                    "Definitive chemoradiation if surgically unresectable",
                    "Bronchoscopic laser therapy for airway obstruction relief",
                    "Targeted molecular therapy — EGFR/ALK/ROS1 testing"
                ]
            },
            "Right": {
                "location_analysis": (
                    "Tumor identified in the right hilar region near "
                    "the right main bronchus and middle lobe bronchus. "
                    "Proximity to the carina and pulmonary vessels "
                    "requires precise staging before treatment."
                ),
                "symptoms": [
                    "Chronic cough with gradual worsening",
                    "Right-sided chest heaviness or pressure",
                    "Recurrent right middle lobe collapse or pneumonia",
                    "Mild dyspnea on exertion progressing over time",
                    "Occasional hemoptysis (blood in sputum)",
                    "Right chest wall tenderness on palpation",
                    "Appetite loss with unintended weight reduction",
                    "Intermittent low-grade fever"
                ],
                "next_steps": [
                    "Flexible bronchoscopy with brushings and lavage",
                    "EBUS-TBNA for mediastinal lymph node sampling",
                    "PET-CT for metabolic staging assessment",
                    "Pulmonary function tests with diffusion capacity",
                    "Thoracic surgery consultation for resectability"
                ],
                "treatments": [
                    "Right middle or lower lobectomy depending on extent",
                    "Bilobectomy if middle and lower lobes both involved",
                    "Neoadjuvant chemo followed by surgical resection",
                    "Immunotherapy — atezolizumab or durvalumab",
                    "Post-operative radiation if positive surgical margins"
                ]
            },
            "Bottom Left": {
                "location_analysis": (
                    "Tumor located in the left lower lobe basal segment "
                    "near the diaphragm and descending aorta. Lower "
                    "lobe tumors may cause pleural effusion and require "
                    "assessment of diaphragmatic involvement."
                ),
                "symptoms": [
                    "Left lower chest pain worsening with breathing",
                    "Progressive breathlessness especially when active",
                    "Left-sided pleural effusion causing reduced breath sounds",
                    "Persistent low-grade fever and night sweats",
                    "Loss of appetite and unexplained weight loss",
                    "Dull ache radiating to the left flank area",
                    "Dry cough that intensifies when lying on the left side",
                    "General lethargy and declining physical performance"
                ],
                "next_steps": [
                    "Thoracentesis if pleural effusion — send for cytology",
                    "CT-guided biopsy of left lower lobe mass",
                    "PET-CT to assess diaphragmatic and pleural involvement",
                    "Echocardiogram to rule out pericardial involvement",
                    "Surgical consultation for left lower lobectomy planning"
                ],
                "treatments": [
                    "Left lower lobectomy with systematic nodal dissection",
                    "VATS lobectomy if early stage and no chest wall invasion",
                    "Pleurodesis if recurrent malignant pleural effusion",
                    "Adjuvant chemotherapy — cisplatin-based regimen",
                    "Targeted therapy if actionable mutations identified"
                ]
            },
            "Bottom": {
                "location_analysis": (
                    "Tumor detected in the inferior mediastinal/subcarinal "
                    "area near the esophagus, heart, and diaphragm. "
                    "This central-lower location may affect swallowing, "
                    "cardiac function, and requires multi-organ assessment."
                ),
                "symptoms": [
                    "Difficulty swallowing (dysphagia) or painful swallowing",
                    "Central chest pain or pericardial discomfort",
                    "Worsening shortness of breath especially when supine",
                    "Persistent hiccups due to phrenic nerve irritation",
                    "Unexplained fatigue and exercise intolerance",
                    "Acid reflux-like symptoms unresponsive to medication",
                    "Heart palpitations or irregular heartbeat sensation",
                    "Steady unintentional weight decline over weeks"
                ],
                "next_steps": [
                    "EUS (endoscopic ultrasound) for subcarinal assessment",
                    "Cardiac MRI if pericardial involvement suspected",
                    "Barium swallow to evaluate esophageal compression",
                    "PET-CT for comprehensive mediastinal staging",
                    "Multidisciplinary team discussion for treatment planning"
                ],
                "treatments": [
                    "Surgical resection if feasible with clear margins",
                    "Definitive chemoradiation for unresectable disease",
                    "Pericardial window if symptomatic pericardial effusion",
                    "Targeted therapy guided by comprehensive genomic profiling",
                    "Immunotherapy combined with chemotherapy"
                ]
            },
            "Bottom Right": {
                "location_analysis": (
                    "Tumor located in the right lower lobe basal segment "
                    "near the liver dome and inferior vena cava. This "
                    "location requires evaluation for potential "
                    "diaphragmatic invasion and hepatic metastasis."
                ),
                "symptoms": [
                    "Right lower chest pain aggravated by coughing",
                    "Referred pain to right shoulder (diaphragmatic irritation)",
                    "Right-sided pleural effusion with reduced breathing",
                    "Persistent cough productive with clear to yellow sputum",
                    "Gradual weight loss and decreased appetite",
                    "Right upper abdominal fullness or tenderness",
                    "Shallow breathing due to diaphragm discomfort",
                    "Episodes of sharp pain during coughing or sneezing"
                ],
                "next_steps": [
                    "CT-guided biopsy of right lower lobe lesion",
                    "Abdominal CT to rule out liver dome invasion",
                    "PET-CT for staging and distant metastasis check",
                    "Pulmonary function tests including gas exchange",
                    "Hepatobiliary consultation if liver involvement suspected"
                ],
                "treatments": [
                    "Right lower lobectomy with diaphragmatic assessment",
                    "VATS approach if no chest wall or diaphragm invasion",
                    "Systemic chemotherapy — carboplatin + pemetrexed",
                    "Stereotactic radiation if patient is high surgical risk",
                    "Molecular testing for EGFR, ALK, ROS1, BRAF mutations"
                ]
            }
        }
    },

    # ══════════════════════════════════════════════════════════
    # SQUAMOUS CELL — Stage II — HIGH RISK
    # ══════════════════════════════════════════════════════════
    "Squamous Cell": {
        "stage": "Stage II",
        "risk": "HIGH RISK",
        "risk_color": "#FF4444",
        "description": (
            "Squamous Cell Carcinoma accounts for ~25-30% of lung "
            "cancers, strongly associated with smoking. Stage II "
            "indicates regional involvement requiring combined "
            "treatment approaches."
        ),
        "locations": {
            "Top Left": {
                "location_analysis": (
                    "Squamous cell lesion in the left upper lobe with "
                    "possible hilar lymph node involvement. Left upper "
                    "lobe squamous tumors may invade the chest wall or "
                    "subclavian vessels in advanced cases. Regional "
                    "staging is critical."
                ),
                "symptoms": [
                    "Chronic productive cough with thick mucus",
                    "Left upper chest wall pain and shoulder discomfort",
                    "Hemoptysis — coughing up blood-stained sputum",
                    "Recurrent left upper lobe pneumonia",
                    "Hoarseness due to recurrent laryngeal nerve compression",
                    "Swelling in the left supraclavicular region",
                    "Persistent left-sided pleuritic chest pain",
                    "Wheezing audible during forced exhalation"
                ],
                "next_steps": [
                    "Bronchoscopy with biopsy for histological confirmation",
                    "CT chest with contrast for mediastinal staging",
                    "EBUS for hilar and mediastinal lymph node assessment",
                    "PET-CT to evaluate regional and distant spread",
                    "Pulmonary rehabilitation before potential surgery"
                ],
                "treatments": [
                    "Left upper lobectomy with mediastinal lymph node dissection",
                    "Neoadjuvant chemoradiation followed by surgical assessment",
                    "Concurrent cisplatin-based chemotherapy with radiation",
                    "Immunotherapy — nivolumab or pembrolizumab post-chemo",
                    "Palliative radiation for symptomatic relief if advanced"
                ]
            },
            "Top": {
                "location_analysis": (
                    "Squamous tumor in the superior mediastinum near "
                    "the trachea. Central squamous cell carcinoma "
                    "classically arises from proximal bronchi. High risk "
                    "of airway obstruction and SVC syndrome."
                ),
                "symptoms": [
                    "Severe persistent cough with bloody sputum",
                    "Stridor or audible wheezing from airway narrowing",
                    "Facial and neck swelling (SVC obstruction signs)",
                    "Dyspnea worsening rapidly over days to weeks",
                    "Difficulty swallowing solid foods",
                    "Distended neck veins visible at rest",
                    "Morning headaches from venous congestion",
                    "Cyanotic discoloration of lips and fingertips"
                ],
                "next_steps": [
                    "Urgent rigid bronchoscopy for airway assessment and stenting",
                    "CT angiography to evaluate SVC patency",
                    "Mediastinoscopy with biopsy of paratracheal nodes",
                    "Urgent oncology referral — same week appointment",
                    "Venography if SVC syndrome clinically suspected"
                ],
                "treatments": [
                    "Emergent airway stenting if critical obstruction present",
                    "Concurrent chemoradiation — standard of care for Stage II",
                    "SVC stenting if symptomatic venous obstruction",
                    "Photodynamic therapy for endobronchial tumor debulking",
                    "Consolidation immunotherapy after chemoradiation"
                ]
            },
            "Top Right": {
                "location_analysis": (
                    "Squamous cell carcinoma in the right upper lobe "
                    "with potential extension to hilar lymph nodes. "
                    "Right upper lobe is the most common site for "
                    "squamous cell tumors. Assessment of azygos vein "
                    "and superior mediastinal nodes important."
                ),
                "symptoms": [
                    "Chronic cough not responding to antibiotics",
                    "Right upper chest pain worsening over time",
                    "Hemoptysis — recurrent episodes of bloody sputum",
                    "Unintentional weight loss exceeding 5% body weight",
                    "Clubbing of fingers (paraneoplastic sign)",
                    "Persistent right shoulder blade pain",
                    "Fever of unknown origin with elevated ESR",
                    "Decreased stamina during routine physical activities"
                ],
                "next_steps": [
                    "Bronchoscopy with brushing and biopsy of right upper lobe",
                    "PET-CT for complete staging workup",
                    "EBUS-TBNA for station 4R and 7 lymph node sampling",
                    "Pulmonary function tests — FEV1 and DLCO critical",
                    "Cardiopulmonary exercise testing before major surgery"
                ],
                "treatments": [
                    "Right upper lobectomy with systematic nodal dissection",
                    "Neoadjuvant chemotherapy — cisplatin/gemcitabine × 3 cycles",
                    "Adjuvant radiation if N1 nodes positive post-surgery",
                    "Pembrolizumab maintenance if PD-L1 TPS ≥ 1%",
                    "Surveillance CT every 3 months for 2 years post-treatment"
                ]
            },
            "Left": {
                "location_analysis": (
                    "Squamous lesion at the left hilum near the left "
                    "main bronchus. Classic location for squamous cell "
                    "carcinoma. Risk of left main bronchus obstruction "
                    "and left lung collapse. Bronchoscopy is essential."
                ),
                "symptoms": [
                    "Persistent wheezing and stridor on the left side",
                    "Post-obstructive pneumonia with fever and cough",
                    "Progressive dyspnea with left lung auscultation changes",
                    "Hemoptysis — moderate volume blood in sputum",
                    "Chest tightness and left-sided pleuritic pain",
                    "Left lung reduced breath sounds on examination",
                    "Productive cough with foul-smelling purulent sputum",
                    "Recurrent febrile episodes not responding to antibiotics"
                ],
                "next_steps": [
                    "Urgent bronchoscopy — direct endobronchial assessment",
                    "EBUS for hilar and subcarinal lymph node staging",
                    "CT-guided biopsy if not accessible bronchoscopically",
                    "Quantitative lung perfusion scan for surgical planning",
                    "Thoracic surgeon assessment for resectability"
                ],
                "treatments": [
                    "Left pneumonectomy if main bronchus involvement confirmed",
                    "Sleeve resection to preserve lung parenchyma if feasible",
                    "Definitive chemoradiation — 60 Gy with concurrent cisplatin",
                    "Endobronchial laser or cryotherapy for airway debulking",
                    "Immunotherapy consolidation — durvalumab for 12 months"
                ]
            },
            "Right": {
                "location_analysis": (
                    "Squamous tumor at the right hilum involving the "
                    "bronchus intermedius area. This location may cause "
                    "right middle and lower lobe atelectasis. Proximity "
                    "to the pulmonary artery trunk requires vascular "
                    "assessment."
                ),
                "symptoms": [
                    "Chronic productive cough with purulent sputum",
                    "Recurrent right-sided pneumonia (post-obstructive)",
                    "Right-sided chest pain — dull and constant",
                    "Progressive breathlessness over weeks",
                    "Hemoptysis with increasing frequency",
                    "Reduced air entry on the right side",
                    "Fatigue disproportionate to activity level",
                    "Unintentional loss of body weight over months"
                ],
                "next_steps": [
                    "Bronchoscopy with biopsy of bronchus intermedius lesion",
                    "CT pulmonary angiography for vascular involvement",
                    "EBUS for subcarinal and right hilar node assessment",
                    "PET-CT scan for systemic staging",
                    "Cardiopulmonary assessment for potential pneumonectomy"
                ],
                "treatments": [
                    "Right bilobectomy (middle + lower) if intermedius involved",
                    "Sleeve right lower lobectomy if technically feasible",
                    "Concurrent chemoradiation if surgery is contraindicated",
                    "Bronchoscopic interventions for airway palliation",
                    "Immunotherapy — nivolumab + ipilimumab combination"
                ]
            },
            "Bottom Left": {
                "location_analysis": (
                    "Squamous cell carcinoma in the left lower lobe "
                    "with proximity to the descending aorta and "
                    "diaphragm. Less common location for squamous "
                    "histology. Requires evaluation of pleural and "
                    "vascular margins."
                ),
                "symptoms": [
                    "Left lower chest pain aggravated by deep breathing",
                    "Persistent dry cough progressing to productive",
                    "Left-sided pleural effusion causing breathlessness",
                    "Low-grade fever and night sweats",
                    "Fatigue and declining exercise tolerance",
                    "Pain radiating to the left back and flank",
                    "Reduced left lung expansion on physical examination",
                    "Anorexia and early satiety"
                ],
                "next_steps": [
                    "CT-guided core biopsy of left lower lobe mass",
                    "Thoracentesis if pleural effusion — cytology analysis",
                    "PET-CT for staging and pleural involvement assessment",
                    "Aortic CT angiography if vascular proximity concerning",
                    "Surgical oncology consultation for lobectomy planning"
                ],
                "treatments": [
                    "Left lower lobectomy with thoracotomy approach",
                    "VATS lobectomy if no chest wall or aortic involvement",
                    "Neoadjuvant cisplatin-gemcitabine before surgical resection",
                    "Pleural drainage and pleurodesis if effusion recurs",
                    "Adjuvant immunotherapy — atezolizumab based on PD-L1"
                ]
            },
            "Bottom": {
                "location_analysis": (
                    "Squamous lesion in the subcarinal/inferior "
                    "mediastinal region. Proximity to the esophagus, "
                    "carina, and pericardium. This location complicates "
                    "surgical approach and may require esophageal "
                    "assessment."
                ),
                "symptoms": [
                    "Dysphagia — difficulty swallowing larger food items",
                    "Central chest pain behind the sternum",
                    "Persistent cough triggered by eating or drinking",
                    "Worsening dyspnea especially in recumbent position",
                    "Unexplained weight loss and reduced oral intake",
                    "Retrosternal burning sensation mimicking heartburn",
                    "Regurgitation of food suggesting esophageal compression",
                    "Hiccups lasting hours due to diaphragm irritation"
                ],
                "next_steps": [
                    "EUS-FNA for subcarinal mass biopsy",
                    "Barium swallow to evaluate esophageal involvement",
                    "PET-CT with mediastinal protocol for staging",
                    "Cardiac assessment — echocardiogram if pericardium near",
                    "Thoracic MDT discussion for treatment consensus"
                ],
                "treatments": [
                    "Definitive chemoradiation — primary treatment here",
                    "Surgical resection only if R0 resection is achievable",
                    "Esophageal stenting if extrinsic compression present",
                    "Immunotherapy consolidation post-chemoradiation",
                    "Palliative interventions for symptom management"
                ]
            },
            "Bottom Right": {
                "location_analysis": (
                    "Squamous cell carcinoma in the right lower lobe "
                    "basal segments with potential diaphragmatic "
                    "involvement. Proximity to the IVC and right "
                    "hepatic area requires abdominal staging."
                ),
                "symptoms": [
                    "Right lower chest and upper abdominal pain",
                    "Referred pain to right shoulder tip (Kehr's sign)",
                    "Productive cough with occasional hemoptysis",
                    "Right-sided pleural effusion with dullness on percussion",
                    "Rapid onset breathlessness and reduced exercise capacity",
                    "Right upper quadrant tenderness on palpation",
                    "Nocturnal cough disrupting sleep quality",
                    "Visible asymmetry in chest wall movement"
                ],
                "next_steps": [
                    "CT-guided biopsy of right lower lobe mass",
                    "Abdominal CT/MRI to rule out hepatic and adrenal mets",
                    "PET-CT with full-body staging protocol",
                    "Thoracentesis with pleural fluid cytology if effusion",
                    "Diaphragm assessment via ultrasound or fluoroscopy"
                ],
                "treatments": [
                    "Right lower lobectomy with diaphragm repair if invaded",
                    "Neoadjuvant chemoradiation followed by surgical reassessment",
                    "Systemic chemotherapy — cisplatin/gemcitabine protocol",
                    "Intercostal nerve block for refractory chest wall pain",
                    "Post-treatment surveillance — CT every 3 months"
                ]
            }
        }
    },

    # ══════════════════════════════════════════════════════════
    # LARGE CELL — Stage III–IV — VERY HIGH RISK
    # ══════════════════════════════════════════════════════════
    "Large Cell": {
        "stage": "Stage III–IV",
        "risk": "VERY HIGH RISK",
        "risk_color": "#CC0000",
        "description": (
            "Large Cell Carcinoma is aggressive and fast-growing "
            "(~10-15% of cases), requiring urgent multi-modal "
            "treatment. Stage III–IV indicates advanced disease "
            "with likely systemic involvement."
        ),
        "locations": {
            "Top Left": {
                "location_analysis": (
                    "Aggressive large cell carcinoma in the left upper "
                    "lobe with high metastatic potential. Superior "
                    "sulcus involvement may cause Pancoast syndrome. "
                    "Rapid growth demands urgent staging and treatment."
                ),
                "symptoms": [
                    "Severe left shoulder and arm pain (Pancoast syndrome)",
                    "Rapid onset of persistent cough and hemoptysis",
                    "Horner's syndrome — drooping eyelid, constricted pupil",
                    "Significant weight loss exceeding 10% body weight",
                    "Bone pain suggesting skeletal metastasis",
                    "Left hand weakness and muscle wasting",
                    "Severe night sweats soaking through bedding",
                    "Overwhelming fatigue limiting all daily activities"
                ],
                "next_steps": [
                    "URGENT — full body PET-CT scan within 48 hours",
                    "Brain MRI with contrast to rule out cerebral metastasis",
                    "CT-guided core biopsy with molecular profiling request",
                    "Bone scan if skeletal pain or elevated alkaline phosphatase",
                    "Emergency tumor board review within one week"
                ],
                "treatments": [
                    "Systemic combination chemotherapy — carboplatin + etoposide",
                    "Immunotherapy — pembrolizumab + chemotherapy first-line",
                    "Palliative radiation to Pancoast tumor for pain relief",
                    "Clinical trial enrollment strongly recommended",
                    "Comprehensive pain management and supportive care team"
                ]
            },
            "Top": {
                "location_analysis": (
                    "Large cell carcinoma in the superior mediastinum "
                    "with risk of tracheal and vascular compression. "
                    "This aggressive tumor may cause life-threatening "
                    "airway and vascular compromise requiring emergent "
                    "intervention."
                ),
                "symptoms": [
                    "Severe dyspnea — rapidly worsening airway compromise",
                    "Facial and upper body swelling (SVC syndrome)",
                    "Stridor and inability to lie flat",
                    "Severe headache and visual disturbances",
                    "Rapid deterioration of overall health status",
                    "Upper extremity edema bilateral",
                    "Confusion and drowsiness from cerebral edema",
                    "Chest pain radiating to the back and neck"
                ],
                "next_steps": [
                    "EMERGENCY — airway assessment and SVC evaluation",
                    "CT angiography of chest STAT for vascular compromise",
                    "Emergent tissue biopsy for rapid histology and typing",
                    "Brain MRI — high risk of CNS metastasis",
                    "ICU standby if airway compromise is critical"
                ],
                "treatments": [
                    "Emergency SVC stenting if clinically obstructed",
                    "Urgent palliative radiation to mediastinal mass",
                    "Systemic immunochemotherapy — first-line combination",
                    "Endobronchial stenting if tracheal compression present",
                    "Palliative care consultation for symptom-focused support"
                ]
            },
            "Top Right": {
                "location_analysis": (
                    "Large cell carcinoma occupying the right upper "
                    "lobe with rapid growth pattern. High risk of "
                    "superior mediastinal node involvement and SVC "
                    "compression. Likely too advanced for curative "
                    "surgery — systemic treatment priority."
                ),
                "symptoms": [
                    "Rapidly worsening cough with large-volume hemoptysis",
                    "Right upper chest pain — constant and severe",
                    "Superior vena cava syndrome signs developing",
                    "Severe fatigue limiting daily activities",
                    "Neurological symptoms — headache, confusion (brain mets)",
                    "Palpable right supraclavicular lymph nodes",
                    "Unexplained bone pain in ribs or spine",
                    "Profound appetite loss and rapid muscle wasting"
                ],
                "next_steps": [
                    "URGENT PET-CT — systemic staging within 48 hours",
                    "Brain MRI with gadolinium enhancement — mandatory",
                    "Core biopsy with comprehensive genomic profiling (CGP)",
                    "Blood work — CBC, LFT, renal function, LDH, calcium",
                    "Urgent multidisciplinary tumor board presentation"
                ],
                "treatments": [
                    "First-line immunochemotherapy — pembrolizumab + chemo",
                    "Palliative radiation for hemoptysis or pain control",
                    "Targeted therapy if driver mutation (KRAS, MET) found",
                    "Clinical trial enrollment — priority for novel agents",
                    "Early palliative care integration for quality of life"
                ]
            },
            "Left": {
                "location_analysis": (
                    "Large cell carcinoma at the left hilum causing "
                    "bronchial obstruction. Aggressive tumor with "
                    "likely mediastinal node involvement. Risk of "
                    "complete left lung collapse and respiratory "
                    "failure if untreated."
                ),
                "symptoms": [
                    "Severe progressive breathlessness — worsening daily",
                    "Complete left lung whiteout on examination (atelectasis)",
                    "Massive hemoptysis episodes requiring hospitalization",
                    "Severe cachexia — rapid muscle wasting and weight loss",
                    "Overwhelming fatigue and inability to perform daily tasks",
                    "Left lung completely silent on auscultation",
                    "Cyanosis — blue discoloration of lips and extremities",
                    "Anxiety and panic attacks from air hunger"
                ],
                "next_steps": [
                    "Emergency bronchoscopy for airway recanalization",
                    "Full body PET-CT and brain MRI for staging",
                    "Tissue biopsy with next-generation sequencing (NGS)",
                    "Respiratory support assessment — may need supplemental O2",
                    "Palliative care team involvement from diagnosis"
                ],
                "treatments": [
                    "Urgent endobronchial debulking for airway restoration",
                    "Systemic chemo — carboplatin + paclitaxel + bevacizumab",
                    "Immunotherapy — atezolizumab-based regimen",
                    "Whole brain radiation if cerebral metastases confirmed",
                    "Best supportive care with aggressive symptom management"
                ]
            },
            "Right": {
                "location_analysis": (
                    "Large cell carcinoma at the right hilum with "
                    "extensive mediastinal involvement. Tumor encasing "
                    "the right main bronchus and pulmonary vessels. "
                    "Advanced disease requiring systemic therapy."
                ),
                "symptoms": [
                    "Severe right-sided chest pain — constant and unremitting",
                    "Major hemoptysis requiring urgent medical attention",
                    "Complete right lung collapse with respiratory distress",
                    "Paraneoplastic hypercalcemia — nausea, confusion, thirst",
                    "Rapid functional decline over days to weeks",
                    "Severe bone pain if skeletal metastases present",
                    "Jaundice suggesting liver metastatic involvement",
                    "Seizures or altered consciousness if brain metastases"
                ],
                "next_steps": [
                    "Emergency CT chest and bronchoscopy for airway assessment",
                    "Complete staging — PET-CT + brain MRI + bone scan",
                    "Rapid tissue acquisition with molecular profiling",
                    "Serum calcium and PTHrP if hypercalcemia suspected",
                    "Emergency MDT meeting for treatment prioritization"
                ],
                "treatments": [
                    "Bronchoscopic intervention for critical airway stenosis",
                    "Combination immunochemotherapy — urgent initiation",
                    "Hypofractionated palliative radiation to right hilum",
                    "Bisphosphonate therapy if hypercalcemia or bone mets",
                    "Hospice and palliative care planning discussion"
                ]
            },
            "Bottom Left": {
                "location_analysis": (
                    "Large cell carcinoma in the left lower lobe with "
                    "diaphragmatic and possible pleural invasion. High "
                    "risk of malignant pleural effusion and peritoneal "
                    "spread across the diaphragm. Late-stage disease "
                    "requiring urgent systemic intervention."
                ),
                "symptoms": [
                    "Severe left lower chest and upper abdominal pain",
                    "Massive pleural effusion causing respiratory failure risk",
                    "Rapid weight loss — more than 10 kg in recent months",
                    "Ascites if transdiaphragmatic spread has occurred",
                    "Severe night sweats and constitutional symptoms",
                    "Left shoulder pain from diaphragmatic irritation",
                    "Inability to lie flat due to fluid accumulation",
                    "Extreme weakness making walking difficult"
                ],
                "next_steps": [
                    "Urgent therapeutic thoracentesis for symptom relief",
                    "Pleural fluid cytology and molecular testing",
                    "Full staging — PET-CT, brain MRI, abdominal CT",
                    "Tissue biopsy with PD-L1 and comprehensive genomic profiling",
                    "Nutritional assessment — consider enteral supplementation"
                ],
                "treatments": [
                    "Indwelling pleural catheter for recurrent effusion",
                    "Systemic immunochemotherapy — urgent start within 1 week",
                    "Talc pleurodesis for definitive pleural management",
                    "Targeted therapy if KRAS G12C, MET, or RET mutation found",
                    "Comprehensive palliative care for pain and symptom control"
                ]
            },
            "Bottom": {
                "location_analysis": (
                    "Large cell carcinoma in the inferior mediastinum "
                    "involving the esophagus and pericardium. High "
                    "risk of cardiac tamponade and esophageal "
                    "obstruction. Life-threatening complications may "
                    "require emergent intervention."
                ),
                "symptoms": [
                    "Complete dysphagia — inability to swallow liquids or solids",
                    "Pericardial effusion causing cardiac tamponade symptoms",
                    "Severe central chest pain radiating to the back",
                    "Syncope or presyncope from cardiac compromise",
                    "Extreme cachexia and rapid overall health decline",
                    "Cardiac arrhythmias from pericardial invasion",
                    "Aspiration pneumonia from esophageal obstruction",
                    "Severe dehydration from inability to swallow fluids"
                ],
                "next_steps": [
                    "EMERGENCY echocardiogram — rule out cardiac tamponade",
                    "Emergent pericardiocentesis if tamponade confirmed",
                    "Upper GI endoscopy for esophageal assessment",
                    "Rapid tissue diagnosis with full molecular workup",
                    "Immediate palliative care and oncology co-management"
                ],
                "treatments": [
                    "Pericardial window if symptomatic pericardial effusion",
                    "Esophageal stenting for malignant dysphagia",
                    "Systemic therapy — doublet chemotherapy + immunotherapy",
                    "Palliative radiation to mediastinal mass",
                    "Total parenteral nutrition if oral intake not possible"
                ]
            },
            "Bottom Right": {
                "location_analysis": (
                    "Large cell carcinoma in the right lower lobe "
                    "with liver dome invasion risk. Transdiaphragmatic "
                    "extension to the liver and adrenal gland must be "
                    "evaluated. Advanced presentation requiring urgent "
                    "systemic therapy."
                ),
                "symptoms": [
                    "Severe right lower chest and right upper abdominal pain",
                    "Hepatomegaly palpable if liver metastasis present",
                    "Jaundice if biliary obstruction from liver involvement",
                    "Massive right pleural effusion with respiratory distress",
                    "Adrenal insufficiency signs if bilateral adrenal mets",
                    "Ascites from peritoneal seeding",
                    "Profound anemia causing severe weakness",
                    "Dark urine and pale stools indicating hepatic compromise"
                ],
                "next_steps": [
                    "URGENT — abdominal CT/MRI for liver and adrenal staging",
                    "Full body PET-CT + brain MRI with contrast",
                    "Liver biopsy if hepatic lesions identified",
                    "Adrenal function tests — cortisol and ACTH levels",
                    "Emergency oncology admission for treatment initiation"
                ],
                "treatments": [
                    "Systemic immunochemotherapy — start within 48-72 hours",
                    "Liver-directed therapy if limited hepatic metastasis",
                    "Pleural drainage with indwelling catheter placement",
                    "Stereotactic radiation to oligometastatic sites",
                    "Aggressive supportive care — pain, nutrition, psychology"
                ]
            }
        }
    },

    # ══════════════════════════════════════════════════════════
    # NORMAL — No Cancer — LOW RISK
    # ══════════════════════════════════════════════════════════
    "Normal": {
        "stage": "N/A",
        "risk": "LOW",
        "risk_color": "#00AA44",
        "description": (
            "No malignant features detected. Lung tissue appears "
            "within normal parameters. No suspicious regions "
            "identified by the AI analysis."
        ),
        "locations": {}  # Not used for Normal
    }
}


# ── Default data for Normal scans (no location needed) ───────
NORMAL_DATA = {
    "location_analysis": (
        "No suspicious regions detected in the CT scan. Lung "
        "parenchyma appears clear with no areas of abnormal "
        "enhancement. No malignant features identified."
    ),
    "symptoms": [
        "No cancer-related symptoms detected",
        "Routine monitoring recommended",
        "Maintain healthy lifestyle habits",
        "Avoid smoking and passive smoke exposure",
        "Report any new respiratory symptoms promptly"
    ],
    "next_steps": [
        "Continue routine annual chest CT screening",
        "Maintain regular health checkups",
        "Pulmonologist review if symptoms develop",
        "Smoking cessation program if applicable",
        "No urgent intervention required"
    ],
    "treatments": [
        "No treatment required at this time",
        "Preventive lifestyle measures recommended",
        "Annual low-dose CT screening if high-risk",
        "Influenza and pneumonia vaccination",
        "Regular respiratory health monitoring"
    ]
}


# ══════════════════════════════════════════════════════════════
# BINARY MALIGNANT — Location-Specific Clinical Data
# Used when the binary model detects Malignant
# ══════════════════════════════════════════════════════════════
BINARY_MALIGNANT_DATA = {
    "Top Left": {
        "location_analysis": (
            "Malignant activity detected in the left upper lobe "
            "apical region. The nodule shows suspicious density "
            "patterns near the subclavian vessels. Further "
            "high-resolution CT with thin-slice protocol is "
            "recommended to characterize the lesion morphology "
            "and assess potential invasion."
        ),
        "symptoms": [
            "Left shoulder and upper arm pain radiating downward",
            "Persistent dry cough worsening over weeks",
            "Mild chest discomfort localized to upper left area",
            "Unexplained fatigue and general weakness",
            "Occasional shortness of breath during exertion",
            "Tingling or numbness in the left arm (nerve involvement)",
            "Mild hoarseness or voice changes",
            "Night sweats and low-grade intermittent fever"
        ],
        "next_steps": [
            "High-resolution CT scan with contrast for detailed nodule characterization",
            "CT-guided biopsy of left upper lobe lesion",
            "PET scan to assess metabolic activity and rule out metastasis",
            "Pulmonary function tests to assess surgical candidacy",
            "Oncology consultation for further evaluation"
        ],
        "treatments": [
            "Surgical resection (lobectomy) if confirmed invasive",
            "Stereotactic body radiation (SBRT) if surgery not feasible",
            "Active surveillance with serial CT if indeterminate",
            "Targeted therapy if molecular markers are positive",
            "Immunotherapy assessment with PD-L1 expression testing"
        ]
    },
    "Top": {
        "location_analysis": (
            "Malignant activity detected in the superior mediastinal "
            "region near the trachea and great vessels. This central-"
            "upper location requires careful evaluation for airway "
            "compromise and vascular involvement. A dedicated "
            "mediastinal protocol CT is strongly recommended."
        ),
        "symptoms": [
            "Persistent cough with occasional blood-tinged sputum",
            "Difficulty swallowing or sensation of chest pressure",
            "Facial or neck swelling (possible SVC compression)",
            "Hoarseness or voice changes due to nerve proximity",
            "Shortness of breath worsening when lying flat",
            "Recurrent upper respiratory tract infections",
            "Dull ache behind the breastbone",
            "Visible swelling in the neck or upper chest veins"
        ],
        "next_steps": [
            "Urgent high-resolution CT with mediastinal protocol",
            "Bronchoscopy to assess airway involvement",
            "CT angiography to evaluate vascular proximity",
            "Mediastinoscopy for lymph node staging",
            "Multidisciplinary tumor board review"
        ],
        "treatments": [
            "Surgical resection with mediastinal lymph node dissection",
            "Neoadjuvant chemotherapy to shrink tumor before surgery",
            "Concurrent chemoradiation if surgery not feasible",
            "Targeted therapy based on molecular profiling results",
            "Immunotherapy — pembrolizumab if PD-L1 ≥ 50%"
        ]
    },
    "Top Right": {
        "location_analysis": (
            "Malignant activity detected in the right upper lobe "
            "apical segment — the most common site for lung "
            "malignancies. The nodule requires detailed "
            "characterization with thin-slice CT to assess "
            "margins, spiculation, and potential pleural involvement."
        ),
        "symptoms": [
            "Persistent cough not responding to standard treatment",
            "Right-sided chest pain or tightness in upper area",
            "Unexplained weight loss over recent weeks",
            "Recurrent upper respiratory infections",
            "Mild hemoptysis (blood-streaked sputum)",
            "Shoulder blade pain on the right side",
            "General malaise and reduced exercise tolerance",
            "Swollen lymph nodes in the neck area"
        ],
        "next_steps": [
            "High-resolution CT with thin-slice protocol for nodule characterization",
            "CT-guided percutaneous biopsy of right upper lobe",
            "PET-CT scan for complete staging workup",
            "Blood work including tumor markers (CEA, CYFRA 21-1)",
            "Referral to thoracic surgeon for evaluation"
        ],
        "treatments": [
            "Right upper lobectomy if confirmed malignant",
            "VATS (video-assisted thoracoscopic surgery) approach",
            "Stereotactic ablative radiotherapy if medically inoperable",
            "Adjuvant targeted therapy based on mutation analysis",
            "Post-surgical monitoring with 3-month CT follow-up"
        ]
    },
    "Left": {
        "location_analysis": (
            "Malignant activity detected in the left hilar region "
            "near the left main bronchus and pulmonary artery. "
            "This central location may cause bronchial obstruction "
            "and requires detailed assessment of vascular "
            "involvement with contrast-enhanced CT."
        ),
        "symptoms": [
            "Persistent wheezing localized to the left lung",
            "Progressive shortness of breath on exertion",
            "Left-sided chest pain with deep breathing",
            "Recurrent left lung pneumonia or atelectasis",
            "Productive cough with mucoid sputum",
            "Audible stridor during inspiration",
            "Left arm swelling if vascular compression occurs",
            "Fatigue with decreased physical stamina"
        ],
        "next_steps": [
            "Contrast-enhanced CT for vascular involvement assessment",
            "Bronchoscopy with endobronchial biopsy",
            "Endobronchial ultrasound (EBUS) for nodal staging",
            "Cardiac evaluation if pericardial involvement suspected",
            "Pulmonary function tests including split lung function"
        ],
        "treatments": [
            "Surgical resection if confirmed and resectable",
            "Sleeve lobectomy to preserve lung tissue where possible",
            "Definitive chemoradiation if surgically unresectable",
            "Bronchoscopic laser therapy for airway obstruction relief",
            "Targeted molecular therapy after biopsy confirmation"
        ]
    },
    "Right": {
        "location_analysis": (
            "Malignant activity detected in the right hilar region "
            "near the right main bronchus and middle lobe bronchus. "
            "Proximity to the carina and pulmonary vessels requires "
            "precise CT staging with vascular protocol before "
            "determining treatment approach."
        ),
        "symptoms": [
            "Chronic cough with gradual worsening",
            "Right-sided chest heaviness or pressure",
            "Recurrent right middle lobe collapse or pneumonia",
            "Mild dyspnea on exertion progressing over time",
            "Occasional hemoptysis (blood in sputum)",
            "Right chest wall tenderness on palpation",
            "Appetite loss with unintended weight reduction",
            "Intermittent low-grade fever"
        ],
        "next_steps": [
            "High-resolution CT with contrast for staging",
            "Flexible bronchoscopy with brushings and lavage",
            "EBUS-TBNA for mediastinal lymph node sampling",
            "PET-CT for metabolic staging assessment",
            "Thoracic surgery consultation for resectability"
        ],
        "treatments": [
            "Lobectomy depending on extent of involvement",
            "Bilobectomy if middle and lower lobes both involved",
            "Neoadjuvant chemo followed by surgical resection",
            "Immunotherapy — atezolizumab or durvalumab",
            "Post-operative radiation if positive surgical margins"
        ]
    },
    "Bottom Left": {
        "location_analysis": (
            "Malignant activity detected in the left lower lobe "
            "basal segment near the diaphragm. Lower lobe nodules "
            "may cause pleural effusion and require assessment of "
            "diaphragmatic involvement. A closer CT scan with "
            "pleural protocol is recommended."
        ),
        "symptoms": [
            "Left lower chest pain worsening with breathing",
            "Progressive breathlessness especially when active",
            "Left-sided pleural effusion causing reduced breath sounds",
            "Persistent low-grade fever and night sweats",
            "Loss of appetite and unexplained weight loss",
            "Dull ache radiating to the left flank area",
            "Dry cough that intensifies when lying on the left side",
            "General lethargy and declining physical performance"
        ],
        "next_steps": [
            "Closer CT scan with pleural protocol for characterization",
            "Thoracentesis if pleural effusion — send for cytology",
            "CT-guided biopsy of left lower lobe mass",
            "PET-CT to assess diaphragmatic and pleural involvement",
            "Surgical consultation for lobectomy planning"
        ],
        "treatments": [
            "Left lower lobectomy with systematic nodal dissection",
            "VATS lobectomy if early stage and no chest wall invasion",
            "Pleurodesis if recurrent malignant pleural effusion",
            "Adjuvant chemotherapy — cisplatin-based regimen",
            "Targeted therapy if actionable mutations identified"
        ]
    },
    "Bottom": {
        "location_analysis": (
            "Malignant activity detected in the inferior mediastinal "
            "subcarinal area near the esophagus and diaphragm. "
            "This central-lower location may affect swallowing and "
            "cardiac function. Multi-organ assessment with dedicated "
            "CT protocol is strongly recommended."
        ),
        "symptoms": [
            "Difficulty swallowing (dysphagia) or painful swallowing",
            "Central chest pain or pericardial discomfort",
            "Worsening shortness of breath especially when supine",
            "Persistent hiccups due to phrenic nerve irritation",
            "Unexplained fatigue and exercise intolerance",
            "Acid reflux-like symptoms unresponsive to medication",
            "Heart palpitations or irregular heartbeat sensation",
            "Steady unintentional weight decline over weeks"
        ],
        "next_steps": [
            "Dedicated CT scan with multi-organ protocol",
            "EUS (endoscopic ultrasound) for subcarinal assessment",
            "Cardiac MRI if pericardial involvement suspected",
            "Barium swallow to evaluate esophageal compression",
            "Multidisciplinary team discussion for treatment planning"
        ],
        "treatments": [
            "Surgical resection if feasible with clear margins",
            "Definitive chemoradiation for unresectable disease",
            "Pericardial window if symptomatic pericardial effusion",
            "Targeted therapy guided by comprehensive genomic profiling",
            "Immunotherapy combined with chemotherapy"
        ]
    },
    "Bottom Right": {
        "location_analysis": (
            "Malignant activity detected in the right lower lobe "
            "basal segment near the liver dome and inferior vena "
            "cava. This location requires evaluation for potential "
            "diaphragmatic invasion. A closer thin-slice CT with "
            "abdominal extension is recommended."
        ),
        "symptoms": [
            "Right lower chest pain aggravated by coughing",
            "Referred pain to right shoulder (diaphragmatic irritation)",
            "Right-sided pleural effusion with reduced breathing",
            "Persistent cough productive with clear to yellow sputum",
            "Gradual weight loss and decreased appetite",
            "Right upper abdominal fullness or tenderness",
            "Shallow breathing due to diaphragm discomfort",
            "Episodes of sharp pain during coughing or sneezing"
        ],
        "next_steps": [
            "Thin-slice CT with abdominal extension for staging",
            "CT-guided biopsy of right lower lobe lesion",
            "Abdominal CT to rule out liver dome invasion",
            "PET-CT for staging and distant metastasis check",
            "Pulmonary function tests including gas exchange"
        ],
        "treatments": [
            "Right lower lobectomy with diaphragmatic assessment",
            "VATS approach if no chest wall or diaphragm invasion",
            "Systemic chemotherapy — carboplatin + pemetrexed",
            "Stereotactic radiation if patient is high surgical risk",
            "Molecular testing for EGFR, ALK, ROS1, BRAF mutations"
        ]
    }
}


def generate_clinical_notes(predicted_class, heatmap_analysis,
                              confidence):
    """
    Generate location-specific clinical notes based on:
    - predicted_class : cancer type string
    - heatmap_analysis: dict from analyze_heatmap() with location_8zone
    - confidence      : float 0-100
    Returns dict with stage, risk, location-specific clinical data
    """
    data = SUBTYPE_DATA.get(predicted_class,
                             SUBTYPE_DATA["Normal"])

    # Get 8-zone location from heatmap
    zone = heatmap_analysis.get("location_8zone", "Top Right")

    # Confidence interpretation
    if confidence >= 90:
        conf_note = "Very high confidence prediction"
    elif confidence >= 75:
        conf_note = "High confidence prediction"
    elif confidence >= 60:
        conf_note = "Moderate confidence — clinical review advised"
    else:
        conf_note = "Low confidence — biopsy strongly recommended"

    # Get location-specific data
    if predicted_class == "Normal" or not data["locations"]:
        loc_data = NORMAL_DATA
    else:
        loc_data = data["locations"].get(zone,
            list(data["locations"].values())[0])

    return {
        "class":             predicted_class,
        "stage":             data["stage"],
        "risk":              data["risk"],
        "risk_color":        data["risk_color"],
        "description":       data["description"],
        "location_analysis": loc_data["location_analysis"],
        "symptoms":          loc_data["symptoms"],
        "next_steps":        loc_data["next_steps"],
        "treatments":        loc_data["treatments"],
        "conf_note":         conf_note,
        "confidence":        round(confidence, 1),
        "zone":              zone
    }


def generate_binary_clinical_notes(heatmap_analysis, confidence):
    """
    Generate location-specific clinical notes for binary
    malignant detection based on Grad-CAM 8-zone location.
    """
    zone = heatmap_analysis.get("location_8zone", "Top Right")

    if confidence >= 90:
        conf_note = "Very high confidence prediction"
    elif confidence >= 75:
        conf_note = "High confidence prediction"
    elif confidence >= 60:
        conf_note = "Moderate confidence — clinical review advised"
    else:
        conf_note = "Low confidence — biopsy strongly recommended"

    loc_data = BINARY_MALIGNANT_DATA.get(zone,
        BINARY_MALIGNANT_DATA["Top Right"])

    # Determine stage from activation percentage
    pct = heatmap_analysis.get("activation_pct", 0)
    if pct < 10:
        stage = "Stage I"
        risk = "MODERATE RISK"
        risk_color = "#FF8C00"
    elif pct < 30:
        stage = "Stage II"
        risk = "HIGH RISK"
        risk_color = "#FF4444"
    else:
        stage = "Stage III–IV"
        risk = "VERY HIGH RISK"
        risk_color = "#CC0000"

    return {
        "class":             "Malignant",
        "stage":             stage,
        "risk":              risk,
        "risk_color":        risk_color,
        "description": (
            "The AI binary classifier has detected malignant "
            "activity in this CT scan. A closer, high-resolution "
            "CT scan is strongly recommended to characterize the "
            "lesion and confirm the diagnosis before treatment "
            "planning."
        ),
        "location_analysis": loc_data["location_analysis"],
        "symptoms":          loc_data["symptoms"],
        "next_steps":        loc_data["next_steps"],
        "treatments":        loc_data["treatments"],
        "conf_note":         conf_note,
        "confidence":        round(confidence, 1),
        "zone":              zone
    }

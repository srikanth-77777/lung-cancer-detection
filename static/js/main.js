// ── State ──────────────────────────────────────────────────
var files   = { f1:null, f2:null };
var summary = { s1:null, s2:null };
 
// ── Jump to Sector 2 ──────────────────────────────────────
function jumpToSector2() {
  document.querySelectorAll('.page').forEach(function(p){
    p.classList.remove('active');
  });
  document.querySelectorAll('.nav-item').forEach(function(n){
    n.classList.remove('active');
  });
  document.getElementById('p2').classList.add('active');
  document.querySelectorAll('.nav-item')[1].classList.add('active');
  window.scrollTo(0, 0);
}
 
// ── Navigation ─────────────────────────────────────────────
function goPage(pageId, el) {
  document.querySelectorAll('.page').forEach(function(p){ p.classList.remove('active'); });
  document.querySelectorAll('.nav-item').forEach(function(n){ n.classList.remove('active'); });
  document.getElementById(pageId).classList.add('active');
  el.classList.add('active');
  if (pageId === 'p3') renderSummary();
}
 
// ── File handling ──────────────────────────────────────────
function handleFile(input, pvId, pnId, psId, piId) {
  var file = input.files[0];
  if (!file) return;
  files[input.id] = file;
  var reader = new FileReader();
  reader.onload = function(e) {
    document.getElementById(piId).src = e.target.result;
  };
  reader.readAsDataURL(file);
  document.getElementById(pnId).textContent = file.name;
  document.getElementById(psId).textContent = (file.size/1024).toFixed(1)+' KB';
  document.getElementById(pvId).classList.add('show');
}
 
function onDrag(e, zId) {
  e.preventDefault();
  document.getElementById(zId).classList.add('dragover');
}
 
function offDrag(zId) {
  document.getElementById(zId).classList.remove('dragover');
}
 
function onDrop(e, fId, pvId, pnId, psId) {
  e.preventDefault();
  offDrag(fId === 'f1' ? 'zone1' : 'zone2');
  var file = e.dataTransfer.files[0];
  if (!file) return;
  files[fId] = file;
  var piId = fId === 'f1' ? 'pi1' : 'pi2';
  var reader = new FileReader();
  reader.onload = function(ev) {
    document.getElementById(piId).src = ev.target.result;
  };
  reader.readAsDataURL(file);
  document.getElementById(pnId).textContent = file.name;
  document.getElementById(psId).textContent = (file.size/1024).toFixed(1)+' KB';
  document.getElementById(pvId).classList.add('show');
}
 
// ── 4-class analysis (now on PAGE 1) ──────────────────────
async function runFourClass() {
  var file = files['f1'];
  if (!file) { showErr('er1','Please select a CT scan image first!'); return; }
  document.getElementById('ab1').disabled = true;
  show('ld1'); hide('rc1'); hideErr('er1');
  var fd = new FormData();
  fd.append('image', file);
  var patName = document.getElementById('pat1').value.trim();
  fd.append('patient_name', patName || 'Anonymous');
  try {
    var r = await fetch('/analyze/fourclass',{method:'POST',body:fd});
    var d = await r.json();
    if (d.error) { showErr('er1',d.error); hide('ld1'); return; }
    renderFourClass(d);
    hide('ld1'); show('rc1');
  } catch(e) {
    showErr('er1','Server error: '+e.message);
    hide('ld1');
  }
  document.getElementById('ab1').disabled = false;
}
 
function renderFourClass(d) {
  var n = d.clinical_notes;
  var p = d.probabilities;
  var isNormal = n.class === 'Normal';
 
  document.getElementById('di1').textContent = isNormal?'🟢':n.risk==='VERY HIGH RISK'?'🔴':'🟠';
  document.getElementById('dr1').textContent  = d.prediction;
  document.getElementById('dr1').style.color  = n.risk_color;
  document.getElementById('dc1').textContent  = 'Confidence: '+d.confidence+'% · '+n.conf_note;
 
  var rb1 = document.getElementById('rb1');
  rb1.textContent = n.risk;
  rb1.style.cssText = 'background:'+n.risk_color+'22;border:1px solid '+n.risk_color+
    '66;color:'+n.risk_color+';padding:7px 14px;border-radius:20px;font-size:11px;font-weight:700;font-family:monospace;';
 
  var cls = ['Adenocarcinoma','Large Cell','Normal','Squamous Cell'];
  var bh  = '';
  cls.forEach(function(c){
    var pct = p[c]||0, top = c===d.prediction;
    bh += '<div class="prob-row">'+
      '<div class="prob-lbl" style="color:'+(top?'#ff8c00':'inherit')+
      ';font-weight:'+(top?700:400)+'">'+c+'</div>'+
      '<div class="prob-track"><div class="prob-fill '+(top?'top':'')+
      '" style="width:'+pct+'%"></div></div>'+
      '<div class="prob-pct">'+pct+'%</div></div>';
  });
  document.getElementById('pb1').innerHTML = bh;
 
  document.getElementById('oi1').src = 'data:image/png;base64,'+d.original_img;
  document.getElementById('ei1').src = 'data:image/png;base64,'+d.enhanced_img;
  document.getElementById('hi1').src = 'data:image/png;base64,'+d.heatmap_img;
 
  // Remove old analysis grid
  document.getElementById('ag1').innerHTML = '';
 
  // Build clinical notes with stage banner + location data
  var notesHtml = '';
 
  // Stage + Risk banner
  if (!isNormal) {
    notesHtml +=
      '<div class="n-card full" style="text-align:center;padding:28px;">'+
        '<div class="stage-badge" style="font-size:20px;padding:10px 30px;margin-bottom:12px;">'+n.stage+'</div>'+
        '<div style="font-size:16px;font-weight:700;color:'+n.risk_color+';letter-spacing:2px;">'+n.risk+'</div>'+
        '<div style="font-size:12px;color:var(--muted);margin-top:8px;font-family:var(--mono);">'+n.description+'</div>'+
      '</div>';
  }
 
  // Location Analysis
  notesHtml +=
    '<div class="n-card full"><div class="n-title">📍 LOCATION ANALYSIS</div>'+
    '<div class="stage-note">'+n.location_analysis+'</div>'+
    (n.zone && !isNormal ? '<div style="margin-top:8px;font-size:11px;color:var(--accent);font-family:var(--mono);">Heatmap zone: '+n.zone+'</div>' : '')+
    '</div>';
 
  document.getElementById('ng1').innerHTML = notesHtml;
 
  // XAI: Explanation Narrative
  document.getElementById('xai1-narrative').innerHTML = formatExplanation(d.explanation);
 
  // Bridge: show if cancer detected (not Normal)
  if (!isNormal) {
    document.getElementById('bridge1-title').textContent =
      d.prediction + ' Confirmed — Further Analysis Recommended';
    document.getElementById('bridge1-desc').innerHTML =
      'AI confirmed <strong style="color:#ff8c00">' + d.prediction + '</strong>. ' +
      'Next recommended step is a closer <strong style="color:var(--text)">CT nodule scan</strong> ' +
      'to determine if the detected region is <strong style="color:var(--text)">malignant or benign</strong>.';
    document.getElementById('bridge1').style.display = 'block';
  } else {
    document.getElementById('bridge1').style.display = 'none';
  }

 
  document.getElementById('ds1').textContent =
    '⚠️ DISCLAIMER: AI-assisted research tool only. '+n.conf_note+
    '. Final diagnosis must be confirmed by a qualified radiologist.';
 
  summary.s1 = d;
  document.getElementById('badge1').classList.add('show');
}
 
// ── Binary analysis (now on PAGE 2) ───────────────────────
async function runBinary() {
  var file = files['f2'];
  if (!file) { showErr('er2','Please select a CT scan image first!'); return; }
  document.getElementById('ab2').disabled = true;
  show('ld2'); hide('rc2'); hideErr('er2');
  var fd = new FormData();
  fd.append('image', file);
  var patName = document.getElementById('pat2').value.trim();
  fd.append('patient_name', patName || 'Anonymous');
  try {
    var r = await fetch('/analyze/binary',{method:'POST',body:fd});
    var d = await r.json();
    if (d.error) { showErr('er2', d.error); hide('ld2'); return; }
    renderBinary(d);
    hide('ld2'); show('rc2');
  } catch(e) {
    showErr('er2','Server error: '+e.message);
    hide('ld2');
  }
  document.getElementById('ab2').disabled = false;
}
 
function renderBinary(d) {
  var m = d.is_malignant;
  var bn = document.getElementById('bn2');
  bn.className = 'diag-banner '+(m?'malignant':'benign');
  document.getElementById('di2').textContent = m ? '🔴' : '🟢';
  document.getElementById('dr2').textContent  = d.prediction;
  document.getElementById('dr2').style.color  = m ? '#ff4444' : '#00ff88';
  document.getElementById('dc2').textContent  =
    'Confidence: '+d.confidence+'% · Benign: '+d.benign_prob+'% · Malignant: '+d.malig_prob+'%';
 
  var rb = document.getElementById('rb2');
  if (m) {
    rb.textContent = '⚠ HIGH RISK';
    rb.style.cssText = 'background:rgba(255,68,68,0.2);border:1px solid rgba(255,68,68,0.5);color:#ff4444;padding:7px 14px;border-radius:20px;font-size:11px;font-weight:700;font-family:monospace;';
  } else {
    rb.textContent = '✓ LOW RISK';
    rb.style.cssText = 'background:rgba(0,255,136,0.2);border:1px solid rgba(0,255,136,0.5);color:#00ff88;padding:7px 14px;border-radius:20px;font-size:11px;font-weight:700;font-family:monospace;';
  }
 
  if (m) {
    document.getElementById('bg2').style.display = 'none';
    document.getElementById('mg2').style.display = 'block';
    document.getElementById('oi2m').src = 'data:image/png;base64,'+d.original_img;
    document.getElementById('ei2m').src = 'data:image/png;base64,'+d.enhanced_img;
    document.getElementById('hi2').src  = 'data:image/png;base64,'+d.heatmap_img;
    var a = d.cam_analysis;
    var stageMap = {'Small':'Localized Risk Profile','Medium':'Regional Risk Profile','Large':'Extensive Risk Profile'};
    var stageLabel = stageMap[a.size_label] || 'Unknown';
    document.getElementById('ag2').innerHTML =
      ac('📍 Tumor Location', a.location, (a.shape||'Nodular')+' mass · '+(a.is_central?'Central airway region':'Peripheral lung field')) +
      ac('⚖️ Clinical Risk Profile', stageLabel, a.stage_hint) +
      ac('📐 Area Coverage', a.activation_pct+'% of scan area', a.size_label+' mass — '+(a.activation_pct<10?'Localized growth':a.activation_pct<30?'Moderate spread':'Extensive spread')) +
      ac('🔴 Spread Pattern', (a.num_spots<=1?'Single Focus':'Multiple Foci ('+a.num_spots+')'), a.spread);
    document.getElementById('re2').innerHTML =
      '<strong>🩺 Malignancy Detected</strong>'+d.recommendation;

    // Clinical notes for binary (from backend)
    if (d.clinical_notes) {
      var cn = d.clinical_notes;
      var cnHtml = '';

      // Location Analysis
      cnHtml +=
        '<div class="n-card full"><div class="n-title">📍 LOCATION ANALYSIS</div>'+
        '<div class="stage-note">'+cn.location_analysis+'</div>'+
        '<div style="margin-top:8px;font-size:11px;color:var(--accent);font-family:var(--mono);">Heatmap zone: '+cn.zone+'</div>'+
        '</div>';

      // Symptoms
      cnHtml +=
        '<div class="n-card"><div class="n-title">⚠️ SYMPTOMS</div><ul>'+
        cn.symptoms.map(function(s){return '<li>'+s+'</li>';}).join('')+'</ul></div>';

      // Steps
      cnHtml +=
        '<div class="n-card"><div class="n-title">✅ STEPS TO UNDERTAKE</div><ul>'+
        cn.next_steps.map(function(s){return '<li>'+s+'</li>';}).join('')+'</ul></div>';

      // Treatments
      cnHtml +=
        '<div class="n-card full"><div class="n-title">💊 TREATMENT OPTIONS</div>'+
        '<ul style="display:grid;grid-template-columns:1fr 1fr;gap:8px">'+
        cn.treatments.map(function(s){return '<li>'+s+'</li>';}).join('')+'</ul></div>';

      document.getElementById('ng2').innerHTML = cnHtml;
    }

    // XAI: Explanation
    document.getElementById('xai2').style.display = 'block';
    document.getElementById('xai2-narrative').innerHTML = formatExplanation(d.explanation);
    // Reset LIME state
    document.getElementById('lime-result-s2').style.display = 'none';
    document.getElementById('lime-btn-s2').disabled = false;
    document.getElementById('lime-btn-s2').innerHTML = '🔬 Generate LIME Explanation (Detailed Superpixel Analysis)';
  } else {
    document.getElementById('bg2').style.display = 'block';
    document.getElementById('mg2').style.display = 'none';
    document.getElementById('oi2b').src = 'data:image/png;base64,'+d.original_img;
    document.getElementById('ei2b').src = 'data:image/png;base64,'+d.enhanced_img;
  }
 
  summary.s2 = d;
  document.getElementById('badge2').classList.add('show');
}
 
// ── Save to summary ────────────────────────────────────────
function saveToSummary(sector) {
  var btn = document.getElementById('sv'+sector);
  btn.classList.add('saved');
  btn.innerHTML = '✅ Saved to Summary Report';
  btn.disabled = true;
  document.getElementById('badge3').classList.add('show');
}
 
// ── Render summary ─────────────────────────────────────────
function renderSummary() {
  var has = summary.s1 || summary.s2;
  document.getElementById('sumEmpty').style.display   = has ? 'none'  : 'block';
  document.getElementById('sumContent').style.display = has ? 'block' : 'none';
  if (!has) return;
 
  var html = '';
 
  if (summary.s1) {
    var d = summary.s1;
    var n = d.clinical_notes;
    var isNormal = n.class === 'Normal';
    html += '<div class="sum-card">'+
      '<div class="sum-card-header s1h">'+
        '<div class="sum-num">01</div> Subtype Classification — ResNet50'+
      '</div>'+
      '<div class="sum-body">'+
        '<div class="sum-result" style="color:'+n.risk_color+'">'+d.prediction+'</div>'+
        '<div class="sum-conf">Confidence: '+d.confidence+'% · Stage: '+n.stage+'</div>'+
        '<div class="sum-img-row">'+
          '<div class="sum-img-card"><div class="sum-img-lbl">Original</div><img src="data:image/png;base64,'+d.original_img+'" alt=""/></div>'+
          '<div class="sum-img-card"><div class="sum-img-lbl">Grad-CAM</div><img src="data:image/png;base64,'+d.heatmap_img+'" alt=""/></div>'+
        '</div>'+
        '<div class="sum-tags">'+
          '<div class="sum-tag hi">'+n.stage+'</div>'+
          '<div class="sum-tag hi">📍 '+(n.zone||'N/A')+'</div>'+
          '<div class="sum-tag hi">'+n.risk+'</div>'+
          (d.cam_analysis ? '<div class="sum-tag">'+d.cam_analysis.size_label+' mass</div>' : '')+
        '</div>'+
        '<button class="btn-analyze" style="margin-top:14px;width:100%;display:flex;align-items:center;justify-content:center;gap:8px;" onclick="triggerDownload(' + d.db_id + ')">📥 Download Clinical Report</button>'+
      '</div></div>';
  } else {
    html += '<div class="sum-card"><div class="sum-body" style="text-align:center;padding:40px;color:var(--muted)">No Sector 1 result saved yet</div></div>';
  }
 
  if (summary.s2) {
    var d2 = summary.s2;
    var m2 = d2.is_malignant;
    html += '<div class="sum-card">'+
      '<div class="sum-card-header s2h">'+
        '<div class="sum-num">02</div> Binary Detection — ResNet50'+
      '</div>'+
      '<div class="sum-body">'+
        '<div class="sum-result" style="color:'+(m2?'#ff4444':'#00ff88')+'">'+d2.prediction+'</div>'+
        '<div class="sum-conf">Confidence: '+d2.confidence+'% · Benign: '+d2.benign_prob+'% · Malignant: '+d2.malig_prob+'%</div>'+
        '<div class="sum-img-row">'+
          '<div class="sum-img-card"><div class="sum-img-lbl">Original</div><img src="data:image/png;base64,'+d2.original_img+'" alt=""/></div>'+
          (m2 ? '<div class="sum-img-card"><div class="sum-img-lbl">Grad-CAM</div><img src="data:image/png;base64,'+d2.heatmap_img+'" alt=""/></div>' :
               '<div class="sum-img-card"><div class="sum-img-lbl">Enhanced</div><img src="data:image/png;base64,'+d2.enhanced_img+'" alt=""/></div>')+
        '</div>'+
        (m2 && d2.cam_analysis ? '<div class="sum-tags">'+
          '<div class="sum-tag hi">📍 '+d2.cam_analysis.location+'</div>'+
          '<div class="sum-tag hi">📏 '+d2.cam_analysis.size_label+'</div>'+
          '<div class="sum-tag hi">⚡ '+d2.cam_analysis.intensity_label+'</div>'+
          '<div class="sum-tag">'+(m2?'⚠ HIGH RISK':'✓ LOW RISK')+'</div>'+
        '</div>' : '<div class="sum-tags"><div class="sum-tag">✓ LOW RISK</div></div>')+
        '<button class="btn-analyze" style="margin-top:14px;width:100%;display:flex;align-items:center;justify-content:center;gap:8px;" onclick="triggerDownload(' + d2.db_id + ')">📥 Download Clinical Report</button>'+
      '</div></div>';
  } else {
    html += '<div class="sum-card"><div class="sum-body" style="text-align:center;padding:40px;color:var(--muted)">No Sector 2 result saved yet</div></div>';
  }
 
  document.getElementById('sumGrid').innerHTML = html;
}
 
// ── Clear summary ──────────────────────────────────────────
function clearSummary() {
  summary = { s1:null, s2:null };
  ['sv1','sv2'].forEach(function(id){
    var b = document.getElementById(id);
    b.classList.remove('saved');
    b.innerHTML = '💾 Save to Summary Report';
    b.disabled = false;
  });
  ['badge1','badge2','badge3'].forEach(function(id){
    document.getElementById(id).classList.remove('show');
  });
  renderSummary();
}
 
// ── Helpers ────────────────────────────────────────────────
function ac(lbl,val,sub,col) {
  return '<div class="a-card">'+
    '<div class="a-lbl">'+lbl+'</div>'+
    '<div class="a-val" style="color:'+(col||'#00d4ff')+'">'+val+'</div>'+
    '<div class="a-sub">'+sub+'</div></div>';
}
 
function show(id)  { document.getElementById(id).classList.add('show'); }
function hide(id)  { document.getElementById(id).classList.remove('show'); }
function showErr(id,msg) {
  var b = document.getElementById(id);
  b.textContent = '❌ '+msg;
  b.classList.add('show');
}
function hideErr(id) { document.getElementById(id).classList.remove('show'); }

// ── XAI Helpers ────────────────────────────────────────────────
function toggleXaiInfo(id) {
  document.getElementById(id).classList.toggle('show');
}

function formatExplanation(text) {
  // Convert **bold** markdown to <strong> tags
  return text.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
}


// ── LIME Analysis for Binary (Page 2) ──────────────────────────
async function runLimeBinary() {
  var file = files['f2'];
  if (!file) { showErr('er2','No image available for LIME analysis!'); return; }
  var btn = document.getElementById('lime-btn-s2');
  btn.disabled = true;
  btn.textContent = '⏳ Running LIME analysis...';
  show('ld-lime-s2');
  document.getElementById('lime-result-s2').style.display = 'none';

  var fd = new FormData();
  fd.append('image', file);
  try {
    var r = await fetch('/explain/lime-binary', {method:'POST', body:fd});
    var d = await r.json();
    hide('ld-lime-s2');
    if (d.error) {
      showErr('er2', 'LIME Error: '+d.error);
      btn.disabled = false;
      btn.textContent = '🔬 Generate LIME Explanation (Detailed Superpixel Analysis)';
      return;
    }
    document.getElementById('lime-pos-img-s2').src = 'data:image/png;base64,'+d.lime_positive;
    document.getElementById('lime-full-img-s2').src = 'data:image/png;base64,'+d.lime_mask;
    document.getElementById('lime-narrative-s2').innerHTML = formatExplanation(d.lime_narrative);
    document.getElementById('lime-result-s2').style.display = 'block';
    btn.textContent = '✅ LIME Analysis Complete';
  } catch(e) {
    hide('ld-lime-s2');
    showErr('er2', 'LIME Error: '+e.message);
    btn.disabled = false;
    btn.textContent = '🔬 Generate LIME Explanation (Detailed Superpixel Analysis)';
  }
}


// ── Chatbot ────────────────────────────────────────────────
function toggleChat() {
  document.getElementById('chatWindow').classList.toggle('show');
}

function handleChatKey(e) {
  if (e.key === 'Enter') sendChatMessage();
}

async function sendChatMessage() {
  var input = document.getElementById('chatInput');
  var text = input.value.trim();
  if (!text) return;

  var chatBody = document.getElementById('chatBody');
  
  // Add user message
  var userMsgDiv = document.createElement('div');
  userMsgDiv.className = 'chat-msg user';
  userMsgDiv.textContent = text;
  chatBody.appendChild(userMsgDiv);
  
  input.value = '';
  chatBody.scrollTop = chatBody.scrollHeight;

  // Add temp bot message
  var botMsgDiv = document.createElement('div');
  botMsgDiv.className = 'chat-msg bot';
  botMsgDiv.textContent = 'Typing...';
  chatBody.appendChild(botMsgDiv);
  chatBody.scrollTop = chatBody.scrollHeight;

  try {
    var response = await fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        message: text,
        context: { s1: summary.s1, s2: summary.s2 }
      })
    });
    var data = await response.json();
    
    // Replace text
    if (data.error) {
      botMsgDiv.style.color = '#ff4444';
      botMsgDiv.textContent = 'Error: ' + data.error;
    } else {
      botMsgDiv.textContent = data.response;
    }
  } catch (err) {
    botMsgDiv.style.color = '#ff4444';
    botMsgDiv.textContent = 'Network error. Could not reach server.';
  }
  chatBody.scrollTop = chatBody.scrollHeight;
}

// ── Trigger Report Download ─────────────────────────────────
function triggerDownload(dbId) {
  if (!dbId) {
    alert("No database ID associated with this analysis.");
    return;
  }
  window.open('/download/report/' + dbId, '_blank');
}

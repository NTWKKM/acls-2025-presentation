import re, json, math, random, subprocess, os

# Read source file
with open('cases/acls-2025-cases.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Neutral Case Titles for Exam / Questions-Only Version (Clinical Presentation Titles)
NEUTRAL_CASE_TITLES = {
    1: "Sudden Collapse in Emergency Department",
    2: "Unresponsive Patient Found at Home",
    3: "Sudden Post-operative Collapse",
    4: "Dizziness, Diaphoresis & Hypoperfusion",
    5: "Chest Tightness & Palpitations with History of IHD",
    6: "Severe Dyspnea & Acute Pulmonary Edema",
    7: "Recurrent Syncope in Patient on Diuretics",
    8: "Submersion Injury & Cardiac Arrest",
    9: "Post-Cardiac Arrest Care & Hemodynamic Support",
    10: "Post-CABG Cardiac Arrest in ICU",
    11: "Sudden Palpitations in Young Adult",
    12: "Maternal Collapse at 32 Weeks Gestation",
    13: "Collapse in End-Stage Renal Disease Patient",
    14: "Collapse in Patient with Mechanical Circulatory Support (LVAD)",
    15: "Refractory Out-of-Hospital Cardiac Arrest"
}

# ECG SVG Generator (Height 56px - Perfect balance)
def generate_ecg_svg(rhythm_type, width=650, height=56, stroke='#10b981'):
    random.seed(42)
    points = []
    mid = height / 2.0
    
    for x in range(width):
        t = x
        y = 0
        if rhythm_type == 'vf':
            y = math.sin(t*0.2)*14 + math.sin(t*0.55)*7 + math.sin(t*1.1)*4 + (random.random()-0.5)*6
        elif rhythm_type == 'asystole':
            y = (random.random()-0.5)*1.2
        elif rhythm_type == 'pea':
            mod = t % 70
            if mod < 4: y = -12
            elif mod < 8: y = 20
            else: y = (random.random()-0.5)*1.2
        elif rhythm_type == 'bradycardia':
            mod = t % 150
            if mod < 4: y = -6
            elif mod < 7: y = -14
            elif mod < 12: y = 24
            elif mod < 16: y = -5
            elif mod > 40 and mod < 60: y = -7 * math.sin((mod-40)/20*math.pi)
            else: y = (random.random()-0.5)*1.2
        elif rhythm_type == 'torsades':
            cycle = t % 160
            envelope = math.sin(cycle / 160.0 * math.pi)
            y = envelope * (math.sin(cycle * 0.35) * 18 + math.sin(cycle * 0.7) * 11) + (random.random()-0.5)*2
        elif rhythm_type == 'hyperK':
            mod = t % 65
            if mod < 4: y = -10
            elif mod < 10: y = 20
            elif mod > 20 and mod < 45: y = -18 * math.sin((mod-20)/25*math.pi)
            else: y = (random.random()-0.5)*1.2
        elif rhythm_type == 'afrvr':
            mod = (t + int(math.sin(t*0.05)*10)) % 30
            if mod < 3: y = -12
            elif mod < 6: y = 22
            else: y = (random.random()-0.5)*2
        elif rhythm_type == 'svt':
            mod = t % 28
            if mod < 3: y = -14
            elif mod < 7: y = 25
            else: y = (random.random()-0.5)*1.2
        elif rhythm_type == 'pacing':
            mod = t % 50
            if mod < 2: y = 28
            elif mod < 5: y = -20
            elif mod < 10: y = 16
            else: y = (random.random()-0.5)*1.2
        else: # nsr
            mod = t % 60
            if mod < 4: y = -5
            elif mod < 7: y = -18
            elif mod < 11: y = 25
            elif mod < 14: y = -6
            elif mod > 25 and mod < 40: y = -5 * math.sin((mod-25)/15*math.pi)
            else: y = (random.random()-0.5)*1.2
            
        points.append(f"{x},{mid - y:.2f}")
    
    path_d = "M " + " L ".join(points)
    svg = f'''<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" style="background: #090d16; border-radius: 6px; border: 1px solid #334155; margin-top: 6px; display: block;">
      <defs>
        <pattern id="grid-{rhythm_type}" width="18" height="18" patternUnits="userSpaceOnUse">
          <path d="M 18 0 L 0 0 0 18" fill="none" stroke="rgba(37,99,235,0.18)" stroke-width="0.5"/>
        </pattern>
      </defs>
      <rect width="100%" height="100%" fill="url(#grid-{rhythm_type})" />
      <path d="{path_d}" fill="none" stroke="{stroke}" stroke-width="2" stroke-linejoin="round" />
    </svg>'''
    return svg

# Neutralize explicit rhythm giveaways in scenario text
def neutralize_scenario(text):
    text = re.sub(r'มอนิเตอร์แสดงคลื่น Ventricular Fibrillation \(VF\)', 'มอนิเตอร์แสดงคลื่นไฟฟ้าหัวใจดังแถบ ECG ด้านล่าง', text)
    text = re.sub(r'พบคลื่น Asystole \(เส้นตรง\)', 'พบคลื่นไฟฟ้าหัวใจดังแสดงในแถบ ECG ด้านล่าง', text)
    text = re.sub(r'พบ Pulseless Electrical Activity \(PEA\) อัตรา 110/นาที', 'พบคลื่นไฟฟ้าหัวใจดังแสดงในแถบ ECG ด้านล่าง อัตราประมาณ 110/นาที', text)
    text = re.sub(r'มอนิเตอร์แสดง Sinus Bradycardia อัตรา 36 ครั้ง/นาที', 'มอนิเตอร์แสดงคลื่นไฟฟ้าหัวใจดังแสดงในแถบ ECG ด้านล่าง', text)
    text = re.sub(r'มอนิเตอร์แสดง Monomorphic VT', 'มอนิเตอร์แสดงคลื่นไฟฟ้าหัวใจดังแสดงในแถบ ECG ด้านล่าง', text)
    text = re.sub(r'มอนิเตอร์แสดง AF with RVR', 'มอนิเตอร์แสดงคลื่นไฟฟ้าหัวใจดังแสดงในแถบ ECG ด้านล่าง', text)
    text = re.sub(r'มอนิเตอร์แสดง Torsades de Pointes', 'มอนิเตอร์แสดงคลื่นไฟฟ้าหัวใจดังแสดงในแถบ ECG ด้านล่าง', text)
    text = re.sub(r'ติดมอนิเตอร์พบคลื่น Asystole', 'ติดมอนิเตอร์พบคลื่นไฟฟ้าหัวใจดังแสดงในแถบ ECG ด้านล่าง', text)
    text = re.sub(r'มอนิเตอร์แสดง Sinus Rhythm', 'มอนิเตอร์แสดงคลื่นไฟฟ้าหัวใจดังแสดงในแถบ ECG ด้านล่าง', text)
    text = re.sub(r'มอนิเตอร์แสดง SVT', 'มอนิเตอร์แสดงคลื่นไฟฟ้าหัวใจดังแสดงในแถบ ECG ด้านล่าง', text)
    text = re.sub(r'มอนิเตอร์แสดง PEA', 'มอนิเตอร์แสดงคลื่นไฟฟ้าหัวใจดังแสดงในแถบ ECG ด้านล่าง', text)
    text = re.sub(r'ติดมอนิเตอร์พบคลื่น Sine Wave อัตรา 45/นาที QRS กว้างมาก', 'ติดมอนิเตอร์พบคลื่นไฟฟ้าหัวใจดังแสดงในแถบ ECG ด้านล่าง', text)
    text = re.sub(r'เกิด PEA arrest', 'เกิด cardiac arrest', text)
    text = re.sub(r'มอนิเตอร์ยังคงเป็น Asystole เส้นตรง', 'มอนิเตอร์แสดงคลื่นไฟฟ้าหัวใจดังแสดงในแถบ ECG ด้านล่าง', text)
    return text

# Neutralize rhythm text in vitals
def neutralize_vitals(vitals_html):
    return re.sub(r'<li><strong>Rhythm:</strong> .*?</li>', '<li><strong>Rhythm:</strong> Refer to ECG Strip</li>', vitals_html)

# Parse slides
parts = content.split('<div class="slide"')
cases_data = {}

for part in parts[1:]:
    m = re.search(r'id="(slide-[^"]+)"', part)
    if not m: continue
    slide_id = m.group(1)
    
    cm = re.search(r'slide-case(\d+)-(intro|q\d+)', slide_id)
    if not cm: continue
    case_num = int(cm.group(1))
    slide_type = cm.group(2)
    
    if case_num not in cases_data:
        cases_data[case_num] = {'questions': []}
    
    if slide_type == 'intro':
        title_m = re.search(r'<h2>(.*?)</h2>', part, re.DOTALL)
        num_m = re.search(r'<div class="case-number">(.*?)</div>', part, re.DOTALL)
        obj_m = re.search(r'<div class="objective">(.*?)</div>', part, re.DOTALL)
        scen_m = re.search(r'<p class="scenario">(.*?)</p>', part, re.DOTALL)
        vitals_m = re.search(r'<div class="vitals">(.*?)</div>\s*<div class="ecg-strip"', part, re.DOTALL)
        rhythm_m = re.search(r'data-rhythm="([^"]+)"', part)
        color_m = re.search(r'data-ecg-color="([^"]+)"', part)
        label_m = re.search(r'<div class="ecg-label">(.*?)</div>', part)
        
        num_text = num_m.group(1).strip() if num_m else f'Case {case_num}'
        diff_tag = ''
        if 'difficulty-tag' in num_text:
            if 'core' in num_text.lower():
                diff_tag = '<span class="tag tag-core">Core</span>'
            elif 'advanced' in num_text.lower():
                diff_tag = '<span class="tag tag-advanced">Advanced</span>'
            num_text = re.sub(r'<span class="difficulty-tag[^"]*">.*?</span>', '', num_text, flags=re.DOTALL).strip()
        
        rhythm = rhythm_m.group(1) if rhythm_m else 'nsr'
        color = color_m.group(1) if color_m else '#10b981'
        label = label_m.group(1) if label_m else 'ECG LEAD II'
        
        scen_text = scen_m.group(1).strip() if scen_m else ''
        vitals_text = vitals_m.group(1).strip() if vitals_m else ''
        
        cases_data[case_num]['title'] = title_m.group(1).strip() if title_m else ''
        cases_data[case_num]['number'] = num_text
        cases_data[case_num]['diff_tag'] = diff_tag
        cases_data[case_num]['objective'] = obj_m.group(1).strip() if obj_m else ''
        cases_data[case_num]['scenario'] = scen_text
        cases_data[case_num]['scenario_neutral'] = neutralize_scenario(scen_text)
        cases_data[case_num]['vitals'] = vitals_text
        cases_data[case_num]['vitals_neutral'] = neutralize_vitals(vitals_text)
        cases_data[case_num]['rhythm'] = rhythm
        cases_data[case_num]['color'] = color
        cases_data[case_num]['label'] = label
    else:
        q_m = re.search(r'<p class="question-text">(.*?)</p>', part, re.DOTALL)
        opts = re.findall(r'<div class="option-card" data-correct="(true|false)">(.*?)</div>', part)
        exp_m = re.search(r'<div class="explanation-panel">(.*?)</div>\s*<div class="nav-buttons"', part, re.DOTALL)
        
        q_obj = {
            'id': slide_type,
            'question': q_m.group(1).strip() if q_m else '',
            'options': [{'correct': opt[0] == 'true', 'text': opt[1].strip()} for opt in opts],
            'explanation': exp_m.group(1).strip() if exp_m else ''
        }
        cases_data[case_num]['questions'].append(q_obj)

# Helper function to generate HTML document
def generate_html_doc(with_answers=True):
    subtitle_type = "Complete Handbook with Explanations & Answer Key" if with_answers else "Student Worksheet / Question Bank (Without Answers)"
    doc_title = "ACLS 2025 Case Handbook (With Answers)" if with_answers else "ACLS 2025 Case Handbook (Questions Only)"

    html_out = f"""<!DOCTYPE html>
<html lang="th">
<head>
  <meta charset="UTF-8">
  <title>{doc_title}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Sarabun:wght@400;500;600;700&family=Sora:wght@600;700&display=swap" rel="stylesheet">
  <style>
    @page {{
      size: A4;
      margin: 11mm 13mm 11mm 13mm;
      @bottom-right {{
        content: counter(page);
      }}
    }}
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    
    body {{
      font-family: 'Sarabun', 'Segoe UI', Tahoma, sans-serif;
      color: #1e293b;
      background: #ffffff;
      line-height: 1.48;
      font-size: 13.5px;
    }}

    .cover-page {{
      padding: 35px 20px;
      text-align: center;
      page-break-after: always;
      display: flex;
      flex-direction: column;
      justify-content: center;
      min-height: 90vh;
    }}

    .cover-badge {{
      display: inline-block;
      background: #eff6ff;
      color: #2563eb;
      border: 1px solid #bfdbfe;
      padding: 6px 16px;
      border-radius: 20px;
      font-weight: 700;
      font-size: 13px;
      letter-spacing: 1px;
      margin-bottom: 18px;
    }}

    .cover-title {{
      font-family: 'Sora', 'Sarabun', sans-serif;
      font-size: 34px;
      font-weight: 700;
      color: #0f1e3d;
      margin-bottom: 12px;
      line-height: 1.2;
    }}

    .cover-subtitle {{
      font-size: 17px;
      color: #64748b;
      margin-bottom: 35px;
      font-weight: 500;
    }}

    .toc-box {{
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 12px;
      padding: 22px 28px;
      text-align: left;
      max-width: 750px;
      margin: 0 auto;
    }}

    .toc-title {{
      font-size: 17px;
      font-weight: 700;
      color: #0f1e3d;
      margin-bottom: 14px;
      border-bottom: 2px solid #2563eb;
      padding-bottom: 6px;
    }}

    .toc-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px 22px;
    }}

    .toc-item {{
      font-size: 13.5px;
      color: #334155;
    }}
    .toc-item strong {{
      color: #2563eb;
    }}

    /* CASE SECTION (COMFORTABLY BALANCED 1 PAGE PER CASE) */
    .case-card {{
      page-break-after: always;
      page-break-inside: avoid;
      padding-top: 4px;
    }}

    .case-card:last-child {{
      page-break-after: avoid;
    }}

    .case-header {{
      border-bottom: 2.5px solid #2563eb;
      padding-bottom: 6px;
      margin-bottom: 8px;
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
    }}

    .case-num-title h2 {{
      font-family: 'Sora', 'Sarabun', sans-serif;
      font-size: 19px;
      color: #0f1e3d;
      font-weight: 700;
      line-height: 1.25;
    }}

    .case-num-title .c-label {{
      font-size: 11.5px;
      font-weight: 700;
      color: #2563eb;
      text-transform: uppercase;
      letter-spacing: 1px;
      margin-bottom: 2px;
    }}

    .tag {{
      display: inline-block;
      font-size: 10.5px;
      font-weight: 700;
      padding: 2.5px 9px;
      border-radius: 10px;
      text-transform: uppercase;
    }}
    .tag-core {{ background: #dbeafe; color: #1e40af; border: 1px solid #93c5fd; }}
    .tag-advanced {{ background: #fef3c7; color: #92400e; border: 1px solid #fcd34d; }}

    .objective-box {{
      background: #f0f9ff;
      border-left: 3.5px solid #0284c7;
      padding: 7px 12px;
      border-radius: 0 6px 6px 0;
      margin-bottom: 8px;
      font-size: 12.5px;
      color: #0369a1;
    }}

    .scenario-box {{
      background: #f8fafc;
      border: 1px solid #cbd5e1;
      border-radius: 8px;
      padding: 10px 14px;
      margin-bottom: 8px;
      font-size: 13.5px;
      line-height: 1.5;
      color: #0f172a;
    }}

    .ecg-container {{
      margin-top: 5px;
      position: relative;
    }}
    .ecg-strip-header {{
      font-size: 10.5px;
      font-weight: 700;
      color: #64748b;
      letter-spacing: 0.5px;
      margin-bottom: 2px;
      text-transform: uppercase;
    }}

    .vitals-box {{
      background: #fff;
      border: 1px solid #cbd5e1;
      border-radius: 6px;
      padding: 7px 14px;
      margin-bottom: 10px;
    }}
    .vitals-box h4 {{
      display: none;
    }}
    .vitals-box ul {{
      list-style: none;
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 3px 14px;
    }}
    .vitals-box li {{
      font-size: 12.5px;
      color: #334155;
    }}
    .vitals-box li strong {{ color: #0f172a; }}

    /* QUESTION ITEM */
    .question-block {{
      background: #ffffff;
      border: 1px solid #e2e8f0;
      border-radius: 8px;
      padding: 7px 12px;
      margin-bottom: 8px;
      page-break-inside: avoid;
    }}

    .q-title {{
      font-size: 13.5px;
      font-weight: 700;
      color: #0f1e3d;
      margin-bottom: 5px;
    }}

    .options-list {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 5px 12px;
      margin-bottom: 0;
    }}

    .opt-item {{
      padding: 6px 10px;
      border-radius: 5px;
      border: 1px solid #cbd5e1;
      font-size: 12.5px;
      color: #334155;
      background: #f8fafc;
      display: flex;
      align-items: center;
      gap: 7px;
    }}

    .opt-checkbox {{
      width: 13px;
      height: 13px;
      border: 1.5px solid #94a3b8;
      border-radius: 3px;
      display: inline-block;
      flex-shrink: 0;
    }}

    .opt-item.correct {{
      background: #f0fdf4;
      border-color: #22c55e;
      color: #15803d;
      font-weight: 600;
    }}
    .opt-item.correct::after {{
      content: " ✓ (Correct)";
      color: #16a34a;
      font-weight: 700;
      margin-left: auto;
    }}

    .exp-box {{
      background: #f8fafc;
      border-top: 1px solid #e2e8f0;
      padding-top: 6px;
      margin-top: 4px;
      font-size: 12px;
      color: #475569;
    }}

    .exp-box h4 {{
      font-size: 12px;
      color: #2563eb;
      margin-bottom: 2px;
    }}

    .distractor-notes {{
      margin-top: 4px;
      padding-left: 14px;
    }}
    .distractor-notes li {{
      font-size: 11.5px;
      color: #64748b;
      margin-bottom: 1px;
    }}

    .key-teaching {{
      background: #eff6ff;
      border-left: 3px solid #2563eb;
      padding: 6px 10px;
      border-radius: 0 5px 5px 0;
      margin-top: 4px;
      font-size: 11.5px;
      color: #1e40af;
    }}
    .key-teaching strong {{ display: block; font-size: 10.5px; text-transform: uppercase; color: #2563eb; }}
  </style>
</head>
<body>

  <!-- COVER PAGE -->
  <div class="cover-page">
    <div>
      <span class="cover-badge">AHA 2025 GUIDELINES COMPLIANT</span>
      <h1 class="cover-title">ACLS 2025 Interactive Case Handbook</h1>
      <p class="cover-subtitle">{subtitle_type}</p>
    </div>
    
    <div class="toc-box">
      <div class="toc-title">Table of Contents</div>
      <div class="toc-grid">
"""

    for cnum in sorted(cases_data.keys()):
        c = cases_data[cnum]
        title_text = c['title'] if with_answers else NEUTRAL_CASE_TITLES.get(cnum, c['title'])
        html_out += f"""
        <div class="toc-item"><strong>Case {cnum}:</strong> {title_text}</div>"""

    html_out += """
      </div>
    </div>
  </div>

  <!-- CASES DATA -->
"""

    for cnum in sorted(cases_data.keys()):
        c = cases_data[cnum]
        
        case_title = c['title'] if with_answers else NEUTRAL_CASE_TITLES.get(cnum, c['title'])
        scen_text = c['scenario_neutral'] if not with_answers else c['scenario']
        vitals_text = c['vitals_neutral'] if not with_answers else c['vitals']
        
        # SVG Strip (height 56px for perfectly comfortable balance)
        svg_code = generate_ecg_svg(c['rhythm'], width=650, height=56, stroke=c['color'])
        ecg_label_str = c['label'] if with_answers else "ECG STRIP - MONITOR LEAD II"
        
        ecg_block = f"""
    <div class="ecg-container">
      <div class="ecg-strip-header">ECG Monitor: {ecg_label_str}</div>
      {svg_code}
    </div>
"""

        html_out += f"""
  <div class="case-card">
    <div class="case-header">
      <div class="case-num-title">
        <div class="c-label">{c.get('number', f'Case {cnum}')}</div>
        <h2>{case_title}</h2>
      </div>
      <div>{c.get('diff_tag', '')}</div>
    </div>

    {f'<div class="objective-box">{c["objective"]}</div>' if c.get('objective') else ''}

    <div class="scenario-box">
      <strong>Clinical Scenario:</strong> {scen_text}
      {ecg_block}
    </div>

    {f'<div class="vitals-box">{vitals_text}</div>' if vitals_text else ''}

    <div class="questions-section">
"""
        for idx, q in enumerate(c['questions'], 1):
            html_out += f"""
      <div class="question-block">
        <div class="q-title">Q{idx}. {q['question']}</div>
        <div class="options-list">
"""
            for opt in q['options']:
                if with_answers:
                    correct_cls = ' correct' if opt['correct'] else ''
                    checkbox_html = ''
                else:
                    correct_cls = ''
                    checkbox_html = '<span class="opt-checkbox"></span>'

                html_out += f"""
          <div class="opt-item{correct_cls}">{checkbox_html}<span>{opt['text']}</span></div>"""
            
            html_out += f"""
        </div>
"""
            if with_answers and q.get('explanation'):
                html_out += f"""
        <div class="exp-box">{q['explanation']}</div>"""
            
            html_out += """
      </div>
"""
        html_out += """
    </div>
  </div>
"""

    html_out += """
</body>
</html>
"""
    return html_out

# Generate HTMLs
with open('cases/acls-2025-cases-answers.html', 'w', encoding='utf-8') as f:
    f.write(generate_html_doc(with_answers=True))

with open('cases/acls-2025-cases-no-answers.html', 'w', encoding='utf-8') as f:
    f.write(generate_html_doc(with_answers=False))

print("Generated comfortably balanced 1-page per case print HTML templates successfully!")

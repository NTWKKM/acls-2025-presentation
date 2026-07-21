import re, json, subprocess, os

# Read source file
with open('cases/acls-2025-cases.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Split by slide div
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
        
        num_text = num_m.group(1).strip() if num_m else f'Case {case_num}'
        diff_tag = ''
        if 'difficulty-tag' in num_text:
            if 'core' in num_text.lower():
                diff_tag = '<span class="tag tag-core">Core</span>'
            elif 'advanced' in num_text.lower():
                diff_tag = '<span class="tag tag-advanced">Advanced</span>'
            num_text = re.sub(r'<span class="difficulty-tag[^"]*">.*?</span>', '', num_text, flags=re.DOTALL).strip()
        
        cases_data[case_num]['title'] = title_m.group(1).strip() if title_m else ''
        cases_data[case_num]['number'] = num_text
        cases_data[case_num]['diff_tag'] = diff_tag
        cases_data[case_num]['objective'] = obj_m.group(1).strip() if obj_m else ''
        cases_data[case_num]['scenario'] = scen_m.group(1).strip() if scen_m else ''
        cases_data[case_num]['vitals'] = vitals_m.group(1).strip() if vitals_m else ''
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
      margin: 15mm 15mm 18mm 15mm;
      @bottom-right {{
        content: counter(page);
      }}
    }}
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    
    body {{
      font-family: 'Sarabun', 'Segoe UI', Tahoma, sans-serif;
      color: #1e293b;
      background: #ffffff;
      line-height: 1.6;
      font-size: 14px;
    }}

    .cover-page {{
      padding: 40px 20px;
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
      margin-bottom: 20px;
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
      font-size: 18px;
      color: #64748b;
      margin-bottom: 40px;
      font-weight: 500;
    }}

    .toc-box {{
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 12px;
      padding: 24px 30px;
      text-align: left;
      max-width: 750px;
      margin: 0 auto;
    }}

    .toc-title {{
      font-size: 18px;
      font-weight: 700;
      color: #0f1e3d;
      margin-bottom: 16px;
      border-bottom: 2px solid #2563eb;
      padding-bottom: 8px;
    }}

    .toc-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 10px 24px;
    }}

    .toc-item {{
      font-size: 14px;
      color: #334155;
    }}
    .toc-item strong {{
      color: #2563eb;
    }}

    /* CASE SECTION */
    .case-card {{
      page-break-after: always;
      padding-top: 10px;
    }}

    .case-card:last-child {{
      page-break-after: avoid;
    }}

    .case-header {{
      border-bottom: 3px solid #2563eb;
      padding-bottom: 12px;
      margin-bottom: 16px;
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
    }}

    .case-num-title h2 {{
      font-family: 'Sora', 'Sarabun', sans-serif;
      font-size: 22px;
      color: #0f1e3d;
      font-weight: 700;
      line-height: 1.3;
    }}

    .case-num-title .c-label {{
      font-size: 13px;
      font-weight: 700;
      color: #2563eb;
      text-transform: uppercase;
      letter-spacing: 1px;
      margin-bottom: 4px;
    }}

    .tag {{
      display: inline-block;
      font-size: 11px;
      font-weight: 700;
      padding: 3px 10px;
      border-radius: 12px;
      text-transform: uppercase;
    }}
    .tag-core {{ background: #dbeafe; color: #1e40af; border: 1px solid #93c5fd; }}
    .tag-advanced {{ background: #fef3c7; color: #92400e; border: 1px solid #fcd34d; }}

    .objective-box {{
      background: #f0f9ff;
      border-left: 4px solid #0284c7;
      padding: 10px 14px;
      border-radius: 0 8px 8px 0;
      margin-bottom: 16px;
      font-size: 13.5px;
      color: #0369a1;
    }}

    .scenario-box {{
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 10px;
      padding: 14px 18px;
      margin-bottom: 16px;
      font-size: 15px;
      line-height: 1.55;
      color: #0f172a;
    }}

    .vitals-box {{
      background: #fff;
      border: 1px solid #cbd5e1;
      border-radius: 8px;
      padding: 12px 16px;
      margin-bottom: 20px;
    }}
    .vitals-box h4 {{
      font-size: 13.5px;
      color: #2563eb;
      margin-bottom: 8px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }}
    .vitals-box ul {{
      list-style: none;
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 6px 16px;
    }}
    .vitals-box li {{
      font-size: 13px;
      color: #334155;
    }}
    .vitals-box li strong {{ color: #0f172a; }}

    /* QUESTION ITEM */
    .question-block {{
      background: #ffffff;
      border: 1px solid #e2e8f0;
      border-radius: 10px;
      padding: 14px 18px;
      margin-bottom: 16px;
      page-break-inside: avoid;
    }}

    .q-title {{
      font-size: 15px;
      font-weight: 700;
      color: #0f1e3d;
      margin-bottom: 12px;
    }}

    .options-list {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px 12px;
      margin-bottom: 12px;
    }}

    .opt-item {{
      padding: 8px 12px;
      border-radius: 6px;
      border: 1px solid #cbd5e1;
      font-size: 13.5px;
      color: #334155;
      background: #f8fafc;
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    .opt-checkbox {{
      width: 14px;
      height: 14px;
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
      padding-top: 10px;
      margin-top: 8px;
      font-size: 13px;
      color: #475569;
    }}

    .exp-box h4 {{
      font-size: 13px;
      color: #2563eb;
      margin-bottom: 4px;
    }}

    .distractor-notes {{
      margin-top: 6px;
      padding-left: 16px;
    }}
    .distractor-notes li {{
      font-size: 12.5px;
      color: #64748b;
      margin-bottom: 2px;
    }}

    .key-teaching {{
      background: #eff6ff;
      border-left: 3px solid #2563eb;
      padding: 8px 12px;
      border-radius: 0 6px 6px 0;
      margin-top: 8px;
      font-size: 12.5px;
      color: #1e40af;
    }}
    .key-teaching strong {{ display: block; font-size: 11px; text-transform: uppercase; color: #2563eb; }}
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
        html_out += f"""
        <div class="toc-item"><strong>Case {cnum}:</strong> {c.get('title', '')}</div>"""

    html_out += """
      </div>
    </div>
  </div>

  <!-- CASES DATA -->
"""

    for cnum in sorted(cases_data.keys()):
        c = cases_data[cnum]
        html_out += f"""
  <div class="case-card">
    <div class="case-header">
      <div class="case-num-title">
        <div class="c-label">{c.get('number', f'Case {cnum}')}</div>
        <h2>{c.get('title', '')}</h2>
      </div>
      <div>{c.get('diff_tag', '')}</div>
    </div>

    {f'<div class="objective-box">{c["objective"]}</div>' if c.get('objective') else ''}

    <div class="scenario-box">
      <strong>Clinical Scenario:</strong><br>
      {c.get('scenario', '')}
    </div>

    {f'<div class="vitals-box">{c["vitals"]}</div>' if c.get('vitals') else ''}

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

print("Generated HTML print templates successfully!")

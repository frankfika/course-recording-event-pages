#!/usr/bin/env python3
"""Generate index.html from extracted.json for C1-Chapter3"""

import json
import re
import html

def load_data():
    with open('extracted.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def e(text):
    """Escape HTML entities"""
    return html.escape(text)

def md_to_html(lines):
    """Convert markdown-like text lines to HTML"""
    result = []
    in_table = False
    in_list = False

    for line in lines:
        stripped = line.strip()

        # Table handling
        if '|' in stripped and stripped.startswith('|'):
            if not in_table:
                if in_list:
                    result.append('</ul>')
                    in_list = False
                result.append('<table style="width:100%;border-collapse:collapse;margin:10px 0;font-size:0.85rem;">')
                in_table = True
            # Skip separator rows
            if re.match(r'^\|[\s\-:]+\|', stripped):
                continue
            cells = [c.strip() for c in stripped.strip('|').split('|')]
            is_header = not any('<td' in r for r in result[-5:] if '<t' in r) if len(result) > 0 else True
            tag = 'th' if result[-1].endswith('</table>') or (in_table and '<tr>' not in ''.join(result[-3:])) else 'td'
            # Check if it's likely a header row (first data row after table start)
            row_cells = ''.join(f'<td style="padding:6px 10px;border:1px solid var(--border);">{format_inline(c)}</td>' for c in cells)
            result.append(f'<tr>{row_cells}</tr>')
            continue
        elif in_table:
            result.append('</table>')
            in_table = False

        # Skip empty lines
        if not stripped:
            if in_list:
                result.append('</ul>')
                in_list = False
            continue

        # Horizontal rule
        if stripped == '---' or stripped == '————————————————':
            if in_list:
                result.append('</ul>')
                in_list = False
            result.append('<hr style="border:none;border-top:1px solid var(--border);margin:12px 0;">')
            continue

        # Headers
        if stripped.startswith('# ') and not stripped.startswith('# '):
            if in_list:
                result.append('</ul>')
                in_list = False
            result.append(f'<h3 style="margin:14px 0 8px;font-size:1.05rem;">{format_inline(stripped[2:])}</h3>')
            continue
        if stripped.startswith('## '):
            if in_list:
                result.append('</ul>')
                in_list = False
            result.append(f'<h4 style="margin:12px 0 6px;font-size:0.95rem;">{format_inline(stripped[3:])}</h4>')
            continue
        if stripped.startswith('### '):
            if in_list:
                result.append('</ul>')
                in_list = False
            result.append(f'<h5 style="margin:10px 0 4px;font-size:0.88rem;font-weight:600;">{format_inline(stripped[4:])}</h5>')
            continue
        if stripped.startswith('# '):
            if in_list:
                result.append('</ul>')
                in_list = False
            result.append(f'<h3 style="margin:14px 0 8px;font-size:1.05rem;">{format_inline(stripped[2:])}</h3>')
            continue

        # List items
        if stripped.startswith('- ') or stripped.startswith('* ') or re.match(r'^\d+\.\s', stripped):
            if not in_list:
                result.append('<ul style="margin:6px 0;padding-left:20px;">')
                in_list = True
            content = re.sub(r'^[-*]\s|^\d+\.\s', '', stripped)
            result.append(f'<li style="margin:3px 0;color:var(--text-700);font-size:0.85rem;">{format_inline(content)}</li>')
            continue

        # Blockquote
        if stripped.startswith('> '):
            if in_list:
                result.append('</ul>')
                in_list = False
            result.append(f'<blockquote style="border-left:3px solid var(--blue-500);padding-left:12px;margin:8px 0;color:var(--text-700);font-style:italic;font-size:0.85rem;">{format_inline(stripped[2:])}</blockquote>')
            continue

        # Regular paragraph
        if in_list:
            result.append('</ul>')
            in_list = False
        result.append(f'<p style="margin:6px 0;font-size:0.85rem;line-height:1.7;color:var(--text-700);">{format_inline(stripped)}</p>')

    if in_list:
        result.append('</ul>')
    if in_table:
        result.append('</table>')

    return '\n'.join(result)

def format_inline(text):
    """Format inline markdown: bold, code, etc."""
    text = html.escape(text)
    # Bold
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    # Inline code
    text = re.sub(r'`(.+?)`', r'<code style="background:var(--bg-gray);padding:1px 5px;border-radius:4px;font-size:0.82rem;">\1</code>', text)
    # Emoji preservation (already in text)
    return text

def get_css():
    with open('/Users/fangchen/.claude/skills/course-ppt-design/assets/template.css', 'r') as f:
        return f.read()

def get_nav_js(total):
    return f"""<script>
const nav = document.getElementById('slideNav');
for (let i = 1; i <= {total}; i++) {{
  const a = document.createElement('a');
  a.href = '#s' + i;
  a.dataset.slide = i;
  nav.appendChild(a);
}}

const observer = new IntersectionObserver(entries => {{
  entries.forEach(e => {{
    if (e.isIntersecting) {{
      const id = e.target.id;
      document.querySelectorAll('.slide-nav a').forEach(a => a.classList.remove('active'));
      const active = document.querySelector(`.slide-nav a[href="#${{id}}"]`);
      if (active) active.classList.add('active');
    }}
  }});
}}, {{ threshold: 0.5 }});

document.querySelectorAll('.slide').forEach(s => observer.observe(s));

document.addEventListener('keydown', e => {{
  const slides = document.querySelectorAll('.slide');
  const current = [...slides].findIndex(s => {{
    const r = s.getBoundingClientRect();
    return r.top >= -100 && r.top < window.innerHeight / 2;
  }});
  if (e.key === 'ArrowDown' || e.key === ' ' || e.key === 'PageDown') {{
    e.preventDefault();
    if (current < slides.length - 1) slides[current + 1].scrollIntoView({{ behavior: 'smooth' }});
  }}
  if (e.key === 'ArrowUp' || e.key === 'PageUp') {{
    e.preventDefault();
    if (current > 0) slides[current - 1].scrollIntoView({{ behavior: 'smooth' }});
  }}
}});
</script>"""

# Model info mapping
MODEL_INFO = {
    'MiniMax-M2.7': {'color': '#3B82F6', 'icon_key': '图片_7'},
    'Kimi K2': {'color': '#9333EA', 'icon_key': '图片_8'},
    'Kimi-k2': {'color': '#9333EA', 'icon_key': '图片_8'},
    'Deepseek V3.1': {'color': '#059669', 'icon_key': '图片_9'},
    'DeepSeek V3.1': {'color': '#059669', 'icon_key': '图片_9'},
    '豆包Doubao-Seed-2.0': {'color': '#F97316', 'icon_key': '图片_11'},
    'GPT 5.4': {'color': '#111827', 'icon_key': '图片_12'},
    'Claude Opus 4.5': {'color': '#DB2777', 'icon_key': '图片_14'},
    'Claude 4.7': {'color': '#DB2777', 'icon_key': '图片_14'},
}

MODEL_COLORS = {
    'MiniMax-M2.7': '#3B82F6',
    'Kimi K2': '#9333EA',
    'Kimi-k2': '#9333EA',
    'Deepseek V3.1': '#059669',
    'DeepSeek V3.1': '#059669',
    '豆包Doubao-Seed-2.0': '#F97316',
    'GPT 5.4': '#111827',
    'Claude Opus 4.5': '#DB2777',
    'Claude 4.7': '#DB2777',
}

ROUND_COLORS = {
    'Round 1': '#3B82F6',
    'Round 2': '#9333EA',
    'Round 3': '#059669',
    'Round 4': '#F97316',
    'Round 5': '#DB2777',
}

def find_model_icon(slide, model_name):
    """Find the model icon image from the slide"""
    if not slide['images']:
        return None
    info = MODEL_INFO.get(model_name)
    if info:
        for img in slide['images']:
            if info['icon_key'] in img['file']:
                return img['file']
    # Fallback: first image
    return slide['images'][0]['file'] if slide['images'] else None

def gen_model_response_slide(slide, slide_idx, total, round_tag, topic, model_name):
    """Generate a model response slide"""
    texts = slide['texts']

    # Extract content: skip "main.py" at start, and round/topic/model at end
    content_texts = []
    skip_end = 0
    for t in reversed(texts):
        if t.startswith('Round ') or t.startswith('结果对比') or t in MODEL_INFO or t in ['Kimi K2', 'Kimi-k2', 'Deepseek V3.1', 'DeepSeek V3.1', 'MiniMax-M2.7', '豆包Doubao-Seed-2.0', 'GPT 5.4', 'Claude Opus 4.5', 'Claude 4.7']:
            skip_end += 1
        else:
            break

    start = 1 if texts[0] == 'main.py' else 0
    end = len(texts) - skip_end if skip_end > 0 else len(texts)
    content_texts = texts[start:end]

    icon = find_model_icon(slide, model_name)
    color = MODEL_COLORS.get(model_name, '#3B82F6')
    round_color = ROUND_COLORS.get(round_tag, '#3B82F6')

    content_html = md_to_html(content_texts)

    icon_html = f'<img src="{icon}" alt="{e(model_name)}" style="width:36px;height:36px;border-radius:8px;object-fit:contain;">' if icon else ''

    return f'''
<section class="slide" id="s{slide_idx}">
  <div class="slide-inner stagger">
    <div style="display:flex;align-items:center;gap:12px;margin-bottom:8px;">
      <span class="tag" style="background:{round_color}15;color:{round_color};">{e(round_tag)}</span>
      <p style="color:var(--text-400);font-size:0.8rem;">结果对比：{e(topic)}</p>
    </div>
    <div style="display:flex;align-items:center;gap:12px;margin-bottom:16px;">
      {icon_html}
      <h2 style="font-size:1.3rem;">{e(model_name)}</h2>
    </div>
    <div class="script-block" style="max-height:65vh;overflow-y:auto;padding:20px 24px;">
      {content_html}
    </div>
  </div>
  <span class="page-num">{slide_idx:02d} / {total:02d}</span>
</section>'''

def generate_html():
    data = load_data()
    slides = data['slides']
    total = len(slides)  # 41
    css = get_css()

    sections = []

    # ===== Slide 1: Cover =====
    s = slides[0]
    sections.append(f'''
<section class="slide" id="s1" style="background:var(--bg-blue);">
  <div class="slide-inner stagger" style="text-align:center;">
    <span class="tag tag-dark" style="margin-bottom:16px;">C1</span>
    <p style="color:var(--blue-600);font-weight:600;margin-bottom:12px;">必修 · 5节</p>
    <h1 style="margin-bottom:16px;">AI工具与核心概念</h1>
    <p style="color:var(--text-500);font-size:1.1rem;margin-bottom:24px;">从零建立对AI的完整认知</p>
    <p style="color:var(--text-400);font-size:0.9rem;">讲师：陈放</p>
  </div>
  <span class="page-num">01 / {total:02d}</span>
</section>''')

    # ===== Slide 2: Chapter Divider =====
    s = slides[1]
    sections.append(f'''
<section class="slide" id="s2" style="background:linear-gradient(135deg, #1E3A5F 0%, #0F172A 100%);">
  <div class="slide-inner stagger" style="text-align:center;">
    <span class="tag tag-dark" style="border:1px solid rgba(255,255,255,0.2);margin-bottom:20px;">CHAPTER 3</span>
    <h1 style="color:white;font-size:clamp(2.5rem,5vw,4rem);margin-bottom:16px;">2026大模型擂台赛</h1>
    <p style="color:rgba(255,255,255,0.6);font-size:1.2rem;">AI已经开始替你上班</p>
  </div>
  <div class="deco" style="width:300px;height:300px;background:rgba(59,130,246,0.15);top:-80px;right:-60px;"></div>
  <div class="deco" style="width:200px;height:200px;background:rgba(147,51,234,0.1);bottom:-40px;left:-40px;"></div>
  <span class="page-num" style="color:rgba(255,255,255,0.4);">02 / {total:02d}</span>
</section>''')

    # ===== Slide 3: Quote =====
    sections.append(f'''
<section class="slide" id="s3" style="background:var(--bg);">
  <div class="slide-inner stagger" style="text-align:center;">
    <div class="quote-bar" style="text-align:left;max-width:800px;margin:0 auto;">
      <h2 style="font-size:clamp(1.5rem,3vw,2.2rem);line-height:1.5;margin-bottom:20px;">"别再问哪个AI更聪明了<br>——先问谁更适合你的场景"</h2>
    </div>
    <div style="display:flex;flex-wrap:wrap;gap:10px;justify-content:center;margin-top:32px;">
      <span class="pill">DeepSeek V3.1</span>
      <span class="pill">MiniMax-M2.7</span>
      <span class="pill">豆包Doubao-Seed-2.0</span>
      <span class="pill">Kimi-k2</span>
      <span class="pill">GPT 5.4</span>
      <span class="pill">Claude 4.7</span>
    </div>
  </div>
  <span class="page-num">03 / {total:02d}</span>
</section>''')

    # ===== Slide 4: Model Introductions =====
    s = slides[3]
    models_domestic = [
        ('MiniMax-M2.7', '系宇科技（轻量理想）', 'images/slide4_图片_7.jpg'),
        ('Kimi-k2', '月之暗面（长文处理强领）', 'images/slide4_图片_8.png'),
        ('DeepSeek V3.1', '幽方量化（推理强，开源企业落地友好）', 'images/slide4_图片_9.png'),
        ('豆包Doubao-Seed-2.0', '字节跳动（多模态体验顺手）', 'images/slide4_图片_11.png'),
    ]
    models_foreign = [
        ('GPT 5.4', 'OpenAI（元级模型开创者）', 'images/slide4_图片_12.jpg'),
        ('Claude Sonnet 4.7', 'Anthropic（安全性强，代码与长任务依然强）', 'images/slide4_图片_14.png'),
    ]

    domestic_cards = ''
    for name, desc, img in models_domestic:
        domestic_cards += f'''
        <div class="card" style="display:flex;align-items:center;gap:14px;">
          <img src="{img}" alt="{e(name)}" style="width:44px;height:44px;border-radius:10px;object-fit:contain;">
          <div>
            <h3 style="font-size:0.9rem;">{e(name)}</h3>
            <p style="font-size:0.78rem;margin-top:2px;">{e(desc)}</p>
          </div>
        </div>'''

    foreign_cards = ''
    for name, desc, img in models_foreign:
        foreign_cards += f'''
        <div class="card" style="display:flex;align-items:center;gap:14px;">
          <img src="{img}" alt="{e(name)}" style="width:44px;height:44px;border-radius:10px;object-fit:contain;">
          <div>
            <h3 style="font-size:0.9rem;">{e(name)}</h3>
            <p style="font-size:0.78rem;margin-top:2px;">{e(desc)}</p>
          </div>
        </div>'''

    sections.append(f'''
<section class="slide" id="s4" style="background:var(--bg);">
  <div class="slide-inner stagger">
    <h2 style="margin-bottom:24px;">模型与公司介绍</h2>
    <span class="tag tag-blue" style="margin-bottom:12px;">🇨🇳 国产模型</span>
    <div class="card-grid card-grid-2" style="margin-bottom:24px;">
      {domestic_cards}
    </div>
    <span class="tag tag-purple" style="margin-bottom:12px;">🌍 非国产模型</span>
    <div class="card-grid card-grid-2">
      {foreign_cards}
    </div>
  </div>
  <span class="page-num">04 / {total:02d}</span>
</section>''')

    # ===== Slide 5: GPT Timeline =====
    s = slides[4]
    sections.append(f'''
<section class="slide" id="s5" style="background:var(--bg);">
  <div class="slide-inner stagger">
    <span class="tag tag-blue" style="margin-bottom:12px;">📊 时间线</span>
    <h2 style="margin-bottom:8px;">{e(s['texts'][0])}</h2>
    <p style="margin-bottom:20px;">{e(s['texts'][1])}</p>
    <div class="timeline">
      <div class="timeline-step">
        <div class="timeline-icon" style="background:var(--bg-blue);color:var(--blue-500);">📄</div>
        <h3 style="font-size:0.82rem;">GPT-3</h3>
        <p style="font-size:0.72rem;">2020.06</p>
      </div>
      <div class="timeline-step">
        <div class="timeline-icon" style="background:var(--bg-green);color:var(--green-500);">💬</div>
        <h3 style="font-size:0.82rem;">GPT-3.5</h3>
        <p style="font-size:0.72rem;">2022.11</p>
      </div>
      <div class="timeline-step">
        <div class="timeline-icon" style="background:var(--bg-purple);color:var(--purple-500);">🧠</div>
        <h3 style="font-size:0.82rem;">GPT-4</h3>
        <p style="font-size:0.72rem;">2023.03</p>
      </div>
      <div class="timeline-step">
        <div class="timeline-icon" style="background:var(--bg-pink);color:var(--pink-500);">👁️</div>
        <h3 style="font-size:0.82rem;">GPT-4o</h3>
        <p style="font-size:0.72rem;">2024.05</p>
      </div>
      <div class="timeline-step">
        <div class="timeline-icon" style="background:var(--bg-dark);color:white;">🚀</div>
        <h3 style="font-size:0.82rem;">GPT-5.4</h3>
        <p style="font-size:0.72rem;">2026.03</p>
      </div>
    </div>
    <p style="font-size:0.72rem;color:var(--text-400);margin-top:20px;text-align:center;">{e(s['texts'][2])}</p>
  </div>
  <span class="page-num">05 / {total:02d}</span>
</section>''')

    # ===== Slide 6: Competition Rules =====
    round_icons = ['✍️', '🧠', '💻', '📊', '🤖']
    round_names = ['写作', '推理', '代码', '数据分析', 'Agent规划']
    round_colors_list = ['var(--blue-500)', 'var(--purple-500)', 'var(--green-500)', 'var(--orange-500)', 'var(--pink-500)']

    round_cards = ''
    for i in range(5):
        round_cards += f'''
        <div class="card" style="text-align:center;border-top:3px solid {round_colors_list[i]};">
          <div style="font-size:1.8rem;margin-bottom:8px;">{round_icons[i]}</div>
          <span class="tag" style="background:{round_colors_list[i]}15;color:{round_colors_list[i]};font-size:0.7rem;margin-bottom:6px;">Round {i+1}</span>
          <h3 style="font-size:0.95rem;">{round_names[i]}</h3>
        </div>'''

    sections.append(f'''
<section class="slide" id="s6" style="background:var(--bg);">
  <div class="slide-inner stagger">
    <h2 style="margin-bottom:24px;text-align:center;">比赛规则</h2>
    <div class="card-grid" style="grid-template-columns:repeat(5,1fr);gap:14px;">
      {round_cards}
    </div>
    <p style="text-align:center;margin-top:24px;color:var(--text-400);font-size:0.85rem;">⚠️ 横评有效期只有30天——模型更新太快，排名随时会变</p>
  </div>
  <span class="page-num">06 / {total:02d}</span>
</section>''')

    # ===== Slide 7: Round 1 Prompt =====
    s = slides[6]
    sections.append(f'''
<section class="slide" id="s7" style="background:var(--bg);">
  <div class="slide-inner stagger">
    <span class="tag tag-blue" style="margin-bottom:12px;">✍️ Round 1</span>
    <h2 style="margin-bottom:20px;">写一封能直接发的招生邮件</h2>
    <div class="card" style="margin-bottom:20px;">
      <p style="font-size:0.9rem;line-height:1.8;color:var(--text-700);">请写一封180字以内的招生邮件，目标用户是30-40岁的职场管理者，主题是"AI不是学一个工具，而是重构工作方式"。要求：不油腻、不喊口号，要有行动感。</p>
    </div>
    <h3 style="margin-bottom:12px;">评判标准</h3>
    <div class="card-grid card-grid-3">
      <div class="card" style="border-top:3px solid var(--blue-500);text-align:center;">
        <p style="font-size:0.85rem;">语气得体，不油腻不喊口号</p>
      </div>
      <div class="card" style="border-top:3px solid var(--purple-500);text-align:center;">
        <p style="font-size:0.85rem;">180字以内，能直接发</p>
      </div>
      <div class="card" style="border-top:3px solid var(--green-500);text-align:center;">
        <p style="font-size:0.85rem;">有行动感，读完想点链接</p>
      </div>
    </div>
  </div>
  <span class="page-num">07 / {total:02d}</span>
</section>''')

    # ===== Slides 8-13: Round 1 Results =====
    r1_models = [
        (8, 'MiniMax-M2.7'), (9, 'Kimi K2'), (10, 'Deepseek V3.1'),
        (11, '豆包Doubao-Seed-2.0'), (12, 'GPT 5.4'), (13, 'Claude Opus 4.5')
    ]
    for idx, (slide_num, model) in enumerate(r1_models):
        s = slides[slide_num - 1]
        sections.append(gen_model_response_slide(s, slide_num, total, 'Round 1', '招生邮件', model))

    # ===== Slide 14: Round 2 Prompt =====
    s = slides[13]
    constraint_items = ''
    constraints = [
        '每人必须上完全部4门课，每门只上一次',
        '每门课在整周恰好开2次（供不同人选择）',
        '每次上课最多坐3人',
        'Alice和Bob不能同堂',
        '编程(P)必须在设计(D)之前上（对每个人都适用）',
        'David周三全天缺席',
        'Carol只能上午来',
    ]
    for i, c in enumerate(constraints):
        constraint_items += f'<li style="margin:4px 0;font-size:0.85rem;color:var(--text-700);">{e(c)}</li>'

    sections.append(f'''
<section class="slide" id="s14" style="background:var(--bg);">
  <div class="slide-inner stagger">
    <span class="tag tag-purple" style="margin-bottom:12px;">🧠 Round 2</span>
    <h2 style="margin-bottom:8px;">排一个满足所有约束的课表</h2>
    <p style="margin-bottom:16px;color:var(--text-500);">⏺ 排课逻辑题</p>
    <div class="card" style="margin-bottom:16px;">
      <p style="font-size:0.85rem;line-height:1.7;color:var(--text-700);margin-bottom:8px;">某培训机构要在周一到周五给4名学员排4门课。学员：Alice、Bob、Carol、David。课程：数学(M)、英语(E)、编程(P)、设计(D)。每天2个时段：上午/下午。只有1间教室，每时段只能开1门课。</p>
      <h3 style="font-size:0.88rem;margin-bottom:6px;">约束条件</h3>
      <ol style="padding-left:20px;">
        {constraint_items}
      </ol>
    </div>
    <h3 style="margin-bottom:10px;">评判标准</h3>
    <div class="card-grid card-grid-2" style="gap:10px;">
      <div class="card" style="padding:14px;border-top:3px solid var(--purple-500);"><p style="font-size:0.82rem;">所有约束是否全部满足</p></div>
      <div class="card" style="padding:14px;border-top:3px solid var(--blue-500);"><p style="font-size:0.82rem;">有无遗漏或冲突</p></div>
      <div class="card" style="padding:14px;border-top:3px solid var(--green-500);"><p style="font-size:0.82rem;">推理过程是否清晰可追溯</p></div>
      <div class="card" style="padding:14px;border-top:3px solid var(--orange-500);"><p style="font-size:0.82rem;">输出格式是否结构化</p></div>
    </div>
  </div>
  <span class="page-num">14 / {total:02d}</span>
</section>''')

    # ===== Slides 15-20: Round 2 Results =====
    r2_models = [
        (15, 'MiniMax-M2.7'), (16, 'Kimi K2'), (17, 'Deepseek V3.1'),
        (18, '豆包Doubao-Seed-2.0'), (19, 'GPT 5.4'), (20, 'Claude Opus 4.5')
    ]
    for idx, (slide_num, model) in enumerate(r2_models):
        s = slides[slide_num - 1]
        sections.append(gen_model_response_slide(s, slide_num, total, 'Round 2', '排一个满足所有约束的课表', model))

    # ===== Slide 21: Round 3 Prompt =====
    sections.append(f'''
<section class="slide" id="s21" style="background:var(--bg);">
  <div class="slide-inner stagger">
    <span class="tag tag-green" style="margin-bottom:12px;">💻 Round 3</span>
    <h2 style="margin-bottom:16px;">做一个课程报名页</h2>
    <div class="card" style="margin-bottom:20px;">
      <p style="font-size:0.88rem;line-height:1.8;color:var(--text-700);">用HTML+CSS+JS做一个课程报名页：顶部强钩子标题，中间3个课程亮点带图标，讲师介绍区域，报名表单（姓名/手机/公司/职位），主色#23877B，适配手机端。</p>
    </div>
    <h3 style="margin-bottom:12px;">四个评判角度</h3>
    <div class="card-grid" style="grid-template-columns:repeat(4,1fr);gap:12px;">
      <div class="card" style="text-align:center;border-top:3px solid var(--blue-500);padding:16px;">
        <p style="font-size:1.4rem;margin-bottom:6px;">🎨</p>
        <h3 style="font-size:0.85rem;">视觉</h3>
        <p style="font-size:0.78rem;">好不好看</p>
      </div>
      <div class="card" style="text-align:center;border-top:3px solid var(--green-500);padding:16px;">
        <p style="font-size:1.4rem;margin-bottom:6px;">⚙️</p>
        <h3 style="font-size:0.85rem;">功能</h3>
        <p style="font-size:0.78rem;">能不能用</p>
      </div>
      <div class="card" style="text-align:center;border-top:3px solid var(--purple-500);padding:16px;">
        <p style="font-size:1.4rem;margin-bottom:6px;">📱</p>
        <h3 style="font-size:0.85rem;">响应式</h3>
        <p style="font-size:0.78rem;">手机能看</p>
      </div>
      <div class="card" style="text-align:center;border-top:3px solid var(--orange-500);padding:16px;">
        <p style="font-size:1.4rem;margin-bottom:6px;">📝</p>
        <h3 style="font-size:0.85rem;">代码</h3>
        <p style="font-size:0.78rem;">质量如何</p>
      </div>
    </div>
  </div>
  <span class="page-num">21 / {total:02d}</span>
</section>''')

    # ===== Slide 22: Round 3 Results (Screenshots) =====
    s = slides[21]
    screenshot_models = ['MiniMax-M2.7', 'Kimi-k2', 'DeepSeek V3.1', '豆包Doubao-Seed-2.0', 'GPT 5.4', 'Claude 4.7']
    screenshot_cards = ''
    for i, img in enumerate(s['images']):
        model_name = screenshot_models[i] if i < len(screenshot_models) else f'模型 {i+1}'
        screenshot_cards += f'''
      <div class="card" style="padding:0;overflow:hidden;">
        <div class="img-frame" style="border:none;border-radius:0;">
          <img src="{img['file']}" alt="{e(model_name)}" style="width:100%;height:auto;display:block;max-height:300px;object-fit:contain;">
        </div>
        <div style="padding:10px 14px;border-top:1px solid var(--border);">
          <h3 style="font-size:0.82rem;text-align:center;">{e(model_name)}</h3>
        </div>
      </div>'''

    sections.append(f'''
<section class="slide" id="s22" style="background:var(--bg);">
  <div class="slide-inner stagger">
    <div style="display:flex;align-items:center;gap:12px;margin-bottom:16px;">
      <span class="tag tag-green">💻 Round 3</span>
      <p style="color:var(--text-400);font-size:0.8rem;">结果对比：做一个课程报名页</p>
    </div>
    <div class="card-grid card-grid-3" style="gap:14px;">
      {screenshot_cards}
    </div>
  </div>
  <span class="page-num">22 / {total:02d}</span>
</section>''')

    # ===== Slide 23: Round 4 Prompt =====
    s = slides[22]
    dashboard_img = ''
    for img in s['images']:
        if '图片_11' in img['file']:
            dashboard_img = img['file']

    sections.append(f'''
<section class="slide" id="s23" style="background:var(--bg);">
  <div class="slide-inner stagger">
    <span class="tag tag-orange" style="margin-bottom:12px;">📊 Round 4</span>
    <h2 style="margin-bottom:16px;">看一张运营看板，说出关键结论</h2>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;">
      <div>
        <div class="img-frame" style="margin-bottom:16px;">
          <img src="{dashboard_img}" alt="运营看板截图" style="width:100%;height:auto;display:block;max-height:340px;object-fit:contain;">
        </div>
        <p style="font-size:0.8rem;color:var(--text-400);text-align:center;">运营看板截图</p>
      </div>
      <div>
        <div class="card" style="margin-bottom:12px;">
          <h3 style="font-size:0.88rem;margin-bottom:8px;">任务要求</h3>
          <ul style="padding-left:16px;">
            <li style="font-size:0.82rem;margin:4px 0;">根据目前的销售运营看板</li>
            <li style="font-size:0.82rem;margin:4px 0;">给出3个关键结论、指出1个潜在风险、提出1个建议动作</li>
            <li style="font-size:0.82rem;margin:4px 0;">基于数据，不要泛泛而谈</li>
          </ul>
          <p style="font-size:0.78rem;color:var(--text-400);margin-top:8px;">我们这里只测试模型的思维，并不是测试模型的视觉能力</p>
        </div>
        <h3 style="font-size:0.88rem;margin-bottom:8px;">评判标准</h3>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;">
          <div class="card" style="padding:10px;border-top:2px solid var(--orange-500);"><p style="font-size:0.78rem;">数据引用准确性</p></div>
          <div class="card" style="padding:10px;border-top:2px solid var(--blue-500);"><p style="font-size:0.78rem;">洞察深度</p></div>
          <div class="card" style="padding:10px;border-top:2px solid var(--purple-500);"><p style="font-size:0.78rem;">风险识别合理性</p></div>
          <div class="card" style="padding:10px;border-top:2px solid var(--green-500);"><p style="font-size:0.78rem;">建议可执行性</p></div>
        </div>
      </div>
    </div>
  </div>
  <span class="page-num">23 / {total:02d}</span>
</section>''')

    # ===== Slides 24-29: Round 4 Results =====
    r4_models = [
        (24, 'MiniMax-M2.7'), (25, 'Kimi K2'), (26, 'Deepseek V3.1'),
        (27, '豆包Doubao-Seed-2.0'), (28, 'GPT 5.4'), (29, 'Claude Opus 4.5')
    ]
    for idx, (slide_num, model) in enumerate(r4_models):
        s = slides[slide_num - 1]
        sections.append(gen_model_response_slide(s, slide_num, total, 'Round 4', '看一张运营看板，说出关键结论', model))

    # ===== Slide 30: Round 5 Prompt =====
    s = slides[29]
    sections.append(f'''
<section class="slide" id="s30" style="background:var(--bg);">
  <div class="slide-inner stagger">
    <span class="tag tag-pink" style="margin-bottom:12px;">🤖 Round 5</span>
    <h2 style="margin-bottom:16px;">让AI Agent规划一个任务执行路径和方法</h2>
    <div class="card" style="margin-bottom:16px;">
      <p style="font-size:0.85rem;line-height:1.8;color:var(--text-700);margin-bottom:10px;"><strong>【任务】</strong>帮我写一份《中国制造业AI应用现状与趋势》行业分析报告的写作的执行计划。</p>
      <p style="font-size:0.85rem;line-height:1.8;color:var(--text-700);margin-bottom:10px;"><strong>【约束】</strong></p>
      <ul style="padding-left:20px;margin-bottom:10px;">
        <li style="font-size:0.82rem;margin:3px 0;">面向CEO/CFO等高管读者</li>
        <li style="font-size:0.82rem;margin:3px 0;">篇幅8000字左右</li>
        <li style="font-size:0.82rem;margin:3px 0;">需要数据支撑</li>
        <li style="font-size:0.82rem;margin:3px 0;">3天后要交初稿</li>
      </ul>
      <p style="font-size:0.85rem;color:var(--text-700);"><strong>【要求】</strong>请作为AI助手，规划出你完成这个任务的具体执行计划。</p>
    </div>
    <div class="card" style="background:var(--bg-gray);margin-bottom:16px;">
      <h3 style="font-size:0.85rem;margin-bottom:6px;">输出格式</h3>
      <pre style="font-size:0.78rem;color:var(--text-700);line-height:1.6;white-space:pre-wrap;">## 执行Plan
### Step 1: [任务名称]
- 目标 / 工具/数据源 / 预计产出 / 前置依赖
## 关键决策点
## 风险与备选方案
## 你认为最难的一步是什么？为什么？</pre>
    </div>
    <h3 style="margin-bottom:10px;">评判标准</h3>
    <div class="card-grid" style="grid-template-columns:repeat(4,1fr);gap:10px;">
      <div class="card" style="padding:12px;border-top:2px solid var(--pink-500);text-align:center;"><p style="font-size:0.78rem;">步骤完整性</p></div>
      <div class="card" style="padding:12px;border-top:2px solid var(--blue-500);text-align:center;"><p style="font-size:0.78rem;">可操作性</p></div>
      <div class="card" style="padding:12px;border-top:2px solid var(--purple-500);text-align:center;"><p style="font-size:0.78rem;">时间约束拆解</p></div>
      <div class="card" style="padding:12px;border-top:2px solid var(--green-500);text-align:center;"><p style="font-size:0.78rem;">风险与备选配对</p></div>
    </div>
  </div>
  <span class="page-num">30 / {total:02d}</span>
</section>''')

    # ===== Slides 31-36: Round 5 Results =====
    r5_models = [
        (31, 'MiniMax-M2.7'), (32, 'Kimi K2'), (33, 'Deepseek V3.1'),
        (34, '豆包Doubao-Seed-2.0'), (35, 'GPT 5.4'), (36, 'Claude Opus 4.5')
    ]
    for idx, (slide_num, model) in enumerate(r5_models):
        s = slides[slide_num - 1]
        sections.append(gen_model_response_slide(s, slide_num, total, 'Round 5', 'AI Agent任务规划', model))

    # ===== Slide 37: Round 5 Summary =====
    s = slides[36]
    summary_items = [
        ('DeepSeek V3.1', '拆解清楚，逻辑链完整', 'var(--green-500)'),
        ('MiniMax-M2.7', '实用导向强，适合国内业务落地', 'var(--blue-500)'),
        ('豆包Doubao-Seed-2.0', '分工直白，适合快速协同', 'var(--orange-500)'),
        ('Kimi-k2', '节奏安排清楚，但颗粒度略粗', 'var(--purple-500)'),
        ('Claude 4.7', '清单最细，审核环节意识最强', 'var(--pink-500)'),
    ]
    summary_cards = ''
    for name, desc, color in summary_items:
        summary_cards += f'''
      <div class="card" style="border-left:4px solid {color};display:flex;align-items:center;gap:14px;">
        <div>
          <h3 style="font-size:0.9rem;">{e(name)}</h3>
          <p style="font-size:0.82rem;">{e(desc)}</p>
        </div>
      </div>'''

    sections.append(f'''
<section class="slide" id="s37" style="background:var(--bg);">
  <div class="slide-inner stagger">
    <span class="tag tag-pink" style="margin-bottom:12px;">🤖 Round 5</span>
    <h2 style="margin-bottom:20px;">结果对比</h2>
    <div class="img-frame" style="margin-bottom:20px;">
      <img src="images/slide37_图片_28.png" alt="Round 5 对比图" style="width:100%;height:auto;display:block;max-height:340px;object-fit:contain;">
    </div>
    <div class="card-grid" style="grid-template-columns:1fr;gap:10px;">
      {summary_cards}
    </div>
  </div>
  <span class="page-num">37 / {total:02d}</span>
</section>''')

    # ===== Slide 38: Quick Reference Table =====
    table_rows = [
        ('写邮件、写文案、写报告', 'Kimi-k2 / MiniMax-M2.7', '✍️'),
        ('逻辑推理、排计划、算约束', 'DeepSeek / Claude 4.7', '🧠'),
        ('写代码、做网页、技术开发', 'MiniMax-M2.7 / Claude 4.7', '💻'),
        ('看图、看视频、分析数据看板', '豆包AI / MiniMax-M2.7', '📊'),
        ('中文场景、国内合规需求', 'MiniMax-M2.7 / DeepSeek V3.1', '🇨🇳'),
    ]
    rows_html = ''
    row_colors = ['var(--blue-500)', 'var(--purple-500)', 'var(--green-500)', 'var(--orange-500)', 'var(--pink-500)']
    for i, (scenario, model, icon) in enumerate(table_rows):
        rows_html += f'''
      <div class="card" style="display:grid;grid-template-columns:auto 1fr auto;align-items:center;gap:14px;border-left:3px solid {row_colors[i]};">
        <span style="font-size:1.3rem;">{icon}</span>
        <div>
          <h3 style="font-size:0.88rem;">{e(scenario)}</h3>
        </div>
        <span class="pill" style="font-size:0.78rem;">{e(model)}</span>
      </div>'''

    sections.append(f'''
<section class="slide" id="s38" style="background:var(--bg);">
  <div class="slide-inner stagger">
    <span class="tag tag-blue" style="margin-bottom:12px;">📋 速查表</span>
    <h2 style="margin-bottom:20px;">选模型速查表（国内优先版）</h2>
    <div style="display:grid;gap:12px;">
      {rows_html}
    </div>
    <p style="text-align:center;margin-top:20px;color:var(--text-400);font-size:0.78rem;">推荐基于当前版本测试结果，建议用你自己的真实任务验证。</p>
  </div>
  <span class="page-num">38 / {total:02d}</span>
</section>''')

    # ===== Slide 39: Score Table =====
    models_scores = ['DeepSeek V3.1', 'MiniMax-M2.7', '豆包Doubao-Seed-2.0', 'Kimi-k2', 'Claude 4.7']
    dimensions = ['写作', '推理', '代码', '多模态', 'Agent']

    sections.append(f'''
<section class="slide" id="s39" style="background:var(--bg);">
  <div class="slide-inner stagger">
    <span class="tag tag-purple" style="margin-bottom:12px;">🏆 评分榜</span>
    <h2 style="margin-bottom:20px;">做一个简单的模型评分榜</h2>
    <div class="card" style="overflow-x:auto;">
      <table style="width:100%;border-collapse:collapse;text-align:center;">
        <thead>
          <tr>
            <th style="padding:12px 10px;border-bottom:2px solid var(--border);text-align:left;font-size:0.85rem;">模型</th>
            <th style="padding:12px 10px;border-bottom:2px solid var(--border);font-size:0.85rem;">✍️ 写作</th>
            <th style="padding:12px 10px;border-bottom:2px solid var(--border);font-size:0.85rem;">🧠 推理</th>
            <th style="padding:12px 10px;border-bottom:2px solid var(--border);font-size:0.85rem;">💻 代码</th>
            <th style="padding:12px 10px;border-bottom:2px solid var(--border);font-size:0.85rem;">📊 多模态</th>
            <th style="padding:12px 10px;border-bottom:2px solid var(--border);font-size:0.85rem;">🤖 Agent</th>
            <th style="padding:12px 10px;border-bottom:2px solid var(--border);font-size:0.85rem;font-weight:700;">总分</th>
          </tr>
        </thead>
        <tbody>
          <tr><td style="padding:10px;border-bottom:1px solid var(--border-light);text-align:left;font-weight:600;">DeepSeek V3.1</td><td style="padding:10px;border-bottom:1px solid var(--border-light);">—</td><td style="padding:10px;border-bottom:1px solid var(--border-light);">—</td><td style="padding:10px;border-bottom:1px solid var(--border-light);">—</td><td style="padding:10px;border-bottom:1px solid var(--border-light);">—</td><td style="padding:10px;border-bottom:1px solid var(--border-light);">—</td><td style="padding:10px;border-bottom:1px solid var(--border-light);font-weight:700;">—</td></tr>
          <tr><td style="padding:10px;border-bottom:1px solid var(--border-light);text-align:left;font-weight:600;">MiniMax-M2.7</td><td style="padding:10px;border-bottom:1px solid var(--border-light);">—</td><td style="padding:10px;border-bottom:1px solid var(--border-light);">—</td><td style="padding:10px;border-bottom:1px solid var(--border-light);">—</td><td style="padding:10px;border-bottom:1px solid var(--border-light);">—</td><td style="padding:10px;border-bottom:1px solid var(--border-light);">—</td><td style="padding:10px;border-bottom:1px solid var(--border-light);font-weight:700;">—</td></tr>
          <tr><td style="padding:10px;border-bottom:1px solid var(--border-light);text-align:left;font-weight:600;">豆包Doubao-Seed-2.0</td><td style="padding:10px;border-bottom:1px solid var(--border-light);">—</td><td style="padding:10px;border-bottom:1px solid var(--border-light);">—</td><td style="padding:10px;border-bottom:1px solid var(--border-light);">—</td><td style="padding:10px;border-bottom:1px solid var(--border-light);">—</td><td style="padding:10px;border-bottom:1px solid var(--border-light);">—</td><td style="padding:10px;border-bottom:1px solid var(--border-light);font-weight:700;">—</td></tr>
          <tr><td style="padding:10px;border-bottom:1px solid var(--border-light);text-align:left;font-weight:600;">Kimi-k2</td><td style="padding:10px;border-bottom:1px solid var(--border-light);">—</td><td style="padding:10px;border-bottom:1px solid var(--border-light);">—</td><td style="padding:10px;border-bottom:1px solid var(--border-light);">—</td><td style="padding:10px;border-bottom:1px solid var(--border-light);">—</td><td style="padding:10px;border-bottom:1px solid var(--border-light);">—</td><td style="padding:10px;border-bottom:1px solid var(--border-light);font-weight:700;">—</td></tr>
          <tr><td style="padding:10px;text-align:left;font-weight:600;">Claude 4.7</td><td style="padding:10px;">—</td><td style="padding:10px;">—</td><td style="padding:10px;">—</td><td style="padding:10px;">—</td><td style="padding:10px;">—</td><td style="padding:10px;font-weight:700;">—</td></tr>
        </tbody>
      </table>
    </div>
    <p style="text-align:center;margin-top:16px;color:var(--text-400);font-size:0.78rem;">评分基于本次测试，仅供参考。模型持续更新，排名随时可能变化。</p>
  </div>
  <span class="page-num">39 / {total:02d}</span>
</section>''')

    # ===== Slide 40: Closing Quote =====
    sections.append(f'''
<section class="slide" id="s40" style="background:var(--bg);">
  <div class="slide-inner stagger" style="text-align:center;">
    <div class="quote-bar" style="text-align:left;max-width:700px;margin:0 auto;margin-bottom:32px;">
      <h2 style="font-size:clamp(1.5rem,3vw,2.2rem);line-height:1.5;">"横评有效期只有30天——<br>做你自己的那张表"</h2>
    </div>
    <div class="card" style="display:inline-block;padding:16px 32px;background:var(--bg-blue);">
      <p style="color:var(--blue-600);font-weight:600;font-size:0.9rem;">下节预告：国内Agent为什么突然从聊天框走向工作流？</p>
    </div>
  </div>
  <span class="page-num">40 / {total:02d}</span>
</section>''')

    # ===== Slide 41: The End =====
    sections.append(f'''
<section class="slide" id="s41" style="background:linear-gradient(135deg, #1E3A5F 0%, #0F172A 100%);">
  <div class="slide-inner stagger" style="text-align:center;">
    <h1 style="color:white;font-size:clamp(3rem,6vw,5rem);font-weight:800;letter-spacing:0.05em;">The End</h1>
    <p style="color:rgba(255,255,255,0.4);margin-top:16px;font-size:0.9rem;">C1 · Chapter 3 · 2026大模型擂台赛</p>
  </div>
  <div class="deco" style="width:250px;height:250px;background:rgba(59,130,246,0.15);top:-60px;left:-60px;"></div>
  <div class="deco" style="width:180px;height:180px;background:rgba(147,51,234,0.1);bottom:-30px;right:-30px;"></div>
  <span class="page-num" style="color:rgba(255,255,255,0.3);">41 / {total:02d}</span>
</section>''')

    # Assemble the full HTML
    nav_js = get_nav_js(total)

    html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>C1 · Chapter 3 · 2026大模型擂台赛</title>
<style>
{css}

  /* Extra styles for model response slides */
  .script-block h3 {{ margin: 14px 0 8px; font-size: 1.05rem; }}
  .script-block h4 {{ margin: 12px 0 6px; font-size: 0.95rem; }}
  .script-block h5 {{ margin: 10px 0 4px; font-size: 0.88rem; font-weight: 600; }}
  .script-block table {{ border-collapse: collapse; width: 100%; margin: 10px 0; }}
  .script-block td, .script-block th {{ padding: 6px 10px; border: 1px solid var(--border); font-size: 0.82rem; }}
  .script-block hr {{ border: none; border-top: 1px solid var(--border); margin: 12px 0; }}
  .script-block ul {{ margin: 6px 0; padding-left: 20px; }}
  .script-block li {{ margin: 3px 0; color: var(--text-700); font-size: 0.85rem; }}
  .script-block blockquote {{ border-left: 3px solid var(--blue-500); padding-left: 12px; margin: 8px 0; color: var(--text-700); font-style: italic; }}
  .script-block::-webkit-scrollbar {{ width: 4px; }}
  .script-block::-webkit-scrollbar-thumb {{ background: var(--border); border-radius: 2px; }}

  @media (max-width: 768px) {{
    .slide-inner {{ width: 95vw !important; }}
  }}
</style>
</head>
<body>

<nav class="slide-nav" id="slideNav"></nav>

{''.join(sections)}

{nav_js}
</body>
</html>'''

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"Generated index.html with {total} slides")

if __name__ == '__main__':
    generate_html()

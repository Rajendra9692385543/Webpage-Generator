from flask import Flask, request, render_template_string

app = Flask(__name__)

def parse_syllabus(raw_text):
    lines = raw_text.strip().splitlines()
    modules = []
    current_module = None
    section = None  # "theory" or "practicals"

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if line.lower().startswith("module"):
            if current_module:
                modules.append(current_module)
            current_module = {
                "title": line,
                "theory": [],
                "practicals": []
            }
            section = "theory"  # Default to theory even if not mentioned
        elif line.lower() == "theory":
            section = "theory"
        elif line.lower() in ["practice experiment", "practical experiment", "practicals"]:
            section = "practicals"
        elif section and current_module:
            current_module[section].append(line)

    if current_module:
        modules.append(current_module)

    return modules


@app.route('/')
def index():
    return open('index.html').read()

@app.route('/generate', methods=['POST'])
def generate():
    title = request.form['title']
    code_credit = request.form['code_credit']
    objectives_raw = request.form['objectives'].strip()
    outcomes_raw = request.form['outcomes'].strip()
    syllabus_raw = request.form['syllabus']
    modules = parse_syllabus(syllabus_raw)

    # Handle objectives & outcomes
    def convert_to_html(text):
        if '\n' in text:
            return "<ul>" + "".join(f"<li>{line.strip()}</li>" for line in text.splitlines() if line.strip()) + "</ul>"
        else:
            return f"<p>{text.strip()}</p>"

    objectives_html = convert_to_html(objectives_raw)
    outcomes_html = convert_to_html(outcomes_raw)

    with open("template.html") as f:
        template = f.read()

    html = template \
        .replace("{{title}}", title) \
        .replace("{{code_credit}}", code_credit) \
        .replace("{{objectives}}", objectives_html) \
        .replace("{{outcomes}}", outcomes_html)

    # Generate modules section
    module_html = ""
    for m in modules:
        module_html += '<div class="mb-3">'
        module_html += f'<div class="module-title">{m["title"]}</div>'
        if m["theory"]:
            module_html += '<h5>Theory</h5><ul>'
            for t in m["theory"]:
                module_html += f"<li>{t}</li>"
            module_html += '</ul>'
        if m["practicals"]:
            module_html += '<h5>Practice Experiment</h5><ul>'
            for p in m["practicals"]:
                module_html += f"<li>{p}</li>"
            module_html += '</ul>'
        module_html += '</div>'

    html = html.replace("{{modules}}", module_html)

    return render_template_string(html)

if __name__ == '__main__':
    app.run(debug=True)

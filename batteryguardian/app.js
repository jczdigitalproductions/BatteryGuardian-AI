'use strict';
const el = id => document.getElementById(id);
async function load(url, options) {
  el('message').textContent = 'Analyzing locally…';
  try {
    const response = await fetch(url, options);
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || 'Analysis failed');
    render(result);
    el('message').textContent = 'Completed locally. No telemetry uploaded to the internet.';
  } catch (error) { el('message').textContent = `Error: ${error.message}`; }
}
function render(data) {
  el('status').textContent = data.status;
  el('status').className = data.status;
  el('count').textContent = data.sample_count;
  el('alerts').textContent = data.event_count;
  el('temp').textContent = `${data.latest.temperature_c.toFixed(1)}°C`;
  el('explanation').textContent = data.explanation;
  el('method').textContent = data.method + (data.ml_advisory ? ` | Experimental PyTorch CPU advisory: score=${data.ml_advisory.probability.toFixed(3)}, threshold=${data.ml_advisory.threshold.toFixed(2)}; ${data.ml_advisory.explanation} (${data.ml_advisory.model_source})` : '') + (data.ml_advisory_error ? ` | Optional model unavailable: ${data.ml_advisory_error}` : '');
  const tbody = el('events'); tbody.replaceChildren();
  for (const event of data.events.slice().reverse()) {
    const tr = document.createElement('tr');
    for (const value of [event.index + 1, event.timestamp, event.severity, event.reasons.join(' ')]) {
      const td = document.createElement('td'); td.textContent = value; tr.appendChild(td);
    }
    tbody.appendChild(tr);
  }
  const svg = el('chart'); svg.replaceChildren();
  const vals = data.series.map(row => row.temperature_c);
  if (!vals.length) return;
  const low = Math.min(...vals, 0), high = Math.max(...vals, 65), range = Math.max(1, high - low);
  const points = vals.map((v,i) => `${30 + i * 740 / Math.max(1,vals.length-1)},${195 - (v-low)*170/range}`).join(' ');
  const polyline = document.createElementNS('http://www.w3.org/2000/svg','polyline');
  polyline.setAttribute('points',points); polyline.setAttribute('fill','none');
  polyline.setAttribute('stroke','#7bb6ff'); polyline.setAttribute('stroke-width','3'); svg.appendChild(polyline);
  for (const threshold of [45,60]) {
    if (threshold < low || threshold > high) continue;
    const y = 195 - (threshold-low)*170/range;
    const line = document.createElementNS('http://www.w3.org/2000/svg','line');
    for (const [key,value] of Object.entries({x1:30,x2:770,y1:y,y2:y,stroke:'#e9ad66','stroke-dasharray':'5 5'})) line.setAttribute(key,String(value));
    svg.appendChild(line);
  }
}
el('demo').addEventListener('click',() => load('/api/demo'));
el('file').addEventListener('change',async e => {
  const file = e.target.files[0]; if (!file) return;
  if (file.size > 2000000) {el('message').textContent='File too large';return;}
  load('/api/analyze',{method:'POST',headers:{'Content-Type':'text/csv'},body:await file.text()});
});

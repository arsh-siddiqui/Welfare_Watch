/* WelfareWatch Trend Charts v4 — Higher Score = Better Welfare */
var trendChart = null, stateChart = null;

function scoreColor(v){return v>=80?'#10B981':v>=60?'#3B82F6':v>=40?'#F59E0B':v>=20?'#F97316':'#EF4444'}
function scoreLabel(v){return v>=80?'🌟 Excellent':v>=60?'✅ Good':v>=40?'⚠️ Moderate':v>=20?'🔶 Weak':'🚨 Critical'}

function initTrendCharts(allYears){
  const slider=document.getElementById('yearSlider');
  const yrDisp=document.getElementById('yearDisplay');
  const yrEnd=document.getElementById('yearEnd');
  const stFilt=document.getElementById('stateFilter');
  if(!slider) return;

  function fillSlider(s){
    const pct=((+s.value-+s.min)/(+s.max-+s.min))*100;
    s.style.background=`linear-gradient(to right,var(--p) ${pct}%,var(--b) ${pct}%)`;
  }
  fillSlider(slider);

  function fetchRender(){
    const year=+slider.value, state=stFilt?stFilt.value:'';
    if(yrDisp) yrDisp.textContent=year;
    if(yrEnd)  yrEnd.textContent=year;
    fillSlider(slider);
    fetch('/api/trends?year='+year+(state?'&state='+encodeURIComponent(state):''))
      .then(r=>r.json()).then(data=>{renderTrend(data,allYears,year);renderBars(data);renderInsights(data);})
      .catch(e=>console.error('Trend API:',e));
  }

  function renderTrend(data, allYears, maxYear){
    const years=allYears.filter(y=>y<=maxYear);
    const td=data.yearly_trend||{};
    const labels=data.ind_labels||['Education','Healthcare','Food Security','Employment'];
    const overall=years.map(y=>(td[String(y)]||{}).avg||null);
    const i1=years.map(y=>(td[String(y)]||{}).i1||null);
    const i2=years.map(y=>(td[String(y)]||{}).i2||null);
    const i3=years.map(y=>(td[String(y)]||{}).i3||null);
    const i4=years.map(y=>(td[String(y)]||{}).i4||null);
    const datasets=[
      {label:'Overall Welfare Score',data:overall,borderColor:'#2563EB',backgroundColor:'rgba(37,99,235,.08)',fill:true,tension:.4,borderWidth:3.5,pointRadius:6,pointBackgroundColor:'#2563EB',pointBorderColor:'#fff',pointBorderWidth:2.5,spanGaps:true},
      {label:labels[0],data:i1,borderColor:'#14B8A6',fill:false,tension:.4,borderWidth:2,pointRadius:4,borderDash:[5,3],spanGaps:true},
      {label:labels[1],data:i2,borderColor:'#8B5CF6',fill:false,tension:.4,borderWidth:2,pointRadius:4,borderDash:[5,3],spanGaps:true},
      {label:labels[2],data:i3,borderColor:'#F59E0B',fill:false,tension:.4,borderWidth:2,pointRadius:4,borderDash:[5,3],spanGaps:true},
      {label:labels[3],data:i4,borderColor:'#EC4899',fill:false,tension:.4,borderWidth:2,pointRadius:4,borderDash:[5,3],spanGaps:true},
    ];
    const opts={responsive:true,maintainAspectRatio:false,
      interaction:{mode:'index',intersect:false},
      plugins:{
        legend:{position:'bottom',labels:{font:{family:'Inter',size:12},padding:14,usePointStyle:true,pointStyleWidth:8}},
        tooltip:{backgroundColor:'rgba(255,255,255,.97)',titleColor:'#0A1628',bodyColor:'#475569',borderColor:'#E2E8F0',borderWidth:1,padding:12,
          callbacks:{label:ctx=>{const v=ctx.raw;if(v===null)return null;return ctx.dataset.label+': '+v.toFixed(1)+'/100  '+scoreLabel(v)}}}
      },
      scales:{
        x:{grid:{color:'rgba(226,232,240,.6)'},ticks:{font:{family:'Inter',size:12}}},
        y:{min:0,max:100,grid:{color:'rgba(226,232,240,.6)'},
          ticks:{font:{family:'Inter',size:12},callback:v=>v===0?'0 (Critical)':v===100?'100 (Excellent)':v}}
      },animation:{duration:600}
    };
    const ctx=document.getElementById('trendLineChart');
    if(!ctx) return;
    if(trendChart){trendChart.data.labels=years;trendChart.data.datasets=datasets;trendChart.update('active');}
    else trendChart=new Chart(ctx,{type:'line',data:{labels:years,datasets},options:opts});
  }

  function renderBars(data){
    const sd=data.state_data||{};
    const entries=Object.entries(sd).sort((a,b)=>b[1]-a[1]).slice(0,15);
    const states=entries.map(e=>e[0]),scores=entries.map(e=>e[1]),colors=scores.map(scoreColor);
    const opts={indexAxis:'y',responsive:true,maintainAspectRatio:false,
      plugins:{legend:{display:false},
        tooltip:{backgroundColor:'rgba(255,255,255,.97)',titleColor:'#0A1628',bodyColor:'#475569',borderColor:'#E2E8F0',borderWidth:1,padding:10,
          callbacks:{label:ctx=>' '+ctx.raw.toFixed(1)+'/100  '+scoreLabel(ctx.raw)}}},
      scales:{x:{min:0,max:100,grid:{color:'rgba(226,232,240,.6)'},ticks:{font:{family:'Inter',size:11},callback:v=>v+'/100'}},
        y:{grid:{display:false},ticks:{font:{family:'Inter',size:11}}}},animation:{duration:600}};
    const ctx=document.getElementById('stateBarChart');
    if(!ctx) return;
    if(stateChart){stateChart.data.labels=states;stateChart.data.datasets[0].data=scores;stateChart.data.datasets[0].backgroundColor=colors;stateChart.update('active');}
    else stateChart=new Chart(ctx,{type:'bar',data:{labels:states,datasets:[{data:scores,backgroundColor:colors,borderRadius:6,borderSkipped:false}]},options:opts});
  }

  function renderInsights(data){
    const ins=data.insights, panel=document.getElementById('insightsPanel');
    if(!panel||!ins||!ins.trend) return;
    const arrow=ins.trend==='improving'?'📈':ins.trend==='declining'?'📉':'➡️';
    const trendColor=ins.trend==='improving'?'#10B981':ins.trend==='declining'?'#EF4444':'#94A3B8';
    const trendMsg=ins.trend==='improving'
      ?`<span style="color:#10B981;font-weight:700">${arrow} Welfare is improving</span> — score rose by ${ins.pct_change}%`
      :ins.trend==='declining'
      ?`<span style="color:#EF4444;font-weight:700">${arrow} Welfare is declining</span> — score fell by ${ins.pct_change}%`
      :`<span style="color:#94A3B8;font-weight:700">➡️ Stable</span> — no significant change`;
    panel.innerHTML=`
      <div style="background:var(--surf);border:1px solid var(--b);border-radius:var(--rad);padding:16px 20px;margin-bottom:18px">
        <div style="font-size:13px;font-weight:700;color:var(--th);margin-bottom:12px">📊 Trend Summary</div>
        <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:12px">
          <div style="padding:12px;background:var(--g-l);border-radius:var(--rads);text-align:center;border:1px solid #6EE7B7">
            <div style="font-size:11px;font-weight:700;color:#065F46;text-transform:uppercase;margin-bottom:4px">Best Year</div>
            <div style="font-family:var(--fontd);font-size:22px;font-weight:800;color:#065F46">${ins.best_year}</div>
            <div style="font-size:12px;color:#065F46">Score: ${ins.best_score}/100</div>
          </div>
          <div style="padding:12px;background:var(--r-l);border-radius:var(--rads);text-align:center;border:1px solid #FCA5A5">
            <div style="font-size:11px;font-weight:700;color:#991B1B;text-transform:uppercase;margin-bottom:4px">Weakest Year</div>
            <div style="font-family:var(--fontd);font-size:22px;font-weight:800;color:#991B1B">${ins.worst_year}</div>
            <div style="font-size:12px;color:#991B1B">Score: ${ins.worst_score}/100</div>
          </div>
          <div style="padding:12px;background:var(--p-l);border-radius:var(--rads);text-align:center;border:1px solid #93C5FD">
            <div style="font-size:11px;font-weight:700;color:#1E40AF;text-transform:uppercase;margin-bottom:4px">Change</div>
            <div style="font-family:var(--fontd);font-size:22px;font-weight:800;color:${ins.change>0?'#10B981':'#EF4444'}">${ins.change>0?'+':''}${ins.change}</div>
            <div style="font-size:12px;color:#1E40AF">points</div>
          </div>
          <div style="padding:12px;background:var(--surf2);border-radius:var(--rads);text-align:center;border:1px solid var(--b)">
            <div style="font-size:11px;font-weight:700;color:var(--ts);text-transform:uppercase;margin-bottom:4px">Trend</div>
            <div style="font-size:24px;margin-bottom:2px">${arrow}</div>
            <div style="font-size:12px;font-weight:600;color:${trendColor};text-transform:capitalize">${ins.trend}</div>
          </div>
        </div>
        <div style="padding:10px 14px;background:var(--surf2);border-radius:var(--rads);font-size:13px;color:var(--tb)">${trendMsg}</div>
      </div>`;
  }

  let debounce;
  slider.addEventListener('input',()=>{clearTimeout(debounce);if(yrDisp)yrDisp.textContent=slider.value;fillSlider(slider);debounce=setTimeout(fetchRender,250);});
  stFilt&&stFilt.addEventListener('change',fetchRender);
  fetchRender();
}

/* ── Mobile: reduce chart point radius and tick density on small screens ── */
if (typeof Chart !== 'undefined') {
  Chart.defaults.responsive = true;
  Chart.defaults.maintainAspectRatio = false;

  // Reduce visual weight on mobile
  if (window.innerWidth <= 768) {
    Chart.defaults.elements.point.radius = 3;
    Chart.defaults.elements.point.hoverRadius = 5;
    Chart.defaults.font.size = 10;
    Chart.defaults.plugins.legend.labels.font = { size: 11 };
  }
}

/* ── Trend summary grid responsive ── */
document.addEventListener('DOMContentLoaded', function() {
  function adaptInsightGrid() {
    const panel = document.getElementById('insightsPanel');
    if (!panel) return;
    const grid = panel.querySelector('[style*="grid-template-columns:repeat(4,1fr)"]');
    if (grid && window.innerWidth <= 600) {
      grid.style.gridTemplateColumns = 'repeat(2,1fr)';
    }
  }
  adaptInsightGrid();
  window.addEventListener('resize', adaptInsightGrid);
});

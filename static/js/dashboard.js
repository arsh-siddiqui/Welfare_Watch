document.addEventListener('DOMContentLoaded',function(){
  // Flash auto-dismiss
  setTimeout(()=>document.querySelectorAll('.flash').forEach(el=>{
    el.style.transition='opacity .4s,transform .4s';
    el.style.opacity='0';el.style.transform='translateX(20px)';
    setTimeout(()=>el.remove(),400);
  }),5500);

  // Count-up animation
  document.querySelectorAll('.kpi-val,.strip-v').forEach(el=>{
    const raw=parseInt(el.textContent.replace(/\D/g,''),10);
    if(!isNaN(raw)&&raw>1){
      let c=0;const inc=Math.max(1,Math.ceil(raw/60));
      const t=setInterval(()=>{c=Math.min(c+inc,raw);el.textContent=c.toLocaleString('en-IN');if(c>=raw)clearInterval(t);},18);
    }
  });

  // ── Sidebar toggle ───────────────────────────────────────────────────────
  const sidebar  = document.getElementById('sidebar');
  const mainArea = document.getElementById('mainArea');
  const toggle   = document.getElementById('sidebarToggle');
  const overlay  = document.getElementById('sbOverlay');

  function isMobile(){ return window.innerWidth <= 768; }

  function openMobileSidebar(){
    sidebar?.classList.add('open');
    overlay?.classList.add('on');
    document.body.style.overflow = 'hidden';
  }
  function closeMobileSidebar(){
    sidebar?.classList.remove('open');
    overlay?.classList.remove('on');
    document.body.style.overflow = '';
  }
  function toggleDesktopSidebar(){
    const collapsed = sidebar?.classList.toggle('collapsed');
    if(mainArea) mainArea.style.marginLeft = collapsed ? '64px' : '';
  }

  overlay?.addEventListener('click', closeMobileSidebar);
  document.getElementById('sidebarClose')?.addEventListener('click', closeMobileSidebar);

  document.querySelectorAll('.sb-item').forEach(item=>{
    item.addEventListener('click',()=>{ if(isMobile()) closeMobileSidebar(); });
  });

  toggle?.addEventListener('click',()=>{
    if(isMobile()){ sidebar?.classList.contains('open') ? closeMobileSidebar() : openMobileSidebar(); }
    else { toggleDesktopSidebar(); }
  });

  // Swipe left to close sidebar
  let touchStartX = 0;
  sidebar?.addEventListener('touchstart', e=>{ touchStartX = e.touches[0].clientX; },{passive:true});
  sidebar?.addEventListener('touchend', e=>{
    if(e.changedTouches[0].clientX - touchStartX < -60 && isMobile()) closeMobileSidebar();
  },{passive:true});
  // Swipe from left edge to open
  let edgeStartX = 0;
  document.addEventListener('touchstart', e=>{ edgeStartX = e.touches[0].clientX; },{passive:true});
  document.addEventListener('touchend', e=>{
    if(edgeStartX < 24 && e.changedTouches[0].clientX - edgeStartX > 60 && isMobile()) openMobileSidebar();
  },{passive:true});

  document.addEventListener('keydown', e=>{ if(e.key==='Escape') closeMobileSidebar(); });
  window.addEventListener('resize', ()=>{ if(!isMobile()){ closeMobileSidebar(); document.body.style.overflow=''; }});

  // Slider fill
  document.querySelectorAll('input[type=range]').forEach(s=>{
    const fill=()=>{const pct=((+s.value-+s.min)/(+s.max-+s.min))*100;s.style.background=`linear-gradient(to right,var(--p) ${pct}%,var(--b) ${pct}%)`};
    fill();s.addEventListener('input',fill);
  });

  // Card entrance animations
  const obs=new IntersectionObserver(entries=>{
    entries.forEach((e,i)=>{if(e.isIntersecting){setTimeout(()=>{e.target.style.opacity='1';e.target.style.transform='none';},i*55);obs.unobserve(e.target);}});
  },{threshold:.05});
  document.querySelectorAll('.card,.kpi-card,.feat-card,.ds-card,.rpt-card,.role-card').forEach(el=>{
    el.style.opacity='0';el.style.transform='translateY(14px)';
    el.style.transition='opacity .42s ease,transform .42s ease,box-shadow .2s ease';
    obs.observe(el);
  });

  // Button ripple
  document.querySelectorAll('.btn-p,.btn-g,.hbtn-p').forEach(btn=>{
    btn.style.position='relative';btn.style.overflow='hidden';
    btn.addEventListener('click',e=>{
      const r=btn.getBoundingClientRect(),sz=Math.max(r.width,r.height);
      const s=document.createElement('span');
      s.style.cssText=`position:absolute;width:${sz}px;height:${sz}px;left:${e.clientX-r.left-sz/2}px;top:${e.clientY-r.top-sz/2}px;background:rgba(255,255,255,.25);border-radius:50%;transform:scale(0);animation:rpl .5s ease;pointer-events:none`;
      btn.appendChild(s);setTimeout(()=>s.remove(),500);
    });
  });
  if(!document.getElementById('rplSt')){const s=document.createElement('style');s.id='rplSt';s.textContent='@keyframes rpl{to{transform:scale(2.5);opacity:0}}';document.head.appendChild(s);}

  // Chart.js resize on window resize
  let resizeTimer;
  window.addEventListener('resize', ()=>{
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(()=>{
      if(typeof Chart !== 'undefined' && Chart.instances){
        Object.values(Chart.instances).forEach(chart=>{ try{ chart.resize(); }catch(e){} });
      }
    }, 300);
  });
});

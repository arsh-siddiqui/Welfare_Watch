(function(){
  const root=document.documentElement;
  const saved=localStorage.getItem('ww-theme')||'light';
  root.setAttribute('data-theme',saved);
  document.addEventListener('DOMContentLoaded',function(){
    const btn=document.getElementById('themeBtn'),ico=document.getElementById('themeIco');
    function apply(t){root.setAttribute('data-theme',t);localStorage.setItem('ww-theme',t);if(ico)ico.className=t==='dark'?'fa fa-sun':'fa fa-moon';}
    apply(saved);
    btn?.addEventListener('click',()=>apply(root.getAttribute('data-theme')==='dark'?'light':'dark'));
  });
})();

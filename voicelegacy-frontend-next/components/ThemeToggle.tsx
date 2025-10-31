'use client';
import { useEffect, useState } from 'react';

export default function ThemeToggle(){
  const [mode, setMode] = useState<'dark'|'light'>(() => (typeof window!=='undefined' && localStorage.getItem('theme')==='light')?'light':'dark');
  useEffect(()=>{
    if(mode==='light'){
      document.body.classList.add('bg-white','text-black');
    }else{
      document.body.classList.remove('bg-white','text-black');
    }
    localStorage.setItem('theme', mode);
  }, [mode]);
  return (
    <button className="btn-secondary" onClick={()=>setMode(m=>m==='dark'?'light':'dark')}>
      {mode==='dark' ? '☀️ Light' : '🌙 Dark'}
    </button>
  );
}

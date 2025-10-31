'use client';
import { useEffect, useState } from 'react';

type Toast = { id: number; message: string; type?: 'info'|'success'|'error' };

let pushFn: (t: Omit<Toast, 'id'>) => void;

export function pushToast(t: Omit<Toast,'id'>){ if(pushFn) pushFn(t); }

export default function Toaster(){
  const [items, setItems] = useState<Toast[]>([]);
  useEffect(()=>{ pushFn = (t) => {
    const id = Date.now()+Math.random();
    setItems(prev => [...prev, { id, ...t }]);
    setTimeout(()=> setItems(prev => prev.filter(x=>x.id!==id)), 3500);
  }; },[]);
  return (
    <div className="fixed top-4 right-4 z-50 space-y-2">
      {items.map(t => (
        <div key={t.id} className={
          "px-4 py-2 rounded-lg shadow-lg text-sm " +
          (t.type==='error'?'bg-red-600/90': t.type==='success'?'bg-emerald-600/90':'bg-black/70')
        }>
          {t.message}
        </div>
      ))}
    </div>
  );
}

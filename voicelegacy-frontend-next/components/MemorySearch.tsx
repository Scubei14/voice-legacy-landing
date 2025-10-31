'use client';
import { useState } from 'react';
import { http } from '@/lib/api';

export default function MemorySearch(){
  const [q, setQ] = useState('');
  const [res, setRes] = useState<any[]>([]);
  const [pinned, setPinned] = useState<any[]>([]);

  async function search(e: React.FormEvent){ e.preventDefault();
    if(!q.trim()) return setRes([]);
    try{ const { data } = await http.post('/api/memories/search', { query: q, top_k: 5 }); setRes(data.results || []); }
    catch{ /* ignore */ }
  }

  function pin(item:any){ if(pinned.find((x)=>x.text===item.text)) return; setPinned([...pinned, item]); }
  function unpin(i:number){ setPinned(pinned.filter((_,idx)=> idx!==i)); }

  return (
    <div className="space-y-3">
      <form onSubmit={search} className="flex gap-2">
        <input className="input" value={q} onChange={e=>setQ(e.target.value)} placeholder="e.g. fishing trip 2004" />
        <button className="btn">Search</button>
      </form>
      <div className="space-y-2">
        {res?.length ? res.map((r:any, i:number)=>(
          <div key={i} className="p-2 rounded-lg bg-white/5 border border-white/10">
            <div className="text-[10px] opacity-60 mb-1">score {r.score?.toFixed?.(3) ?? "—"}</div>
            <div className="text-sm">{r.text}</div>
            <button className="btn-secondary mt-2" onClick={()=>pin(r)}>Pin for context</button>
          </div>
        )) : <div className="opacity-60 text-sm">No results.</div>}
      </div>
      {pinned.length>0 && (
        <div className="mt-3">
          <div className="text-xs opacity-70 mb-1">Pinned (client-side):</div>
          <ul className="space-y-1">
            {pinned.map((p:any, i:number)=>(
              <li key={i} className="text-xs bg-white/5 border border-white/10 rounded p-2 flex items-center justify-between gap-2">
                <span className="truncate">{p.text}</span>
                <button className="badge" onClick={()=>unpin(i)}>remove</button>
              </li>
            ))}
          </ul>
          <div className="text-[10px] opacity-50 mt-1">These pinned snippets are a visual aid. The backend already retrieves memories automatically (RAG). </div>
        </div>
      )}
    </div>
  );
}

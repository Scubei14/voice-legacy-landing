'use client';
import { useEffect, useState } from 'react';
import { http } from '@/lib/api';
import { pushToast } from '@/components/Toaster';

type Memory = { id:number, text:string, tags?:string, created_at:string };

export default function MemoriesPage(){
  const [items, setItems] = useState<Memory[]>([]);
  const [text, setText] = useState('');
  const [search, setSearch] = useState('');
  const [results, setResults] = useState<any[]>([]);

  async function load(){
    // No list endpoint in spec; simulate by searching with empty query -> better: show recent via analytics? We'll accept user to search.
    setItems([]);
  }
  async function createMemory(e: React.FormEvent){
    e.preventDefault();
    try{
      const { data } = await http.post('/api/memories/', { text, tags: '' });
      pushToast({ message: 'Memory saved', type:'success' });
      setText(''); setItems([data, ...items]);
    }catch(e:any){ pushToast({ message: e?.response?.data?.detail || 'Failed to save', type:'error' }); }
  }
  async function runSearch(e?: React.FormEvent){
    if(e) e.preventDefault();
    if(!search.trim()) return setResults([]);
    try{
      const { data } = await http.post('/api/memories/search', { query: search, top_k: 10 });
      setResults(data.results || []);
    }catch(e:any){ pushToast({ message: 'Search failed', type:'error' }); }
  }

  useEffect(()=>{ load(); },[]);

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-semibold">Memories</h1>
      <section className="grid md:grid-cols-2 gap-6">
        <div className="card">
          <h2 className="font-semibold mb-3">Add Memory</h2>
          <form onSubmit={createMemory} className="space-y-3">
            <textarea className="input h-40" placeholder="Write a memory..." value={text} onChange={e=>setText(e.target.value)} />
            <button className="btn">Save</button>
          </form>
        </div>
        <div className="card">
          <h2 className="font-semibold mb-3">Search</h2>
          <form onSubmit={runSearch} className="flex gap-2">
            <input className="input" value={search} onChange={e=>setSearch(e.target.value)} placeholder="e.g. ocean vacation"/>
            <button className="btn">Search</button>
          </form>
          <div className="mt-4 space-y-2 max-h-[50vh] overflow-auto">
            {results?.length? results.map((r:any, i:number)=>(
              <div key={i} className="p-3 rounded-lg bg-white/5 border border-white/10">
                <div className="text-sm opacity-60 mb-1">score: {r.score?.toFixed?.(3) ?? "—"}</div>
                <div className="text-sm leading-relaxed">{r.text}</div>
              </div>
            )): <div className="opacity-60 text-sm">No results yet.</div>}
          </div>
        </div>
      </section>
    </div>
  );
}

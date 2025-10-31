'use client';
import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { http } from '@/lib/api';
import { pushToast } from '@/components/Toaster';

export default function PersonaDetail(){
  const { id } = useParams<{id:string}>(); const r = useRouter();
  const [p, setP] = useState<any>(null);
  const [files, setFiles] = useState<FileList | null>(null);
  const [info, setInfo] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  async function load(){
    try{
      const { data } = await http.get(`/api/personas/${id}`); setP(data);
      const vi = await http.get(`/api/voice_training/personas/${id}/voice-info`).catch(()=>({ data:null })); setInfo(vi.data);
    }catch(e:any){ pushToast({ message: e?.response?.data?.detail || 'Failed to load persona', type:'error' }); r.push('/dashboard'); }
  }
  useEffect(()=>{ load(); }, [id]);

  async function train(e: React.FormEvent){
    e.preventDefault(); if(!files || files.length===0) return pushToast({ message: 'Select audio files first', type:'error' });
    const fd = new FormData(); Array.from(files).forEach((f)=> fd.append('files', f));
    setLoading(true);
    try{
      const { data } = await http.post(`/api/voice_training/personas/${id}/train`, fd, { headers: { 'Content-Type': 'multipart/form-data' } });
      pushToast({ message: data.message || 'Training started', type:'success' });
      load();
    }catch(e:any){ pushToast({ message: e?.response?.data?.detail || 'Training failed', type:'error' }); }
    finally{ setLoading(false); }
  }

  if(!p) return <div className="opacity-60">Loading...</div>;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-semibold">{p.name}</h1>
        <a className="btn" href={`/talk/${p.id}`}>Talk</a>
      </div>

      <section className="grid md:grid-cols-2 gap-6">
        <div className="card">
          <h2 className="font-semibold mb-2">Persona</h2>
          <div className="text-sm opacity-80">Provider: {p.voice_provider}</div>
          <div className="text-sm opacity-80">Voice ID: {p.voice_id || '—'}</div>
          <div className="mt-2 text-sm">
            <pre className="bg-black/30 border border-white/10 rounded-md p-3 overflow-auto text-xs">
              {JSON.stringify(p.traits, null, 2)}
            </pre>
          </div>
        </div>

        <div className="card">
          <h2 className="font-semibold mb-2">Train Custom Voice</h2>
          <div className="text-xs opacity-70 mb-2">Upload 1–25 audio files (clean speech). Total &lt; 100MB.</div>
          <form onSubmit={train} className="space-y-3">
            <input type="file" multiple accept="audio/*,video/*" onChange={e=>setFiles(e.target.files)} />
            <button className="btn" disabled={loading}>{loading? 'Uploading...' : 'Start Training'}</button>
          </form>
          <div className="mt-3 text-sm opacity-80">
            {info ? (info.has_custom_voice ? <>Custom voice active: <span className="badge">{info.voice_id}</span></> : info.message) : '—'}
          </div>
        </div>
      </section>
    </div>
  );
}

"use client"
import React, { useEffect, useState, useRef } from "react";
import { useUploads } from "../context/upload_context";
import { apiRequest } from '@/lib/api-client';

type MediaMap = Record<string, { url?: string; loading: boolean; error?: string }>

const UploadList: React.FC = () => {
  const { uploads } = useUploads();
  const [mediaMap, setMediaMap] = useState<MediaMap>({});
  const createdBlobs = useRef<string[]>([]);

  useEffect(() => {
    // cleanup blob URLs on unmount
    return () => {
      createdBlobs.current.forEach((b) => URL.revokeObjectURL(b));
      createdBlobs.current = [];
    };
  }, []);

  useEffect(() => {
    // fetch media serving path for each upload that we don't already have
    uploads.forEach((u) => {
      const key = u.task_id;
      if (mediaMap[key]?.loading || mediaMap[key]?.url) return;

      setMediaMap((m) => ({ ...m, [key]: { loading: true } }));

      (async () => {
        try {
          const res = await apiRequest(`/media/${encodeURIComponent(u.video_path)}`);

          const finalUrl = res.url;
          setMediaMap((m) => ({ ...m, [key]: { url: finalUrl, loading: false } }));
        } catch (err: any) {
          setMediaMap((m) => ({ ...m, [key]: { loading: false, error: String(err) } }));
        }
      })();
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [uploads]);

  if (!uploads.length) {
    return <div className="text-sm text-slate-400">No uploads yet.</div>;
  }

  return (
    <div className="space-y-3">
      <h3 className="text-sm font-semibold">Uploaded</h3>
      <ul className="space-y-2">
        {uploads.map((u, idx) => {
          const entry = mediaMap[u.task_id];
          return (
            <li key={u.task_id + idx} className="flex items-center">
              <div className=" bg-black/5 rounded overflow-hidden flex items-center justify-center">
                {/* {entry?.loading && <div className="text-xs text-slate-500">Loading…</div>}
                {entry?.error && <div className="text-xs text-red-500">Error</div>} */}
                {entry?.url && (
                  <video src={entry.url} className="w-full h-full" controls={true} />
                )}
                {/* {!entry && <div className="text-xs text-slate-400">Queued</div>} */}
              </div>
             
            </li>
          );
        })}
      </ul>
    </div>
  );
};

export default UploadList;

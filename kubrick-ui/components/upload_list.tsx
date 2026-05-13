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
      const key = u.id;
      if (!u.video_path) return;
      if (mediaMap[key]?.loading || mediaMap[key]?.url) return;

      setMediaMap((m) => ({ ...m, [key]: { loading: true } }));

      (async () => {
        try {
          const fileName = (u.video_path as string).split('/').pop();
          const res = await apiRequest(`/video/media/${encodeURIComponent(fileName as string)}`);

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
    return <div className="text-sm text-gray-400 mt-4 text-center">No uploads yet.</div>;
  }

  return (
    <div className="space-y-4 mt-6">
      <h3 className="text-sm font-semibold text-gray-200">Recent Uploads</h3>
      <ul className="space-y-3">
        {uploads.map((u) => {
          const entry = mediaMap[u.id];
          return (
            <li key={u.id} className="flex flex-col bg-white/5 border border-white/10 rounded-lg p-3">
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm text-gray-300 truncate max-w-[150px]">{u.fileName}</span>
                <span className="text-xs font-medium px-2 py-1 rounded bg-white/10 text-gray-300 capitalize">
                  {u.status}
                </span>
              </div>
              
              {u.status === 'uploading' && (
                <div className="w-full bg-gray-700 rounded-full h-1.5 mb-1 overflow-hidden">
                  <div className="bg-indigo-500 h-1.5 rounded-full w-full animate-pulse"></div>
                </div>
              )}
              
              {u.status === 'processing' && (
                <div className="w-full bg-gray-700 rounded-full h-1.5 mb-1 overflow-hidden">
                  <div className="bg-yellow-500 h-1.5 rounded-full w-full animate-pulse"></div>
                </div>
              )}

              {u.status === 'error' && (
                <div className="text-xs text-red-400 mt-1">
                  {u.error || 'Upload failed'}
                </div>
              )}

              {u.status === 'completed' && (
                <div className="mt-2 bg-black/20 rounded overflow-hidden flex items-center justify-center">
                  {entry?.url ? (
                    <video src={entry.url} className="w-full h-auto max-h-[150px] object-cover" controls={true} />
                  ) : (
                    <div className="text-xs text-gray-400 p-4">Loading preview...</div>
                  )}
                </div>
              )}
            </li>
          );
        })}
      </ul>
    </div>
  );
};

export default UploadList;

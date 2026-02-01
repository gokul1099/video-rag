"use client"
import VideoUploader from "@/components/upload_video";
import Image from "next/image";
import { UploadProvider, useUploads } from "@/components/upload_context";
import UploadList from "@/components/upload_list";

function Main() {
  const { addUpload } = useUploads();

  return (
    <div className="bg-white min-h-screen">
<button data-drawer-target="default-sidebar" data-drawer-toggle="default-sidebar" aria-controls="default-sidebar" type="button" className="text-heading bg-transparent box-border border border-transparent hover:bg-neutral-secondary-medium focus:ring-4 focus:ring-neutral-tertiary font-medium leading-5 rounded-base ms-3 mt-3 text-sm p-2 focus:outline-none inline-flex sm:hidden">
   <span className="sr-only">Open sidebar</span>
   <svg className="w-6 h-6" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24">
  <path stroke="currentColor" stroke-linecap="round" stroke-width="2" d="M5 7h14M5 12h14M5 17h10"/>
   </svg>
</button>

  <aside id="default-sidebar" className="fixed top-0 left-0 z-40 w-64 h-full transition-transform -translate-x-full sm:translate-x-0" aria-label="Sidebar">
    <div className="h-full px-3 py-4 overflow-y-auto bg-transparent border-e border-default">
    <VideoUploader onUploadSuccess={(resp) => addUpload(resp)} />
    <div className="mt-6">
      <UploadList />
    </div>
   </div>
</aside>
<div className="p-4 sm:ml-64">
    <div className=""> 
      {}
    </div>
    <div className="pb-28">{/* reserve space for fixed bottom bar */}</div>
</div>

{/* Fixed bottom input bar */}
<div className="fixed bottom-0 left-0 right-0 sm:left-64 bg-transparent border-t px-4 py-3">
  <div className="max-w-5xl mx-auto flex items-center gap-3">
    <label htmlFor="visitors" className="sr-only">Message</label>
    <input
      type="text"
      id="visitors"
      placeholder="Type a message..."
      className="bg-neutral-secondary-medium border text-black border-default-medium text-heading text-base rounded-base focus:ring-brand focus:border-brand flex-1 px-4 py-3.5 shadow-xs placeholder:text-body"
      required
    />
    <button type="button" className="bg-sky-600 hover:bg-sky-700 text-white rounded-base px-4 py-2">
      Send
    </button>
  </div>
</div>
    </div>
  );
}

export default function Home() {
  return (
    <UploadProvider>
      <Main />
    </UploadProvider>
  );
}

import React, { useRef, useEffect } from "react";

export const AvatarVideo = ({ videoUrl, imageUrl, status }) => {
  const videoRef = useRef(null);

  useEffect(() => {
    if (videoUrl && videoRef.current) {
      videoRef.current.load();
      videoRef.current.play().catch(e => console.error("Autoplay prevented:", e));
    }
  }, [videoUrl]);

  return (
    <div className="relative w-full max-w-2xl mx-auto aspect-video bg-black rounded-lg overflow-hidden border border-[#333333] shadow-2xl">
      {videoUrl ? (
        <video
          ref={videoRef}
          className="w-full h-full object-cover"
          controls
          autoPlay
          playsInline
        >
          <source src={videoUrl} type="video/mp4" />
          Your browser does not support the video tag.
        </video>
      ) : imageUrl ? (
        <img
          src={imageUrl}
          alt="Avatar Avatar"
          className="w-full h-full object-cover"
        />
      ) : (
        <div className="flex items-center justify-center w-full h-full text-gray-500">
          No Avatar Selected
        </div>
      )}

      {status && status !== "done" && status !== "pending" && (
        <div className="absolute inset-0 bg-black/60 flex flex-col items-center justify-center backdrop-blur-sm">
          <div className="w-8 h-8 border-2 border-white border-t-transparent rounded-full animate-spin mb-4" />
          <p className="text-white font-medium uppercase tracking-widest text-sm">
            {status}...
          </p>
        </div>
      )}
    </div>
  );
};

import React from "react";

export const Loader = ({ className = "", size = "md" }) => {
  const sizes = {
    sm: "w-4 h-4 border-2",
    md: "w-8 h-8 border-2",
    lg: "w-12 h-12 border-4",
  };

  return (
    <div className={`flex items-center justify-center ${className}`}>
      <div
        className={`${sizes[size]} border-white border-t-transparent rounded-full animate-spin`}
      />
    </div>
  );
};

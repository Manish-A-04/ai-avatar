import React, { forwardRef } from "react";

export const Input = forwardRef(({ className = "", error, label, ...props }, ref) => {
  return (
    <div className="w-full space-y-1">
      {label && <label className="block text-sm font-medium text-gray-300">{label}</label>}
      <input
        ref={ref}
        className={`w-full px-4 py-2 bg-[#1a1a1a] border ${
          error ? "border-red-500" : "border-[#333333]"
        } rounded-sm text-white placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-white focus:border-white transition-colors duration-200 ${className}`}
        {...props}
      />
      {error && <p className="text-sm text-red-400 mt-1">{error}</p>}
    </div>
  );
});

Input.displayName = "Input";

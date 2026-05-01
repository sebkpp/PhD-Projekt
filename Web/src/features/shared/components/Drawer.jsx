import React from "react";

export default function Drawer({ open, onClose, children, width = "w-96" }) {
    if (!open) return null;
    return (
        <div className="fixed inset-0 z-50 flex">
            <div
                className="flex-1 bg-black bg-opacity-30"
                onClick={onClose}
            />
            <div className={`h-full bg-white dark:bg-gray-800 shadow-lg p-6 ${width} animate-slideInRight`}>
                {children}
            </div>
        </div>
    );
}
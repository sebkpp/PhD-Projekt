import React from "react";

export default function PlaceholderChart({ label }) {
    return (
        <div className="border border-dashed border-gray-600 rounded-xl p-6 text-center text-gray-500 my-4">
            <div className="text-sm">{label}</div>
        </div>
    );
}

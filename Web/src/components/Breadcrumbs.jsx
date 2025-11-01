import { Link } from "react-router-dom";

export default function Breadcrumbs({ items, styled = false, className = "" }) {
    return (
        <nav aria-label="breadcrumb" className={`${styled
            ? "bg-gray-800/80 backdrop-blur-sm rounded-lg px-4 shadow-md h-10 flex items-center"
            : ""} ${className}`}>
            <ol className="flex items-center space-x-1">
                {items.map((item, idx) => (
                    <li key={idx} className="flex items-center">
                        {item.to ? (
                            <Link
                                to={item.to}
                                className="text-blue-400 hover:text-blue-200 px-2 py-1 rounded-md transition-colors duration-200
                           hover:bg-gray-700/50 hover:underline underline-offset-4"
                            >
                                {item.label}
                            </Link>
                        ) : (
                            <span className="text-gray-100 font-semibold px-2 py-1">
                {item.label}
              </span>
                        )}
                        {idx < items.length - 1 && (
                            <span className="mx-1 text-gray-500 select-none">›</span>
                        )}
                    </li>
                ))}
            </ol>
        </nav>
    );
}
import { toPng } from "html-to-image";

export function useChartExport() {
    return async function exportChart(chartRef, buttonRef, filename) {
        if (chartRef && buttonRef) {
            chartRef.classList.add("export-light");
            buttonRef.style.display = "none";
            try {
                const dataUrl = await toPng(chartRef);
                chartRef.classList.remove("export-light");
                buttonRef.style.display = "block";
                const link = document.createElement("a");
                link.download = filename;
                link.href = dataUrl;
                link.click();
            } catch (err) {
                chartRef.classList.remove("export-light");
                buttonRef.style.display = "block";
                console.error("Export fehlgeschlagen:", err);
            }
        }
    };
}
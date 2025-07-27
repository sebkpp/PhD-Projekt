import React from 'react';

const Testsite = () => {
    return (

        <div className="p-lg">
            <h1 className="text-3xl font-bold mb-md">Test Page</h1>
            <div className="bg-background text-foreground p-lg border border-[--color-border] rounded-[--border-radius-md] mb-md">
                <p>This is a test paragraph with custom background and foreground colors.</p>
            </div>
            <button className="bg-[--color-accent] text-[--color-background] px-spacing-md py-spacing-sm rounded-[--border-radius-md] border border-[--color-border]">
                Test Button
            </button>
            <div className="bg-[--color-danger] text-[--color-foreground] p-spacing-md mt-md rounded-[--border-radius-md]">
                <p>This is a test alert with danger color.</p>
            </div>
        </div>
    );
};

export default Testsite;
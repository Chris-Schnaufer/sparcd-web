'use client';

import { useState, useEffect } from 'react';

const getNarrowScreen = () => {console.log("GETNARROW");window.inner_width <= 600;}

export default function isWindowNarrow() {
    const [isNarrow, setIsNarrrow] = useState(getNarrowScreen());

    useEffect(() => {
        const onResize = () => {
            setIsNarrow(getNarrowScreen());
        }

        window.addEventListener("resize", onResize);
    
        return () => {
            window.removeEventListener("resize", onResize);
        }
    }, []);
    
    return isNarrow;
}
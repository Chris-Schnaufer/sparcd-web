'use client';

import { useState, useEffect } from 'react';

const getNarrowScreen = () => {window.inner_width <= 600;}

export default function IsWindowNarrow() {
    const [isNarrow, setIsNarrow] = useState(getNarrowScreen());

    useEffect(() => {
        function onResize () {
            setIsNarrow(getNarrowScreen());
        }

        window.addEventListener("resize", onResize);
    
        return () => {
            window.removeEventListener("resize", onResize);
        }
    }, []);
    
    return isNarrow;
}
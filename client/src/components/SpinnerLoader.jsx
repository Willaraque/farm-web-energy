import React from 'react';
import { useEffect, useState } from "react";
import spinnerImage from '../assets/Spinner.gif';

function SpinnerLoader() {
    const [text, setText] = useState('')
    const [showImg, setShowImg] = useState(true)

    useEffect(() => {
        const timer = setTimeout(() => {
            setShowImg(false);
            setText('I waited for 6 seconds to be loaded');
        }, 6000);

        return () => clearTimeout(timer); // Limpia el timeout si el componente se desmonta

    }, [])
    return (
        <>
            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
                {
                    showImg ? (
                        <img src={spinnerImage} alt="Loading spinner" style={{ width: '150px', height: '150px' }} />
                    ) : (
                        <div style={{ fontSize: '24px', fontWeight: 'bold' }}>{text}</div>)
                }
            </div>
        </>
    )
}

export default SpinnerLoader

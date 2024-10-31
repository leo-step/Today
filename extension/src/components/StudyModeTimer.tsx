import React, { useState } from "react";

const CountdownTimer = () => {
    const initialTime = 60 * 60; // Initial time in seconds (1 hour)
    const [timeRemaining, setTimeRemaining] = useState(initialTime);
    const [startedTimer, setStartedTimer] = useState(false);
    const [timerIntervalId, setTimerIntervalId] = useState<NodeJS.Timeout | null>(null);

    // Convert seconds to hours, minutes, and seconds
    const hours = Math.floor(timeRemaining / 3600);
    const minutes = Math.floor((timeRemaining % 3600) / 60);
    const seconds = timeRemaining % 60;

    const onClickReset = () => {
        setTimeRemaining(initialTime);
        setStartedTimer(false);
        if (timerIntervalId) {
            clearInterval(timerIntervalId);
            setTimerIntervalId(null);
        }
    };

    const onStart = () => {
        if (!startedTimer) {
            setStartedTimer(true);
            const intervalId = setInterval(() => {
                setTimeRemaining((prevTime) => {
                    if (prevTime === 0) {
                        clearInterval(intervalId);
                        console.log("Countdown complete!");
                        return 0;
                    } else {
                        return prevTime - 1;
                    }
                });
            }, 1000);
            setTimerIntervalId(intervalId);
        }
    };

    const onStop = () => {
        if (timerIntervalId) {
            clearInterval(timerIntervalId);
            setTimerIntervalId(null);
            setStartedTimer(false);
        }
    };

    return (
        <div style={{zIndex:2}}>
            <div style={{fontSize:"150px", color:"white", fontFamily:"Oswald"}}>{`${hours}h ${minutes}m ${seconds}s`}</div>
            <div style={{width:"100hv", display:"flex", justifyContent:"space-between"}}>
                <button style={{alignSelf:"right", width:"125px", height:"75px", margin:"15px", fontSize:"40px", color:"white", fontFamily:"Oswald", backgroundColor:"#ffc067", borderRadius:"50px", borderColor:"orange"}}
                onClick={onClickReset}>Reset</button>
                <button style={{width:"125px", height:"75px", margin:"15px", fontSize:"40px", color:"white", fontFamily:"Oswald", backgroundColor:"#ffc067", borderRadius:"50px", borderColor:"orange"}}
                onClick={onStart}>Start</button>
                <button style={{width:"125px", height:"75px", margin:"15px", fontSize:"40px", color:"white", fontFamily:"Oswald", backgroundColor:"#ffc067", borderRadius:"50px", borderColor:"orange"}}
                onClick={onStop}>Stop</button>
            </div>  
            
        </div>
    );
};

export default CountdownTimer;

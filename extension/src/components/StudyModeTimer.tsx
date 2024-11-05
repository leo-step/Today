import React, { useState } from "react";

const CountdownTimer = () => {
    const initialTime = 60 * 40; // Initial time in seconds (1 hour)
    const [timeRemaining, setTimeRemaining] = useState(initialTime);
    const [startedTimer, setStartedTimer] = useState(false);
    const [timerIntervalId, setTimerIntervalId] = useState<NodeJS.Timeout | null>(null);

    // Convert seconds to hours, minutes, and seconds
    const hours = Math.floor(timeRemaining / 3600) < 10 ? "0" + Math.floor(timeRemaining / 3600) : Math.floor(timeRemaining / 3600);
    const minutes = (Math.floor((timeRemaining % 3600) / 60) < 10)? ("0" + Math.floor((timeRemaining % 3600) / 60)) : Math.floor((timeRemaining % 3600) / 60);
    const seconds = timeRemaining % 60 < 10 ? "0" + timeRemaining % 60 : timeRemaining % 60; 

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
        <div style={{zIndex:2, width:"700px", alignItems:"center"}}>
            <div style={{ fontSize: "175px", color: "white", fontFamily:"Lekton", fontWeight:"700", display: "flex"}}>
                <span style={{width: "200px", textAlign: "center"}}>{hours}</span>
                <span>:</span>
                <span style={{ width: "200px", textAlign: "center" }}>{minutes}</span>
                <span>:</span>
                <span style={{ width: "200px", textAlign: "center" }}>{seconds}</span>
            </div>
            <div style={{width:"500px", display:"flex", justifyContent:"center", justifySelf:"center"}}>
                <button style={{width:"125px", height:"75px", margin:"15px", fontSize:"40px", color:"white", fontFamily:"Oswald", backgroundColor:"#ffc067", borderRadius:"50px", borderColor:"orange"}}
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

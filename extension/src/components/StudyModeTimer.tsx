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
        <div>
            <p>Countdown Timer:</p>
            <p>{`${hours}h ${minutes}m ${seconds}s`}</p>
            <button onClick={onClickReset}>Reset</button>
            <button onClick={onStart}>Start</button>
            <button onClick={onStop}>Stop</button>
        </div>
    );
};

export default CountdownTimer;

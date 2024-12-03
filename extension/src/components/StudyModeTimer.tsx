import React, { useRef, useState, useEffect } from "react";
import { useAtomValue } from "jotai";
import { timerState } from "./study_mode_state";

const CountdownTimer = () => {
    const timerValue = useAtomValue(timerState); // Get the initial time from the atom
    const [timeRemaining, setTimeRemaining] = useState(timerValue); // Local state for time remaining
    const [startedTimer, setStartedTimer] = useState(false);
    const [timerIntervalId, setTimerIntervalId] = useState<NodeJS.Timeout | null>(null);

    const audioRef = useRef<HTMLAudioElement | null>(null);

    // Sync `timeRemaining` with `timerValue` only when the atom value changes
    useEffect(() => {
        if (!startedTimer && timerIntervalId === null) {
            setTimeRemaining(timerValue);
        }
    }, [timerValue]);

    const onClickReset = () => {
        if (timerIntervalId) {
            clearInterval(timerIntervalId);
            setTimerIntervalId(null);
        }
        setStartedTimer(false);
        setTimeRemaining(timerValue); // Reset to the initial atom value
    };

    const onStart = () => {
        if (!startedTimer) {
            setStartedTimer(true); // Start the timer
            const intervalId = setInterval(() => {
                setTimeRemaining((prevTime) => {
                    if (prevTime === 0) {
                        clearInterval(intervalId);
                        setTimerIntervalId(null);
                        if (audioRef.current) {
                            audioRef.current.play(); // Play sound when timer ends
                        }
                        return 0;
                    }
                    return prevTime - 1; // Decrement time
                });
            }, 1000);
            setTimerIntervalId(intervalId); // Save interval ID
        }
    };

    const onStop = () => {
        if (timerIntervalId) {
            clearInterval(timerIntervalId); // Stop the countdown
            setTimerIntervalId(null);
        }
        setStartedTimer(false); // Pause the timer without resetting
    };

    // Convert seconds to hours, minutes, and seconds
    const hours = Math.floor(timeRemaining / 3600)
        .toString()
        .padStart(2, "0");
    const minutes = Math.floor((timeRemaining % 3600) / 60)
        .toString()
        .padStart(2, "0");
    const seconds = (timeRemaining % 60).toString().padStart(2, "0");

    return (
        <div style={{ zIndex: 2, width: "700px", alignItems: "center" }}>
            <div
                style={{
                    fontSize: "175px",
                    color: "white",
                    fontFamily: "Lekton",
                    fontWeight: "700",
                    display: "flex",
                }}
            >
                <span style={{ width: "200px", textAlign: "center" }}>{hours}</span>
                <span>:</span>
                <span style={{ width: "200px", textAlign: "center" }}>{minutes}</span>
                <span>:</span>
                <span style={{ width: "200px", textAlign: "center" }}>{seconds}</span>
            </div>
            <div
                style={{
                    width: "500px",
                    display: "flex",
                    justifyContent: "center",
                    justifySelf: "center",
                }}
            >
                <button
                    style={buttonStyle}
                    onClick={onClickReset}
                >
                    Reset
                </button>
                <button
                    style={buttonStyle}
                    onClick={onStart}
                >
                    Start
                </button>
                <button
                    style={buttonStyle}
                    onClick={onStop}
                >
                    Stop
                </button>
            </div>
            <audio ref={audioRef} src="/timer_ring.mp3" preload="auto" />
        </div>
    );
};

const buttonStyle: React.CSSProperties = {
    width: "125px",
    height: "75px",
    margin: "15px",
    fontSize: "40px",
    color: "white",
    fontFamily: "Oswald",
    backgroundColor: "#ffc067",
    borderRadius: "50px",
    borderColor: "orange",
};

export default CountdownTimer;
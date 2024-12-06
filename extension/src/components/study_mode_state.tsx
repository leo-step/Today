import { atom } from "jotai";
const study_mode_state = () => {

}
export const timerState = atom(30);
export const deadlineState = atom(new Date());
export const timerReset = atom(false);
export default study_mode_state;
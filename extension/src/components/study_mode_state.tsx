import { atom } from "jotai";
const study_mode_state = () => {

}
export const timerState = atom(25);
export const deadlineState = atom(new Date());

export default study_mode_state;
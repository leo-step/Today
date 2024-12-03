import { atom } from "jotai";
const study_mode_state = () => {

}
export const timerState = atom(30*60);
export const deadlineState = atom(new Date());

export default study_mode_state;
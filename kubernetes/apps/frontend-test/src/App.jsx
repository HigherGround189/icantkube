import { useReducer } from "react";

function reducer(state, action) {
    switch (action) {
        case "inc": return state + 1;
        case "dec": return state - 1;
        default: return state;
    }
}

export default function Component() {
    const [state, dispatch] = useReducer(reducer, 0);

    return (
        <>
        <p>Count = {state}</p>

        <button onClick={() => dispatch("inc")}>+1</button>
        <button onClick={() => dispatch("dec")}>-1</button>
        </>
    )
}
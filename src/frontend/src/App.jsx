import { useReducer } from "react";
// import { useQuery } from "@tanstack/react-query";

function changeCount(count, action) {
    switch (action.type) {
        case "inc": return { value: count.value + 1};
        case "dec": return { value: count.value - 1 };
        default: return count;
    }
}

export default function App() {
    const [count, dispatch] = useReducer(changeCount, { value: 0 })

    return (
        <>
        <div>Count: {count.value}</div>
        <button onClick={() => dispatch({ type: "inc" })}>+1</button>
        <button onClick={() => dispatch({ type: "dec" })}>-1</button>
        </>
    )
}
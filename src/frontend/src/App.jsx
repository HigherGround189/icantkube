import { useReducer, useState } from "react";

function changeCount(count, action) {
    switch (action.type) {
        case "inc":
            return { value: count.value + 1 };
        case "dec":
            return { value: count.value - 1 };
        default:
            return count;
    }
}

export default function App() {
    const [count, dispatch] = useReducer(changeCount, { value: 0 });
    const [message, setMessage] = useState("");

    async function queryBackend() {
        const res = await fetch(`http://backend.backend.svc.cluster.local/api/${count.value}`);
        const data = await res.json();
        setMessage(data.message);
    }

    return (
        <>
            <div>Count: {count.value}</div>

            <button onClick={() => dispatch({ type: "inc" })}>+1</button>
            <button onClick={() => dispatch({ type: "dec" })}>-1</button>

            <hr />

            <button onClick={queryBackend}>Query backend</button>
            <div>{message}</div>
        </>
    );
}

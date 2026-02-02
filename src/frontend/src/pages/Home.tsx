import { useQuery } from "@tanstack/react-query"
import MachinesLoading from "../components/MachinesLoading"

export default function Home() {
    async function fetchMachines() {
        const res = await fetch("/api/sample-echo-microservice/1")
        if (!res.ok) throw new Error('Failed to fetch')
        return res.json()
    }

    const { data, isLoading, isError, error } = useQuery({
        queryKey: ['machines'],
        queryFn: fetchMachines
    })

    if (isLoading) return <MachinesLoading />
    if (isError) return <div>{(error as Error).message}</div>

    return (
        <>
            {data}
        </>
    )
}
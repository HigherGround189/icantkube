import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import "./App.css";
import App from "./App";

const queryClient = new QueryClient({
    defaultOptions: {
        queries: {
            staleTime: 3000,
            retry: 1,
            refetchOnWindowFocus: false,
        },
    },
});

const root = createRoot(document.getElementById("root")!);
root.render(
    <StrictMode>
        <QueryClientProvider client={queryClient}>
            <App />
        </QueryClientProvider>
    </StrictMode>
);

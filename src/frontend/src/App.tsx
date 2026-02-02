import { Tabs, TabsList, TabsTrigger, TabsContent } from "./components/ui/tabs"
import Home from "./pages/Home"

export default function App() {


    return (
        <>
            <Tabs defaultValue="home" className="w-full">
                <TabsList>
                    <TabsTrigger value="home">Home</TabsTrigger>
                </TabsList>
                <TabsContent value="home">
                    <Home />
                </TabsContent>
            </Tabs>
        </>
    )
}
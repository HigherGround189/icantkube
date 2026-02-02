import { Item, ItemContent, ItemMedia, ItemTitle } from "./ui/item"
import { Spinner } from "./ui/spinner"

export default function MachinesLoading() {
    return (
        <>
            <Item variant="muted">
                <ItemMedia>
                    <Spinner />
                </ItemMedia>
                <ItemContent>
                    <ItemTitle className="line-clamp-1">Loading machines...</ItemTitle>
                </ItemContent>
            </Item>
        </>
    )
}
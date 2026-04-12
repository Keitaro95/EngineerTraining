import {
    QueryClient,
    QueryClientProvider,
    useQuery,
} from '@tanstack/react-query'


function Example() {
    const { isPending, error, data } = useQuery({
        queryKey: ['repoData'],
        queryFn: () =>
            fetch('https://api.github.com/repos/TanStack/query').then((res) => res.json(),
            ),
    })
    if (isPending) return 'Loading...'

    if (error) return 'An error has occurred: ' + error.message

    return (
        <div>
            <h1>{data.name}</h1>
            <p>{data.description}</p>
        </div>
    )
}


https://tanstack.com/query/latest/docs/framework/react/guides/query-options
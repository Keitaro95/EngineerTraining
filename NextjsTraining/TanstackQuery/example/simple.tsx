
function Todos() {
    const { isPending, isError, data, error } = useQuery({
        queryKey: ['todos'],
        queryFn: fetchTodoList,
    })

    if (isPending) {
        return <span>Loading...</span>
    }
    if (isError) {
        return <span>Error: {error.message}</span>
    }

    return (
        <ul>
            {data.map((todo) => (
                <li key={todo.id}>{todo.title}</li>
            ))}
        </ul>
    )
}
import { 
    useQuery,
    useMutation,
    useQueryClient,
    QueryClient,
    QueryClientProvider } from '@tanstack/react-query';
import {getTodos, postTodo } from '../api';

const queryClient = new QueryClient();

function App() {
    return (
        <QueryClientProvider client={queryClient}>
            <Todos />
        </QueryClientProvider>
    );
}


function Todos() {
    const queryClient = useQueryClient();

    const query = useQuery({
        queryKey: ['todos'],
        queryFn: getTodos,
    });

    const mutation = useMutation({
        mutationFn: postTodo,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['todos'] });
        },
    })

    return (
        <div>
            <ul>
                {query.data?.map((todo) => (
                    <li key={todo.id}>{todo.text}</li>
                ))}
            </ul>

            <button
                onClick={() => {
                    mutation.mutate({
                        id: Date.now(),
                        title: 'New Todo',
                    })
                }}
            >
                Add Todo
            </button>
        </div>
    )
}

render(<App />, document.getElementById('root'));
export default function BlogLayout({ children, }: { children:React.ReactNode }) {
    return <div>
                <section>{children}</section>
                <p>this section is shown by app/blog/[slug]/layout.tsx</p>    
            </div>
}

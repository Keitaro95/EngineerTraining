


npm installすると
Coding Agent用の docsも入るよ

node_modules/next/dist/docs/
├── 01-app/
│   ├── 01-getting-started/
│   ├── 02-guides/
│   └── 03-api-reference/
├── 02-pages/
├── 03-architecture/
└── index.mdx


npx create-next-app@canary
これで 
AGENT.mdができるよ

```sh
<!-- BEGIN:nextjs-agent-rules -->
 
# Next.js: ALWAYS read docs before coding
 
Before any Next.js work, find and read the relevant doc in `node_modules/next/dist/docs/`. Your training data is outdated — the docs are the source of truth.
 
<!-- END:nextjs-agent-rules -->
```



npx create-next-app@canary --no-agents-md
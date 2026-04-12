## Frontend ディレクトリ構成（Next.js App Router）

Page.tsx：UI表現の最終層。これがクライアントで表示される
```tsx
import { dehydrate, HydrationBoundary, QueryClient } from '@tanstack/react-query';
import { getUsers } from '@/user/api/user.generated';
import { UserListView } from '@/user/components/UserListView';

export default async function UsersPage() {
  const queryClient = new QueryClient();

  // 1. サーバーサイドでAPIを叩いてキャッシュを作る
  await queryClient.prefetchQuery({
    queryKey: ['getUsers'],
    queryFn: getUsers,
  });

  return (
    <main className="p-8">
      <h1 className="text-2xl font-bold mb-6">ユーザー管理</h1>
      
      {/* 2. キャッシュをクライアントコンポーネントへ渡す */}
      <HydrationBoundary state={dehydrate(queryClient)}>
        <UserListView />
      </HydrationBoundary>
    </main>
  );
}
```
↑

* features/user/components/ (UI表現層)：クライアントに表示：TanStack Queryを知らない。 React hookとして使うだけ。
hooks/useUserList.ts からデータを受け取り、JSXで表示するだけです。
「どうやってデータを取ってくるか」「どう整形するか」は一切知りません。
Page.tsxで使われます。
```tsx
'use client';

import { useUserList } from '../hooks/useUserList';

export const UserListView = () => {
  const { users, isLoading, isError } = useUserList();

  if (isLoading) return <div>読み込み中...</div>;
  if (isError) return <div>エラーが発生しました</div>;

  return (
    <ul className="space-y-2">
      {users.map((user) => (
        <li key={user.id} className="p-3 border rounded flex justify-between">
          <span>{user.fullName}</span>
          {user.isAdmin && (
            <span className="bg-red-100 text-red-600 px-2 py-1 text-xs rounded">
              管理者
            </span>
          )}
        </li>
      ))}
    </ul>
  );
};
```
↑
* features/user/hooks/ (BFF / ビジネスロジック層)：機能別のロジック：TanStack Queryの実践場所
「BFF layer」 の実体です。
features/user/api/ のフックを呼び出し、UIが表示しやすい形に filter や map をかけます。
「AというAPIとBというAPIの結果を合体させる」といったロジックもここに書きます。
UI（components）は、この hooks 層だけを見るようにします。
```tsx
'use client';

import { useGetUsers, User } from '../api/user.generated';

// UIが必要な形に変換された型
export interface FormattedUser extends User {
  fullName: string;
  isAdmin: boolean;
}

export const useUserList = () => {
  // Orvalのフックを呼び出し、selectオプションでデータを整形
  const { data, isLoading, error } = useGetUsers({
    select: (users) => 
      users.map((user) => ({
        ...user,
        fullName: `${user.lastName} ${user.firstName}`,
        isAdmin: user.role === 'admin',
      })),
  });

  return {
    users: data ?? [],
    isLoading,
    isError: !!error,
  };
};
```
↑

* features/user/api/ (自動生成の置き場)　：Orvalが管理する。「TanStack Queryの原材料」
Orvalが生成したファイルをそのまま置きます。
ここにある useGetUsers などのフックは、バックエンドのインターフェース（OpenAPI）をそのまま TypeScript に投影しただけの「生のデータ取得機能」です。原則、ここには手動でロジックを書き込みません。（再生成で消えてしまうため）
```tsx
// ※ Orvalが生成したと想定
import { useQuery, UseQueryOptions } from '@tanstack/react-query';

// 生の型定義
export interface User {
  id: string;
  firstName: string;
  lastName: string;
  role: 'admin' | 'user';
}

// 生のAPIリクエスト関数（サーバーサイドのprefetchでも利用する）
export const getUsers = async (): Promise<User[]> => {
  const res = await fetch('/api/users');
  return res.json();
};

// Orvalが生成するTanStack Query Hook
export const useGetUsers = <TData = User[]>(
  options?: UseQueryOptions<User[], Error, TData>
) => {
  return useQuery<User[], Error, TData>({
    queryKey: ['getUsers'],
    queryFn: getUsers,
    ...options,
  });
};
```
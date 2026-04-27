



type MyReadonly<T> = {
    readonly [key in keyof T]: T[key]
  }
// TypeScriptが面白いのが、型の定義を、あたかもこのオブジェクトのループ動作を型定義でしてるところ。
// [key in keyof T]は
// 任意のオブジェクトTに対して
// Tのkeyをループして、keyを展開
// : T[key]でループするkey一つ一つに対して、オブジェクトTの[key]プロパティを渡して展開してる
  







// 2-1-1
// 引数に型注釈（アノテーション）・戻り値に型注釈
function expo2(amount: number): number {
    return amount ** 2
}

// 基本の型指定
let flag: boolean = false;
let decimal: number = 256;
let color: string = "white";

let list: number[] = [1, 2, 3];
let list2: Array<number> = [1, 2, 3];

let x: [string, number];

//  any, unknown　は省略

function logger(message: string): void {
    console.log(message);
}
// null とundefinedは省略

//　戻り値を得られないため戻り型はnever
function infiniteLoop(): never {
    while (true) {     
    }
}

// 交差タイプ
type Kimera = Dog & Bird

// Union Types この型または...
let value: boolean | number | string;
let numberOrString: (number | string)[];

// Literal Types 強く型を制限する
let users: 'Taro' | 'Hanako' | 'Jiro';
users = '';

// typeofで型を抽出
let myObject = { foo: 'foo' }
let anotherObject: typeof myObject = { foo: '' }
anotherObject['foo'] = 'anystring'

//keyof
type SomeType = {
    foo: string
    bar: string
    baz: string
}
type Point = { x: number; y: number };
type P = keyof Point;  // ⇒ "x" | "y"
// keyof Point は Point 型のキー（ここでは "x" および "y"）を列挙した 文字列リテラルのユニオン型になります



// 2-4-4
const indexedObject = {
    0: 0,
    1: 1
}
// キーワードもタイプも同じじゃないとダメだよ
let indexedKey: keyof typeof indexedObject
indexedKey = 1
indexedKey = 2 


// 2-5-2 アサーション（宣言）
// ここでany型を使うけど
let someValue: any = "This is a string";
// 使うときstrに固定する
// let strLength: number = (<string>somevalue).length;
let strLength: number = (someValue as string).length;


// 2-6-1 class
class Creature {
    numberOfHands: number
    numberOfFeet: number
    constructor(numberOfHands: number, numberOfFeet: number) {
        this.numberOfHands = numberOfHands
        this.numberOfFeet = numberOfFeet
    }
}
const creature = new Creature(0, 4)

// 3-2-5
const t3 = [false, 1, '2'] as [boolean, number, string]

// 3-3-4
const obj = {
    foo: false as false,
    bar: 1 as 1,
    baz: '2' as '2',
}
obj['foo'] = true

// 3-7-2
sample.jsonから型を抽出できる




/// 4-1-3 関数でnullableな値を扱う
// 引数にnullが入っても安全に利用できる！！
function getFormatterdValue1(value: number | null) {
    if (value === null) return '--pt'
    return `${value.toFixed(1)} pt`
}

// 4-1-8 関数の引数をオプションにする「?」
function greet(name?: string) {
    if (name === undefined) return 'Hello!'
    return `Hello ${name.toUpperCase()}`
}

/// 4-1-12　デフォルト引数とアノテーション
function getFormatterdValue2(value: number, unit: string | null = null) {
    const _value = value.toFixed(1)
    if (unit === null) return `${_value} pt`
    return `${_value} ${unit.toUpperCase()}`
}


// 4-1-18 readonlyは読み込み専用
type State = {
    readonly id: number
    name: string
}

// 4-1-19
type State = {
    id: number
    name: string
}
const state: Readonly<State> = {
    id: 1,
    name: 'Taro'
}


// 4-2-3 ダウンキャスト：asでアサーションすることで、型をより厳格に固定する！！
const defaultTheme = {
    backgroundColor: "orange" as "orange",
    bordercolor: "red" as "red"
}


// 4-2-8 
// インデックスシグネチャ
// 任意の型を持つプロパティを追加できる
type User = {
    name: string
    [k: string]: number | string
}
const userA: User = {
    name: 'Taro',
    age: 26
}
const x = userA.name
const y = userA.age

//4-2-3
const tuple2 = [false, 1, '2'] as const

// 4-3-1
function reset(value: number | string | boolean) {
    const v0 = value
    if (typeof value === 'number') {
        const v1 = value
        return 0
    }
    const v2 = value
    if (typeof value === 'string') {
        const v3 = value
        return ''
    }
    const v4 = value
    return false
}



// 4-3-6
type User_typeguards = { gender: string; [k: string]: any }
type UserA = User_typeguards & { name:string }
type UserB = User_typeguards & { age:number }
function isUserA(user: UserA | UserB): user is UserA {
    return user.name !== undefined
}
function isUserB(user: UserA | UserB): user is UserB {
    return user.age !== undefined
}


// 宣言空間：メモリ上で宣言空間ごとに確保している範囲が異なる
const value1 = 'test' // value


// interface 以下の二つは結合される　overload
interface UserC {
    name: string
}
interface UserC {
    age:number
}

// Namespace 型定義をexportする
namespace TestA {
    export interface Properties {
        name: string
    }
}
// 名前空間が保有する型に新しい型を付与
const Properties: TestA.Properties = {
    name: 'Taro'
}


// 高度な型 
// Genericsを使うと、型の決定を遅延できます
interface Box<T> {
    value: T
}
// または
interface Box<T = string> {
    value: T
}
// または
interface Box<T extends string | number> {
    value: T
}
const box1: Box<string> = { value: 'test' }


function boxed<T>(props: T) {
    return { value:props }
}


// conditional types
type IsString<T> = T extends string ? true : false
type X = IsString<'test'> 
type Y = IsString<0>




// React Hooksの型

// useState
import { use, useState } from 'react';
const [count, setCount] = useState(0) // 0が入っているので数値型
const [count1, setCount1] = useState<number | null>(0)

// useRef
import { useRef, useEffect } from 'react';

const ExampleuseRef = () => {
    const ref = useRef<null | HTMLDivElement>(null);
    useEffect(() => {
        if (ref.current === null) return
        const size = ref.current.getBoundingClientRect()
        console.log(size)
        })
        return (
            <div>
                <div ref={ref} style={{ width: 100, height:100 }}></div>
            </div>
        )
    }
// useReducer
// 状態の型
interface AppState {
    counter: number;
    random: number;
  }
  
  // アクションごとの型定義（Discriminated Union）
  type IncrementAction = { type: 'increment'; payload: number };
  type RandomAction = { type: 'random' };
  type AppAction = IncrementAction | RandomAction;
  
  // reducer本体
  function appReducer(state: AppState, action: AppAction): AppState {
    switch (action.type) {
      case 'increment':
        return { ...state, counter: state.counter + action.payload };
      case 'random':
        return { ...state, random: Math.random() };
      default:
        return state; // safety for exhaustive checks
    }
  }
  
  // フックの使用例
  const [state, dispatch] = useReducer(appReducer, { counter: 0, random: 0 });
  
  // dispatch の例
  dispatch({ type: 'increment', payload: 10 });
  dispatch({ type: 'random' });
  


// Strategy：共通インターフェース 
// 重さを入力に入れて numberを返す というのは共通
type ShippingStrategy = (weightKg: number) => number;

// 具体的なアルゴリズム定義
const standard: ShippingStrategy = (w) => 500 + w * 100;
const express: ShippingStrategy = (w) => 1200 + w * 200;
const free: ShippingStrategy = (w) => 0;

// 利用する
const shippingCost = ( strategy: ShippingStrategy, weightKg: number) => {
    return strategy(weightKg)
}
console.log(shippingCost(express, 3))

// interface ShippingStrategy {
//     calculate(weightKg: number): number;
// }

// class StandardShipping implements ShippingStrategy {
//     calculate(weightKg: number): number {
//         return 500 + weightKg * 100;
//     }
// }

// class ExpressShipping implements ShippingStrategy {
//     calculate(weightKg: number): number {
//         return 500 + weightKg * 100;
//     }
// }

// class FreeShippting implements ShippingStrategy {
//     calculate(weightKg: number): number {
//         return 0;
//     }
// }

// // Context
// class Order {
//     constructor (
//         private weightKg: number,
//         private shipping: ShippingStrategy,
//     ) {}

//     setShipping(shipping: ShippingStrategy): void {
//         this.shipping = shipping;
//     }
//     shippingCost(): number {
//         return this.shipping.calculate(this.weightKg)
//     }
// }

// // 利用例
// const order = new Order(3, new StandardShipping());
// console.log(order.shippingCost()); // 800

// order.setShipping(new ExpressShipping());
// console.log(order.shippingCost()); // 1800
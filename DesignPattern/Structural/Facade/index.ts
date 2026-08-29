
// ファサード：簡潔な統一インターフェース：窓
// Client ──▶ Facade ──▶ SubsystemA
//                   ├──▶ SubsystemB
//                   └──▶ SubsystemC


// それぞれのサービスの動作を提供する
class InventoryService {
    reserve(sku: string, qty: number): boolean {
        console.log(`在庫確保: ${sku} x${qty}`);
        return true;
    }
    release(sku: string, qty: number): void {
        console.log(`在庫解放: ${sku} x${qty}`);
    }
}

class PaymentGateway {
    charge(customerId: string, amount: number): string {
        console.log(`決済: ${customerId} に ${amount}円`);
        return `txn_${Date.now()}`;
    }
}

class ShippingService {
    schedule(customerId: string, sku: string): string {
        console.log(`配送手段: ${sku} に ${customerId}`);
        return `ship_${Date.now()}`;
    }
}

class NotificationService {
    sendConfirmation(customerId: string, orderId: string): void {
        console.log(`確認メール送信: ${customerId} (注文 ${orderId})`);
    }
}

// ファサード
interface OrderRequest {
    customerId: string;
    sku: string;
    qty: number;
    unitPrice: number;
}

// オーダー用のファサード
class OrderFacade {
    constructor(
        private inventory = new InventoryService(),
        private payment = new PaymentGateway(),
        private shipping = new ShippingService(),
        private notifier = new NotificationService(),
    ) {}

    placeOrder(req: OrderRequest): string {
        if (!this.inventory.reserve(req.sku, req.qty)) {
            throw new Error("在庫不足");
        }
        try {
            const txnId = this.payment.charge(req.customerId, req.unitPrice * req.qty);
            const shipId = this.shipping.schedule(req.customerId, req.sku);
            const orderId = `${txnId}/${shipId}`;
            this.notifier.sendConfirmation(req.customerId, orderId);
            return orderId;
        } catch (e) {
            this.inventory.release(req.sku, req.qty);
            throw e;
        }
    }
}

// クライアントはplaceOrderを1回呼ぶだけ
// 呼び出し順序・エラー時の補償・4つのサービスの存在は全て Facade に隠蔽されています。
const facade = new OrderFacade();
const orderId = facade.placeOrder({
        customerId: "user_42",
        sku: "BOOK-GOF",
        qty: 1,
        unitPrice: 5280,
    });
console.log("注文完了:", orderId);
    
